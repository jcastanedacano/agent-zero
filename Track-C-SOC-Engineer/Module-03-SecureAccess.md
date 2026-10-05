# Module 03 — Secure Access | Track C

**Duration:** 90 minutes  
**Tables:** `CloudAppEvents`, `EntraIdSpnSignInEvents`, `AuditLogs`  
**Portals:** Entra ID (Conditional Access + PIM), Defender for Cloud Apps  
**Minimum role:** Security Admin (scoped to demo tenant)

---

## Learning Objective

At the end of this module, you will be able to configure a Conditional Access policy targeting agent identities using the dedicated **Agents** assignment type in Entra CA, validate it with the What If tool, detect OAuth consent drift via KQL, and document the critical difference between CA for users and CA for agents.

---

## Agenda

| Time | Activity | Type |
|------|----------|------|
| 15 min | Entra CA for Agents: scopes, grant control limitations, Blueprint-level policies | Explanation |
| 10 min | OAuth consent without control: how agents accumulate unreviewed permissions | Explanation |
| 55 min | Lab: CA policy for agents + What If validation + OAuth audit KQL | Lab |
| 10 min | Results review + playbook section 3 documentation | Discussion |

---

## Core Content

1. **The `grantControls: mfa` trap for agents:** A CA policy with `mfa` as a grant control on agent identities is silently invalid — it neither blocks nor forces authentication. Agents cannot complete interactive MFA and the policy generates no enforcement event in the logs. Only `"block"` is valid to block agent access via CA.

2. **Blueprint-level CA as a scaling pattern:** A CA policy per agent instance does not scale. The correct pattern targets the **agent identity blueprint** under `Assignments → Agents → All agent identities` — this automatically covers all current and future agent identities derived from the same blueprint without per-instance configuration.

3. **OAuth consent drift as a silent accumulation vector:** Without consent flow restrictions, an agent can accumulate additional permissions without explicit approval. The signal: `AuditLogs` → `Add delegated permission grant` without correlation to an `AgentPermissionApproved` event. Caveat: that approval event name is not confirmed to exist on a live tenant (see Module 02, Step 6).

4. **Model extraction via API — model theft through the endpoint:** An attacker with access to an Azure AI Foundry endpoint can reconstruct a proprietary model through systematic queries (input/output pairs), without direct model access. The indicator is a massive inference volume from a single identity with high prompt variety. KQL P03-Q6 detects this pattern. Control: per-identity rate limiting in Foundry + CA policy blocking unauthorized identities. Maps to OWASP LLM Top 10 2026, LLM06 — Unbounded Consumption (model extraction/theft was folded into this category in 2026).

