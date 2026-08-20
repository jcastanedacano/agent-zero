---
name: govern-ca-policy-workload-identity
version: "1.0"
pillar: govern
subdomain: ms-entra
description: >-
  Implements Conditional Access policies in Entra ID for AI agent workload
  identities, blocking access outside corporate IP ranges and applying
  session controls. grantControls mfa is invalid for non-human identities;
  only block or no grantControls applies.
tags: [govern, entra, conditional-access, workload-identity, agent-identity]
atlas_techniques: [AML.T0056, AML.T0046]
d3fend_techniques: [D3-UAP, D3-NTF]
nist_ai_rmf: [GOVERN-2.2, MANAGE-1.3]
nist_csf: [PR.AA-05, PR.AC-01]
ms_license: [Microsoft Entra ID P1, Microsoft Entra Workload ID]
ms_roles: [Conditional Access Administrator, Security Administrator]
effort_hours: 8
---

## When to use

- Post Pillar 1: agents classified as High risk require access controls
- The customer has Entra ID P1 (a hard prerequisite for CA)
- Workload ID license required for CA policies on specific service principals

## Critical implementation constraints

**`grantControls: mfa` is INVALID for workload identities.** Only these apply:
- `grantControls: { builtInControls: ["block"] }` — full block
- No `grantControls` + `sessionControls` — session restrictions

**`continuousAccessEvaluation`** cannot be in `enabledForReportingButNotEnforced`.
It must be `disabled` or `enabled` directly.

Always start in `enabledForReportingButNotEnforced` → monitor for 5-7 days → enable.

## Prerequisites

- Agent service principals identified (Pillar 1 output)
- Named Locations configured with the tenant's corporate IPs
- Entra Workload ID license assigned (for CA on non-human identities)

## Workflow

### Step 1 — Get the service principal's object ID

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals
  ?$filter=displayName eq '{AgentDisplayName}'
  &$select=id,appId,displayName
```

Record the `id` (object ID) — not the `appId`.

### Step 2 — Create a Named Location (if it does not exist)

```http
POST https://graph.microsoft.com/v1.0/identity/conditionalAccess/namedLocations
Content-Type: application/json

{
  "@odata.type": "#microsoft.graph.ipNamedLocation",
  "displayName": "Corporate Network - {TenantName}",
  "isTrusted": true,
  "ipRanges": [
    {
      "@odata.type": "#microsoft.graph.iPv4CidrRange",
      "cidrAddress": "10.0.0.0/8"
    }
  ]
}
```

Record the created Named Location's `id`.

### Step 3 — Create the CA policy in report-only

```http
POST https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies
Content-Type: application/json

{
  "displayName": "AISEC-Block-Agents-Outside-CorpNetwork",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "clientApplications": {
      "includeServicePrincipals": ["{service-principal-object-id}"]
    },
    "locations": {
      "includeLocations": ["All"],
      "excludeLocations": ["{named-location-id}"]
    }
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["block"]
  }
}
```

### Step 4 — Monitor in Sign-in logs (5-7 days)

```
Entra ID → Monitoring → Sign-in logs
→ Filter: Service principal sign-ins
→ Search for: Conditional Access = "Report-only: Would be blocked"
```

Confirm there are no false positives (legitimate access that would be blocked).

### Step 5 — Activate enforcement

```http
PATCH https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policy-id}
Content-Type: application/json

{
  "state": "enabled"
}
```

## Verification

- [ ] Named Location created with correct IPs
- [ ] Policy in report-only with no false positives after 5-7 days
- [ ] Policy activated (`state: enabled`)
- [ ] Sign-in logs show blocks from external IPs
- [ ] No impact on legitimate agent access

## Implementation notes

- Known error `AADSTS500011`: the resource principal does not exist in the tenant — verify the agent SP exists with `GET /servicePrincipals/`
- Keep agent CA policies in report-only mode for at least 7 days to identify false positives before enforcing
- Blueprint-level CA (applied to SP groups via `includeAgentIdServicePrincipals`) scales better than per-instance — use this pattern from the start
- `grantControls: mfa` is invalid for agent identities — use only `block` or `sessionControls`
