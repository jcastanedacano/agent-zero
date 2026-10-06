# Module 03 — Secure Access | Track C

**Duration:** 90 minutes  
**Tables:** `CloudAppEvents`, `EntraIdSpnSignInEvents`, `AuditLogs`  
**Portals:** Entra ID (Conditional Access + PIM), Defender for Cloud Apps  
**Minimum role:** Security Admin (scoped to demo tenant)

---

## Learning Objective

At the end of this module, you will be able to configure a Conditional Access policy targeting agent identities using the dedicated **Agents** assignment type in Entra CA, validate it in report-only mode with the sign-in logs, detect OAuth consent drift via KQL, and document the critical difference between CA for users and CA for agents.

---

## Agenda

| Time | Activity | Type |
|------|----------|------|
| 15 min | Entra CA for Agents: scopes, Block as the only control, targeting all agents, a blueprint or an attribute | Explanation |
| 10 min | OAuth consent without control: how agents accumulate unreviewed permissions | Explanation |
| 55 min | Lab: CA policy for agents in report-only + sign-in log validation + OAuth audit KQL | Lab |
| 10 min | Results review + playbook section 3 documentation | Discussion |

---

## Core Content

1. **MFA is not the control for agents:** Agents cannot complete interactive MFA, and Microsoft Learn documents **Block** as the only access control for agent identities. A user policy that requires MFA does not reach an agent that acts as itself, so a tenant that counts on its user MFA policy has no policy on its agents. Agents need their own policy: the Agents assignment, the agent risk condition and `block`. Learn does not document what the Graph API does when it is sent another grant control, so this module does not claim it.

2. **Targeting at scale:** A CA policy per agent instance does not scale. Under `Assignments → Agents`, **All agent identities** covers every agent identity in the tenant, including the ones created later; the object picker also accepts specific agent identities or blueprints (a blueprint target covers the identities created from it, including later ones) and custom security attributes. To allow only approved agents, exclude them from an All-agent-identities Block policy.

3. **OAuth consent drift as a silent accumulation vector:** Without consent flow restrictions, an agent can accumulate additional permissions without explicit approval. The signal: `AuditLogs` → `Add delegated permission grant` without correlation to an `AgentPermissionApproved` event. Caveat: that approval event name is not confirmed to exist on a live tenant (see Module 02, Step 6).

4. **Model extraction via API — model theft through the endpoint:** An attacker with access to an Azure AI Foundry endpoint can reconstruct a proprietary model through systematic queries (input/output pairs), without direct model access. The indicator is a massive inference volume from a single identity with high prompt variety. KQL P03-Q6 detects this pattern. Control: per-identity rate limiting in Foundry + CA policy blocking unauthorized identities. Maps to OWASP LLM Top 10 2026, LLM06 — Unbounded Consumption (model extraction/theft was folded into this category in 2026).

