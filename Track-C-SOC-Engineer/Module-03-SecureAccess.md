# Module 03 — Secure Access | Track C

**Duration:** 90 minutes  
**Tables:** `CloudAppEvents`, `AADServicePrincipalSignInLogs`, `AuditLogs`  
**Portals:** Entra ID (Conditional Access + PIM), Defender for Cloud Apps  
**Minimum role:** Security Admin (scoped to demo tenant)

---

## Learning Objective

At the end of this module, you will be able to configure a Conditional Access policy targeting agent identities using `clientApplications.includeAgentIdServicePrincipals`, validate it with the What If tool, detect OAuth consent drift via KQL, and document the critical difference between CA for users and CA for agents.

---

## Agenda

| Time | Activity | Type |
|------|----------|------|
| 15 min | Entra CA for Agents: scopes, grant control limitations, Blueprint-level policies | Explanation |
| 10 min | OAuth consent without control: how agents accumulate unreviewed permissions | Explanation |
| 55 min | Lab: CA policy for agents + What If validation + OAuth audit KQL | Lab |
| 10 min | Results review + playbook section 3 documentation | Discussion |

---

## Background

### The `grantControls: mfa` trap

This is the most common misconfiguration in CA policies for agents:

```json
// THIS DOES NOT WORK FOR AGENTS — do not use
"grantControls": {
  "builtInControls": ["mfa"]
}
```

For agent identities, `mfa` as a grant control is **silently invalid** — it neither enforces MFA (agents cannot complete it) nor blocks access. The policy appears active but creates no enforcement. The correct options are:

- `"builtInControls": ["block"]` — explicitly blocks access
- No `grantControls` block — use `sessionControls` instead for monitoring

Reference: [Conditional Access for workload identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity)

### Blueprint-level CA vs. per-instance policies

Creating a separate CA policy for each agent instance is an antipattern that fails at scale. Blueprint-level CA policies target `clientApplications.includeAgentIdServicePrincipals` and apply to all agent identities derived from the same blueprint — covering all current and future instances without per-instance configuration.

### Identity laundering in the audit log

When an agent acts under a user's identity (no Entra Agent ID, inherited permissions), the audit log records `"Alice performed action X"` — not the agent. This makes post-incident investigation impossible: you cannot distinguish user action from agent action in the log. Entra Agent ID + dedicated CA policy is the only way to create a separate audit trail for agent actions.

---

## Lab

### Step 1 — Create a CA policy for agent identities

1. In **Entra ID** → **Security** → **Conditional Access** → **New policy**
2. Name: `Agentic AI — Risk-Based Access Control`
3. **Assignments → Users or workload identities:**
   - Select: **Workload identities**
   - Include: **Service principals** → filter to your `demo-sales-agent` app
4. **Assignments → Cloud apps:** All cloud apps
5. **Conditions → Service principal risk** (requires Entra ID Protection P2):
   - Enable: Yes
   - Risk levels: Medium and above
6. **Grant:** Select **Block access**
7. Enable policy: **Report-only** first (do not enable directly in production)
8. Save

> **Why Report-only first:** In a demo tenant, blocking access immediately may break lab workflows. Report-only lets you validate behavior before enforcing.

---

### Step 2 — Validate with What If tool

1. In **Conditional Access** → **What If**
2. User or workload identity: select `demo-sales-agent` service principal
3. Cloud app: select **Microsoft Graph**
4. Sign-in risk: set to **Medium**
5. Click **What If**

**Expected result:** The policy `Agentic AI — Risk-Based Access Control` appears in the results as "Will apply" with action "Block."

**Document:** Screenshot the What If result for your playbook. This is your evidence that the policy applies correctly to agent identities and not to user identities.

---

### Step 3 — Confirm `grantControls: mfa` behavior

1. Duplicate the policy from Step 1
2. Change **Grant** from **Block access** to **Require multifactor authentication**
3. Save as `TEST — MFA Grant for Agent (invalid)`
4. Run What If again with the same parameters

**Expected result:** The MFA policy shows as "Will apply" but the grant control is ineffective for service principals — note that What If may show "Grant: MFA required" but agents cannot satisfy this condition. This is the silent misconfiguration.

5. Delete the test policy after documenting the finding.

---

### Step 4 — KQL: OAuth consent grants without review

