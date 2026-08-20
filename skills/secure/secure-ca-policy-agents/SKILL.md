---
name: secure-ca-policy-agents
version: "1.0"
pillar: secure
subdomain: ms-entra
description: >-
  Creates and validates Conditional Access policies specific to AI agent
  identities using clientApplications.includeAgentIdServicePrincipals,
  avoiding the critical misconfiguration of grantControls mfa being invalid
  for agents.
tags: [secure, entra, conditional-access, workload-identity, least-privilege, mfa-trap]
atlas_techniques: [AML.T0012, AML.T0040]
d3fend_techniques: [D3-MAN, D3-UAP]
nist_ai_rmf: [GOVERN-2.1, MANAGE-2.4]
nist_csf: [PR.AA-05, PR.AC-04]
ms_license: [Microsoft Entra ID P1, Entra Workload ID Premium]
ms_roles: [Conditional Access Administrator, Security Administrator]
effort_hours: 3
---

## When to use

- When registering any agent with Entra Agent ID — the CA policy comes immediately after
- When agents are found with access unrestricted by CA (output of `govern-ca-policy-workload-identity`)
- To migrate from inherited user policies to agent-specific policies
- As a prerequisite before enabling any agent in production

## Prerequisites

- Entra ID P1 minimum (Workload ID Premium for risk conditions)
- Conditional Access Administrator role
- Agents registered with Entra Agent ID (see `govern-entra-agent-id`)
- Access to Entra ID → Security → Conditional Access

## The critical trap: `grantControls: mfa`

```json
// ❌ WRONG — do not use for agents
{
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["mfa"]
  }
}

// ✅ CORRECT — explicit block for at-risk agents
{
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["block"]
  }
}
```

`grantControls: mfa` is **silently invalid** for agent identities — agents cannot complete interactive MFA. The policy appears active but enforces nothing.

## Workflow

### Step 1 — Create the Blueprint-level CA policy

```json
POST https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies
Content-Type: application/json

{
  "displayName": "Agentic AI — Risk-Based Access Control",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "clientApplications": {
      "includeServicePrincipals": [],
      "excludeServicePrincipals": [],
      "includeAgentIdServicePrincipals": "All"
    },
    "signInRiskLevels": ["high", "medium"]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["block"]
  }
}
```

### Step 2 — Validate with the What If tool

1. Entra ID → Security → Conditional Access → **What If**
2. Configure:
   - User: `None (service principal)`
   - Cloud app: select the agent's SP
   - Sign-in risk: `Medium`
3. Run it — confirm the policy shows as **Applied** with action **Block**
4. Repeat with a human user account — confirm the policy does **NOT** apply

### Step 3 — Validate that `grantControls: mfa` does not apply

1. Create a second test policy with `"builtInControls": ["mfa"]`
2. Run What If with the agent's SP
3. Confirm the policy shows as **Not applied** or generates no enforcement
4. **Delete the test policy** — document the finding

### Step 4 — Move to Enforced after the report-only period

After 7 days in `enabledForReportingButNotEnforced`:

```http
PATCH https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policy-id}
Content-Type: application/json

{
  "state": "enabled"
}
```

### Step 5 — KQL: monitor CA policy applications in Sentinel

```kql
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(7d)
| where ConditionalAccessStatus == "failure"
| extend PolicyName = tostring(ConditionalAccessPolicies[0].displayName)
| extend PolicyResult = tostring(ConditionalAccessPolicies[0].result)
| summarize
    BlockedAttempts = count(),
    LastAttempt = max(TimeGenerated),
    SourceIPs = make_set(IPAddress, 10)
    by ServicePrincipalName, PolicyName, PolicyResult
| sort by BlockedAttempts desc
```

## Verification

- [ ] CA policy created with `includeAgentIdServicePrincipals: "All"`
- [ ] What If confirms the policy applies to the agent SP at Medium risk
- [ ] What If confirms the policy does NOT apply to user accounts
- [ ] `grantControls: mfa` validated as ineffective and documented
- [ ] Policy in report-only for a minimum of 7 days before enforcing
- [ ] Monitoring KQL running in Sentinel as a Scheduled Rule

## Implementation notes

- Blueprint-level CA (`includeAgentIdServicePrincipals: All`) covers all current and future agents — this is the correct scaling pattern vs. per-instance
- `Entra Workload ID Premium` is required to add service principal risk conditions (sign-in risk) — without this license only the base condition is available
- Always document the What If result as evidence in the Gap Assessment Template — it is the only validation mechanism that does not require generating real traffic
- Official reference: [Conditional Access for workload identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity)