5. **Agent ID objects leave an audit trail, but under generic names: correlate by ID, not by name.** Validated on a live tenant (October 2026): the blueprint is logged in Entra `AuditLogs` as an *Application* and the agent identity as a *ServicePrincipal*, and every operation observed on them was a generic one: `Add application`, `Add service principal`, `Create application – Certificates and secrets management`, `Update application – Certificates and secrets management`, `Add service principal credentials`, `Add owner to application`, `Add owner to service principal`, `Add user sponsor`, `Consent to application`, `Add app role assignment to service principal`, and `Update application` / `Update service principal`. No operation name identifies an object as an agent, and `ResType` only says `Application` or `ServicePrincipal`. The display name does not work as a filter either: the creator chooses it, a Foundry agent identity appeared with a GUID as its name, and an agent identity named "Hermes Identity" contains no "blueprint". The reliable key is `AgentsInfo`: in the validated tenant, joining `EntraAgentID` and `EntraBlueprintID` against the object id in `AuditLogs` matched the blueprint's Application object and the agent identity's ServicePrincipal object (KQL P03-Q12).

   **What to look for, in order of signal.** A credential added to a blueprint (`Add service principal credentials`, `… – Certificates and secrets management`) is rare and high-signal. Only the blueprint holds credentials (Microsoft Learn: you create credentials on the blueprint, not on individual agent identities), so the operation on an agent identity is refused: the one attempt seen on the validation tenant appears with `Result` = `failure`, a blocked attempt that is still worth reading. Per Microsoft Learn, the Agent ID Developer role can configure federated identity credentials on a blueprint, the create-blueprint page names Agent ID Administrator for adding a secret or certificate, and the permissions reference also lists `agentIdentityBlueprints/credentials/update` under AI Administrator. The platform's own ID Protection detection flags new blueprint credentials only after they are *used* (`suspiciousCredentialUsage`), so the hunt for the addition itself is the earlier signal. Owner and sponsor changes (`Add owner to …`, `Add user sponsor`) show who can modify, re-enable, or delete the agent. Read the actor before the operation: in the validated tenant a person created a blueprint and its identity, a Graph PowerShell application tried to add a credential to the agent identity and was refused (`Result` = `failure`, 2026-09-17), and Microsoft's own provisioning (`Microsoft Azure AD Internal - Jit Provisioning`) created the first-party Copilot Studio blueprint service principal with no human involved. An `application` actor on a credential change deserves review before a `user` one; Microsoft-internal provisioning is a baseline, not an alert.

   **Two coverage limits to state in the lab.** The blueprint *principal* (the blueprint's service principal, where `Consent to application` and `Add app role assignment` were logged) matched neither `AgentsInfo` column, so consent and app-role changes on it are outside this join. And an agent with both IDs empty in `AgentsInfo` is invisible to it. **A field that may close the first gap.** Microsoft Learn documents `agentType` (`agenticApp`, `agenticAppInstance`, `agentIdentityBlueprintPrincipal`, `agentIDuser`) and `blueprintId` on audit `targetResources`. In the validated tenant, Graph `directoryAudits` returned `agentType` on `initiatedBy` (`notAgentic` where present) but returned neither field on the `targetResources` of the Hermes blueprint and agent identity (six events, 2026-09-17), so this lab still joins on ids. Check `AuditLogs.TargetResources` in your workspace before relying on either; if the fields are there, filtering on them also covers blueprint principals and agent users. In this module's terms (Module 06, point 8), these changes are identity-plane persistence and privilege escalation, not input-plane attacks.

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

Reference: [Conditional Access for agents](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id) | [Conditional Access for workload identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity)


---

## Background

### Blueprint-level CA vs. per-instance policies

Creating a separate CA policy for each agent instance is an antipattern that fails at scale. The new **Agents** assignment type in Entra CA (`Assignments → Users, agents or workload identities → Agents → All agent identities`) covers all agent identities in the tenant. To scope to a specific blueprint, select individual agent identities under the same blueprint — every new agent identity derived from that blueprint is automatically covered.

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

> **Why Report-only first:** In a demo tenant, blocking agents immediately may break lab workflows. Report-only lets you validate behavior using the What If tool and Sign-in logs before enforcing.

> **License note:** Conditional Access for agents requires Entra ID P1 or P2 and a Microsoft Agent 365 license.

---

### Step 2 — Validate with What If tool

1. In **Conditional Access** → **What If**
2. Under **User or workload identity:** select **Workload identity** → choose `demo-sales-agent`
3. Under **Cloud app:** select **Microsoft Graph**
4. Under **Agent risk:** set to **High**
5. Click **What If**

**Expected result:** The policy `Agentic AI — Risk-Based Access Control` appears in the results as "Will apply" with action "Block."

**Document:** Screenshot the What If result for your playbook. This is your evidence that the policy applies correctly to agent identities and not to user accounts (run a second What If with a user account to confirm the policy does not appear).

---

### Step 3 — Confirm `grantControls: mfa` behavior for agents

Agents cannot complete interactive MFA. A CA policy with MFA as a grant control on agent identities is silently invalid — it generates no enforcement event and no error.

1. Duplicate the policy from Step 1
2. Under **Assignments**, switch from **Agents** to **Workload identities → Service principals** → select `demo-sales-agent`
3. Change **Grant** from **Block access** to **Require multifactor authentication**
4. Save as `TEST — MFA Grant for Agent (invalid)`
5. Run What If with the same agent identity and High risk

**Expected result:** The MFA policy appears as "Will apply" — but the grant control cannot be enforced because agents cannot satisfy MFA. Microsoft's official documentation confirms: for agent identities, only `Block` is a valid grant control. This is the silent misconfiguration that creates a false sense of security.

6. Delete the test policy after documenting the finding.

> **Reference:** [Microsoft Entra — Conditional Access for workload identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity) — "Can't perform multifactor authentication."

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
    by ServicePrincipalName, AppId
| sort by OffHoursSignIns desc
```

**Expected output:** Agent identities signing in outside configured business hours — a baseline deviation signal.

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
    by ServicePrincipalId, ServicePrincipalName, AppId
| extend ResourceCount = array_length(ResourcesAccessed)
| where ResourceCount > 3
| sort by ResourceCount desc
| project ServicePrincipalName, AppId, ResourceCount, ResourcesAccessed, AccessCount, LastAccess
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

**Coverage, stated plainly.** `AgentsInfo` carries the blueprint's id but not the principal's object id, and a `Consent to application` record names its target by display name only. Q13 therefore matches app-role assignments by the blueprint id found in the principal's service principal names (checked on a Graph `directoryAudits` sample: it matches the 2026-09-17 grant on the Hermes blueprint principal), and matches consent events only when the record carries `agentType` = `agentIdentityBlueprintPrincipal`, which Microsoft Learn documents and this tenant's Graph output did not show. Q13 was not run against `AuditLogs`: the validation session had no Log Analytics workspace access.

**ATT&CK mapping (our own, ATT&CK Enterprise v19.2, ids and names checked against the ATT&CK data):** `Consent to application` maps to T1671 Cloud Application Integration (ATT&CK's detection strategy DET0539 lists the `azure:audit` operation `Consent to application`); `Add app role assignment to service principal` maps to T1098.003 Account Manipulation: Additional Cloud Roles (DET0277 lists `Add app role assignment`).

**Document in your playbook:** Which blueprints are multi-tenant? Who consented, was it an admin consent, and does the permission list match what the blueprint declared in required resource access? Treat every grant on a third-party blueprint principal as potentially inherited by all of its agent identities, because the inheritance configuration lives in the publisher's tenant and cannot be verified locally.

---

### Step 9 — KQL: Identity Protection risk events on agents

Run `KQL-Library/P03-Access-Anomalies.kql`, Q14. ID Protection for agents evaluates eight offline detection types (Track B Module 02, point 12). Microsoft Learn does not say whether these detections raise an incident or alert in Defender XDR: check in your tenant, and if they do not, a custom rule is the path to the SOC queue.

**Prerequisites:** the Entra diagnostic settings must export the agent risk categories to your Log Analytics workspace (Microsoft Learn, export risk data), and ID Protection for agents requires an Agent 365 license (Learn: "starting soon"; Entra ID P2 during the preview). Detections are retained for 90 days, learning mode suppresses behavioral alerts for agents with little history, and in on-behalf-of flows the risk lands on the user, so an empty result is not proof of safety.

**Expected output:** one row per medium or high risk event in the last hour, with the agent's `AgentsInfo` record when `AgentId` matches `EntraAgentID`. Not run against a workspace that has these tables: the validation session had no workspace access.

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

- What happened when you set `grantControls: mfa` for the agent identity in the What If test? How would you document this finding in a configuration hardening guide to prevent a colleague from repeating the error?
- When comparing `EntraIdSpnSignInEvents` for agent identities vs. `SigninLogs` for user identities, what fields are present in one but not the other? What does that mean for correlation queries that need to cover both?

---

## Connection to Module 04

With access controlled and identity separated, the remaining attack surface is the data itself: prompts containing sensitive information, responses that reveal data from other users, and connectors that silently exfiltrate to external endpoints. The next module covers Purview DLP for AI interactions and KQL-based exfiltration detection.

→ [Module 04 — Protect Data](./Module-04-ProtectData.md)