```kql
AuditLogs
| where TimeGenerated > ago(30d)
| where OperationName == "Consent to application"
| extend ConsentedApp = tostring(TargetResources[0].displayName)
| extend ConsentedBy = tostring(InitiatedBy.user.userPrincipalName)
| extend ScopesGranted = tostring(TargetResources[0].modifiedProperties[0].newValue)
| extend IsHighPrivilege = ScopesGranted has_any (
    "Files.ReadWrite.All",
    "Mail.ReadWrite",
    "Directory.ReadWrite.All",
    "Sites.FullControl.All",
    "User.ReadWrite.All"
)
| where IsHighPrivilege == true
| project
    TimeGenerated,
    ConsentedApp,
    ConsentedBy,
    ScopesGranted,
    RiskNote = "High-privilege OAuth consent — verify agent scope is intentional"
| sort by TimeGenerated desc
```

**Expected output:** Consent events where high-privilege scopes were granted to application identities without a corresponding approval record.

---

### Step 5 — KQL: Agent sign-ins outside business hours

```kql
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(7d)
| where ServicePrincipalName has "agent" or AppDisplayName has "agent"
| extend HourOfDay = datetime_part("Hour", TimeGenerated)
| extend IsOffHours = HourOfDay < 6 or HourOfDay > 22
| where IsOffHours == true
| summarize
    OffHoursSignIns = count(),
    EarliestSignIn = min(TimeGenerated),
    LatestSignIn = max(TimeGenerated),
    LocationSet = make_set(Location)
    by ServicePrincipalName, AppId
| sort by OffHoursSignIns desc
```

**Expected output:** Agent identities signing in outside configured business hours — a baseline deviation signal.

---

### Step 6 — KQL: Agents accessing resources outside declared scope

```kql
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(7d)
| where ServicePrincipalName has "agent" or AppDisplayName has "agent"
| summarize
    ResourcesAccessed = make_set(ResourceDisplayName),
    AccessCount = count(),
    LastAccess = max(TimeGenerated)
    by ServicePrincipalId, ServicePrincipalName, AppId
| extend ResourceCount = array_length(ResourcesAccessed)
| where ResourceCount > 3
| sort by ResourceCount desc
| project ServicePrincipalName, AppId, ResourceCount, ResourcesAccessed, AccessCount, LastAccess
```

**Adjust the threshold** (`ResourceCount > 3`) based on your expected agent scope. An agent declared as a SharePoint reader with access to 12 distinct resources is a scope expansion signal.

---

## Playbook Section 3 — Document Your Findings

```markdown
## Section 3: Access Control Configuration

### CA Policy Deployed
- Policy name: Agentic AI — Risk-Based Access Control
- Scope: [list targeted service principals]
- Condition: Service principal risk Medium+
- Grant: Block
- Status: Report-only / Enforced

### Critical Configuration Note
grantControls: mfa is INVALID for agent identities (clientApplications.includeAgentIdServicePrincipals).
Use block or sessionControls only. Confirmed in What If test on [DATE].

### What If Validation
- [ ] Policy applies to demo-sales-agent with Medium risk: [screenshot attached]
- [ ] Policy does NOT apply to user accounts: [screenshot attached]

### Access Anomaly KQL Queries (add to Sentinel)
- [ ] OAuth high-privilege consent without review (weekly)
- [ ] Agent sign-ins outside business hours (daily)
- [ ] Agents accessing more than [N] resources (weekly)

### Findings
| Agent | Resources Accessed | Expected Scope | Gap |
|-------|--------------------|----------------|-----|
| | | | |
```

---

## Closing Questions

- What happened when you set `grantControls: mfa` for the agent identity in the What If test? How would you document this finding in a configuration hardening guide to prevent a colleague from repeating the error?
- When comparing `AADServicePrincipalSignInLogs` for agent identities vs. `SigninLogs` for user identities, what fields are present in one but not the other? What does that mean for correlation queries that need to cover both?

---

## Connection to Module 04

With access controlled and identity separated, the remaining attack surface is the data itself: prompts containing sensitive information, responses that reveal data from other users, and connectors that silently exfiltrate to external endpoints. The next module covers Purview DLP for AI interactions and KQL-based exfiltration detection.

→ [Module 04 — Protect Data](./Module-04-ProtectData.md)