5. **Agent ID objects leave an audit trail, but under generic names: correlate by ID, not by name.** Validated on a live tenant (October 2026): the blueprint is logged in Entra `AuditLogs` as an *Application* and the agent identity as a *ServicePrincipal*, and every operation observed on them was a generic one: `Add application`, `Add service principal`, `Create application – Certificates and secrets management`, `Update application – Certificates and secrets management`, `Add service principal credentials`, `Add owner to application`, `Add owner to service principal`, `Add user sponsor`, `Consent to application`, `Add app role assignment to service principal`, and `Update application` / `Update service principal`. No operation name identifies an object as an agent, and `ResType` only says `Application` or `ServicePrincipal`. The display name does not work as a filter either: the creator chooses it, a Foundry agent identity appeared with a GUID as its name, and an agent identity named "Hermes Identity" contains no "blueprint". The reliable key is `AgentsInfo`: in the validated tenant, joining `EntraAgentID` and `EntraBlueprintID` against the object id in `AuditLogs` matched the blueprint's Application object and the agent identity's ServicePrincipal object (KQL P03-Q12).

   **What to look for, in order of signal.** A credential added to a blueprint (`Add service principal credentials`, `… – Certificates and secrets management`) is rare and high-signal. Only the blueprint holds credentials (Microsoft Learn: you create credentials on the blueprint, not on individual agent identities), so the operation on an agent identity is refused: the one attempt seen on the validation tenant appears with `Result` = `failure`, a blocked attempt that is still worth reading. Per Microsoft Learn, the Agent ID Developer role can configure federated identity credentials on a blueprint, the create-blueprint page names Agent ID Administrator for adding a secret or certificate, and the permissions reference also lists `agentIdentityBlueprints/credentials/update` under AI Administrator. The platform's own ID Protection detection flags new blueprint credentials only after they are *used* (`suspiciousCredentialUsage`), so the hunt for the addition itself is the earlier signal. Owner and sponsor changes (`Add owner to …`, `Add user sponsor`) show who can modify, re-enable, or delete the agent. Read the actor before the operation: in the validated tenant a person created a blueprint and its identity, a Graph PowerShell application tried to add a credential to the agent identity and was refused (`Result` = `failure`, 2026-09-17), and Microsoft's own provisioning (`Microsoft Azure AD Internal - Jit Provisioning`) created the first-party Copilot Studio blueprint service principal with no human involved. An `application` actor on a credential change deserves review before a `user` one; Microsoft-internal provisioning is a baseline, not an alert.

   **Two coverage limits to state in the lab.** The blueprint *principal* (the blueprint's service principal, where `Consent to application` and `Add app role assignment` were logged) matched neither `AgentsInfo` column, so consent and app-role changes on it are outside this join. And an agent with both IDs empty in `AgentsInfo` is invisible to it. **A field that does not close the first gap here.** Microsoft Learn documents `agentType` (`agenticApp`, `agenticAppInstance`, `agentIdentityBlueprintPrincipal`, `agentIDuser`) and `blueprintId` on audit `targetResources`. In the `AuditLogs` table of the validation workspace the key `agentType` exists on every target resource (and `agentType` plus `blueprintId` on `initiatedBy.app`), but its only value over 90 days was `notAgentic`, including for the Hermes blueprint and agent identity, so this lab still joins on ids. Check the values in your own workspace; if they are populated, filtering on them also covers blueprint principals and agent users. In this module's terms (Module 06, point 8), these changes are identity-plane persistence and privilege escalation, not input-plane attacks.

---

## Background

### Why MFA is not the control for agents

Agents cannot complete interactive MFA, and Microsoft Learn documents Block as the only access control for agent identities. A user policy that requires MFA does not reach an agent acting as itself, and a policy written for the agent identity does not apply to its agent user. The shape of an agent policy in Microsoft Graph (beta) is a Block with the agent risk condition:

```json
"conditions": {
  "clientApplications": { "includeAgentIdServicePrincipals": ["All"] },
  "agentIdRiskLevels": "high"
},
"grantControls": { "operator": "OR", "builtInControls": ["block"] }
```

What the API does with a grant control that the portal does not offer is not documented by Learn, so this module does not teach it as a finding.

Reference: [Conditional Access for agents](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id) | [Conditional Access for workload identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity)


---

## Background

### One policy for many agents, not one per instance

Creating a separate CA policy for each agent instance is an antipattern that fails at scale. The **Agents** assignment type in Entra CA (`Assignments → Users, agents or workload identities → Agents → All agent identities`) covers all agent identities in the tenant. To scope to a blueprint, pick the blueprint in the object picker: it covers every agent identity created from it, including the ones created later, but not the blueprint's agent user accounts. To scope by label, use a custom security attribute on the agents.

### Identity laundering in the audit log

When an agent acts under a user's identity (no Entra Agent ID, inherited permissions), the audit log records `"Alice performed action X"` — not the agent. This makes post-incident investigation impossible: you cannot distinguish user action from agent action in the log. Entra Agent ID + dedicated CA policy is the only way to create a separate audit trail for agent actions.

---

## Lab

### Step 1 — Create a CA policy for agent identities

Microsoft Entra now has a dedicated **Agents** assignment type for CA policies — separate from "Workload identities" (service principals). Use this path for all new agent CA policies.

1. In **Microsoft Entra admin center** → **Security** → **Conditional Access** → **New policy**
2. Name: `Agentic AI — Risk-Based Access Control`
3. **Assignments → Users, agents or workload identities:**
   - Under **What does this policy apply to?** → select **Agents**
   - Under **Include** → select **All agent identities**
4. **Target resources → Resources:** Include **All resources**
5. **Conditions → Agent risk (Preview):**
   - Configure: **Yes**
   - Select risk levels: **High** (recommended starting point; lower to Medium after baseline review)
6. **Access controls → Grant:** Select **Block**
7. **Enable policy:** Set to **Report-only** first
8. Select **Create**

> **Why Report-only first:** In a demo tenant, blocking agents immediately may break lab workflows. Report-only lets you validate behavior using the sign-in logs before enforcing.

> **License note:** Conditional Access for agents requires Microsoft 365 E7, or a Microsoft Agent 365 license with at least Microsoft Entra ID P1 or Microsoft 365 E3. Workload ID Premium is a different license, for classic workload identities.

---

### Step 2 — Validate in report-only mode

Learn's agent articles validate with report-only mode and the sign-in logs; they do not describe the What If tool for agents.

1. In **Entra ID** → **Monitoring & health** → **Sign-in logs** → **Service principal sign-ins**
2. Open a sign-in of `demo-sales-agent` that requests a token for a real resource (for example Microsoft Graph)
3. Read the **Conditional Access** tab and the **Report-only** tab

**Expected result:** `Agentic AI — Risk-Based Access Control` is listed as `reportOnlyNotApplied` while the agent risk is below High (the condition is not met) and as `reportOnlyFailure` when it would have blocked. Query 2 of `skills/secure/secure-ca-policy-agents/queries/sentinel-ca-agents.kql` returns the same information for all agent sign-ins.

**Boundary:** the sign-ins of an agent identity at the `AAD Token Exchange Endpoint: Public`, and the token a blueprint requests to create an agent identity, are outside Conditional Access (Learn), so they show `notApplied`. Judge the policy on the sign-ins that request a token for a real resource.

**Document:** screenshot the tab, or save the Query 2 result, for your playbook.

---

### Step 3 — Check that the user MFA policies do not reach the agent

Agents cannot complete interactive MFA, and Learn documents Block as the only access control for agent identities. The assumption to test is the opposite one: that the tenant's MFA policy for users also protects the agents.

1. In **Conditional Access** → **Policies**, find a policy that requires MFA for all users
2. In the **Conditional Access** tab of the agent sign-in from Step 2 (or in `ConditionalAccessPolicies` with Query 2), look for that policy

**Expected result:** the user MFA policy is not among the policies evaluated for the agent sign-in: only agent policies are listed. On the validation tenant (October 2026) the 2351 service principal sign-ins of 90 days that carried an evaluation each listed the same four policies, all of them agent policies, while the tenant had enabled Conditional Access policies for all users. An organization that counts on its user MFA policy has no policy on its agents.

This module does not test what the Graph API does when it is sent a grant control that the portal does not offer: Learn does not document it.

> **Reference:** [Conditional Access for agents](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id) and [Conditional Access for workload identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity) ("Can't perform multifactor authentication").

---

### Step 4 — KQL: OAuth consent grants without review

```kql
AuditLogs
| where TimeGenerated > ago(30d)
| where OperationName == "Consent to application"
| extend ConsentedApp = tostring(TargetResources[0].displayName)
| extend ConsentedBy = tostring(InitiatedBy.user.userPrincipalName)
| mv-apply MP = TargetResources[0].modifiedProperties on (
    where tostring(MP.displayName) == "ConsentAction.Permissions"
    | summarize ScopesGranted = take_any(tostring(MP.newValue)))
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

**Validated on a Sentinel workspace (October 2026).** The scopes are in the `ConsentAction.Permissions` property, not in `modifiedProperties[0]` (which is `ConsentContext.IsAdminConsent`): the earlier version could never match, and the fix turned 0 rows into 7 over 30 days. The query is not agent-specific: it lists every high-privilege consent.

---

### Step 5 — KQL: Agent sign-ins outside business hours

```kql
EntraIdSpnSignInEvents
| where Timestamp > ago(7d)
| where ServicePrincipalName has "agent"
| extend HourOfDay = datetime_part("Hour", Timestamp)
| extend IsOffHours = HourOfDay < 6 or HourOfDay > 22
| where IsOffHours == true
| summarize
    OffHoursSignIns = count(),
    EarliestSignIn = min(Timestamp),
    LatestSignIn = max(Timestamp),
    LocationSet = make_set(Country)
    by ServicePrincipalName, ApplicationId
| sort by OffHoursSignIns desc
```

**Expected output:** Agent identities signing in outside configured business hours — a baseline deviation signal. The column is `ApplicationId`: `EntraIdSpnSignInEvents` has no `AppId` (validated in Advanced Hunting, October 2026).

---

### Step 6 — KQL: Agents accessing resources outside declared scope

```kql
EntraIdSpnSignInEvents
| where Timestamp > ago(7d)
| where ServicePrincipalName has "agent"
| summarize
    ResourcesAccessed = make_set(ResourceDisplayName),
    AccessCount = count(),
    LastAccess = max(Timestamp)
    by ServicePrincipalId, ServicePrincipalName, ApplicationId
| extend ResourceCount = array_length(ResourcesAccessed)
| where ResourceCount > 3
| sort by ResourceCount desc
| project ServicePrincipalName, ApplicationId, ResourceCount, ResourcesAccessed, AccessCount, LastAccess
```

**Adjust the threshold** (`ResourceCount > 3`) based on your expected agent scope. An agent declared as a SharePoint reader with access to 12 distinct resources is a scope expansion signal.

**Limit of this query:** `ServicePrincipalName has "agent"` filters by display name, which the creator chooses (see point 5). An agent identity whose name lacks the word is skipped. Treat the result as a lower bound, or join `AgentsInfo` on `EntraAgentID` as Step 7 does.

---

### Step 7 — KQL: credential, owner, and sponsor changes on Agent ID objects

Run `KQL-Library/P03-Access-Anomalies.kql`, Q12. It correlates `AuditLogs` with `AgentsInfo` by object id, so it finds blueprints and agent identities whatever they are named.

**Expected output:** one row per credential, owner, or sponsor change in the last 7 days on an object listed in `AgentsInfo`, with `Result`, `ObjectType` (`Application` for a blueprint, `ServicePrincipal` for an agent identity), `Actor` and `ActorType`. A credential operation on an agent identity with `Result` = `failure` is a blocked attempt, not an added credential.

**ATT&CK mapping (our own, ATT&CK Enterprise v19.2, ids and names checked against the ATT&CK data):**

| `OperationName` | ATT&CK technique | Note |
|---|---|---|
| `Add service principal credentials`; `Create application – Certificates and secrets management`; `Update application – Certificates and secrets management` | T1098.001 Account Manipulation: Additional Cloud Credentials | ATT&CK's detection strategy DET0531 (analytic AN1469) lists `azure:audit` `Add service principal credentials` for this technique |
| `Add owner to application`; `Add owner to service principal`; `Add user sponsor` | T1098 Account Manipulation | No sub-technique covers ownership or sponsorship, so T1098 is the closest match (our judgment). An owner can add credentials, which is T1098.001 |

Consent and app role changes on the blueprint principal are covered by Step 8. A refused credential attempt (`Result` = `failure`) is still an attempt at T1098.001.

**Document in your playbook:** Which rows have `ActorType = application`, and which have `Result` = `failure`? For each credential change, is there a change record? Who are the owners and sponsors added, and are they the people your governance registry says are accountable (Track B Module 02)?

**If it returns no rows:** either nothing changed in 7 days, or the agent has both `EntraAgentID` and `EntraBlueprintID` empty in `AgentsInfo`, or the change was on the blueprint principal, which this join does not cover. Widen the window to 90 days before concluding anything.

---

### Step 8 — KQL: consent and app-role grants on blueprint principals

Run `KQL-Library/P03-Access-Anomalies.kql`, Q13. A blueprint declares two lists that grant nothing by themselves, *required resource access* and *inheritable permissions*; consent on the blueprint principal is what grants, and when the resource app is inheritable the grant reaches every current and future agent identity from that blueprint. Inherited permissions are not shown on the agent identities in the Entra admin center or Microsoft Graph, only in the token's `scp` and `roles` claims at runtime (Microsoft Learn, inheritable permissions). The grants themselves stay visible on the blueprint principal, so the audit event is the earliest signal.

**Expected output:** one row per `Consent to application` or `Add app role assignment to service principal` in the last 7 days whose target is a blueprint principal, with `Result`, `Actor`, `ActorType`, and the raw `TargetResources` for the permission details.

**Coverage, stated plainly.** `AgentsInfo` carries the blueprint's id but not the principal's object id, and a `Consent to application` record names its target by display name only. Q13 therefore matches app-role assignments by the blueprint id found in the principal's service principal names (run against the real `AuditLogs` of the validation workspace: it returns the 2026-09-17 grant on the Hermes blueprint principal), and matches consent events only when the record carries `agentType` = `agentIdentityBlueprintPrincipal`, which Microsoft Learn documents and which never appeared there (the only value in 90 days was `notAgentic`), so the consent on that principal was missed. In that workspace `AgentsInfo` exists but is empty, so the query needs `AgentsInfo` ingested, or its side run in Advanced Hunting.

**ATT&CK mapping (our own, ATT&CK Enterprise v19.2, ids and names checked against the ATT&CK data):** `Consent to application` maps to T1671 Cloud Application Integration (ATT&CK's detection strategy DET0539 lists the `azure:audit` operation `Consent to application`); `Add app role assignment to service principal` maps to T1098.003 Account Manipulation: Additional Cloud Roles (DET0277 lists `Add app role assignment`).

**Document in your playbook:** Which blueprints are multi-tenant? Who consented, was it an admin consent, and does the permission list match what the blueprint declared in required resource access? Treat every grant on a third-party blueprint principal as potentially inherited by all of its agent identities, because the inheritance configuration lives in the publisher's tenant and cannot be verified locally.

---

### Step 9 — KQL: Identity Protection risk events on agents

Run `KQL-Library/P03-Access-Anomalies.kql`, Q14. ID Protection for agents evaluates eight offline detection types (Track B Module 02, point 12). Microsoft Learn does not say whether these detections raise an incident or alert in Defender XDR: check in your tenant, and if they do not, a custom rule is the path to the SOC queue.

**Prerequisites:** the Entra diagnostic settings must export the agent risk categories to your Log Analytics workspace (Microsoft Learn, export risk data), and ID Protection for agents requires an Agent 365 license (Learn: "starting soon"; Entra ID P2 during the preview). Detections are retained for 90 days, learning mode suppresses behavioral alerts for agents with little history, and in on-behalf-of flows the risk lands on the user, so an empty result is not proof of safety.

**Expected output:** one row per medium or high risk event in the last hour, with the agent's `AgentsInfo` record when `AgentId` matches `EntraAgentID`. On the validation workspace the tables exist but have no rows, so the query runs and returns nothing; its join was exercised against a table shaped like it.

---

## Playbook Section 3 — Document Your Findings

```markdown
## Section 3: Access Control Configuration

### CA Policy Deployed
- Policy name: Agentic AI — Risk-Based Access Control
- Scope: [all agent identities / blueprint / specific agent identities]
- Condition: Agent risk (preview) High
- Grant: Block
- Status: Report-only / Enforced

### Critical Configuration Note
Block is the only access control for agent identities (Microsoft Learn). MFA policies written for users do not reach agents.
Validated in report-only on [DATE]: [screenshot or Query 2 output attached].

### Report-only Validation
- [ ] Policy listed in ConditionalAccessPolicies of the agent sign-ins (reportOnlyNotApplied or reportOnlyFailure): [screenshot or query output attached]
- [ ] No user MFA policy among the policies evaluated for the agent: [screenshot or query output attached]
- [ ] Days in report-only before enforcing: [N, minimum 7]

### Access Anomaly KQL Queries (add to Sentinel)
- [ ] OAuth high-privilege consent without review (weekly)
- [ ] Agent sign-ins outside business hours (daily)
- [ ] Agents accessing more than [N] resources (weekly)
- [ ] Credential, owner, and sponsor changes on Agent ID objects (hourly, review `application` actors first)
- [ ] Consent and app-role grants on blueprint principals (hourly)
- [ ] Identity Protection risk events on agents (every 15 minutes)

### Findings
| Agent | Resources Accessed | Expected Scope | Gap |
|-------|--------------------|----------------|-----|
| | | | |
```

---

## Closing Questions

- What did the Conditional Access tab of the agent sign-in show about the tenant's user MFA policies? How would you document this finding in a configuration hardening guide so that a colleague does not assume a user MFA policy covers agents?
- When comparing `EntraIdSpnSignInEvents` for agent identities vs. `SigninLogs` for user identities, what fields are present in one but not the other? What does that mean for correlation queries that need to cover both?

---

## Connection to Module 04

With access controlled and identity separated, the remaining attack surface is the data itself: prompts containing sensitive information, responses that reveal data from other users, and connectors that silently exfiltrate to external endpoints. The next module covers Purview DLP for AI interactions and KQL-based exfiltration detection.

→ [Module 04 — Protect Data](./Module-04-ProtectData.md)
