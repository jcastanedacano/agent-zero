# Module 02 — Govern & Control | Track C

**Duration:** 90 minutes  
**Tables:** `AgentsInfo`, `AuditLogs`, `CloudAppEvents`  
**Portals:** Entra ID, Power Platform admin center, Copilot Studio admin center  
**Minimum role:** Security Admin (scoped to demo tenant)

---

## Learning Objective

At the end of this module, you will be able to configure Entra Agent ID with lifecycle management, create a DLP policy in Power Platform to restrict makers, enable Copilot Studio approval flow, and write KQL to detect agents that bypassed governance controls.

---

## Agenda

| Time | Activity | Type |
|------|----------|------|
| 15 min | Entra Agent ID: schema, lifecycle states, difference from service principals | Explanation |
| 10 min | Power Platform DLP: connector classification — Business / Non-business / Blocked | Explanation |
| 55 min | Lab: Agent ID + DLP + approval flow + governance gap KQL | Lab |
| 10 min | Results review + playbook section 2 documentation | Discussion |

---

## Core Content

1. **Agent Builder bypass as a systemic gap:** Agent Builder activates agents immediately without going through the Copilot Studio approval flow. This is a product-level design gap — not a configuration error. The compensating control is a CA policy on the Agent Builder App ID, or a Sentinel analytics rule filtering `AgentSource == "AgentBuilder"` on `AuditLogs`.

2. **Identity graph drift:** Agents accumulate OAuth permissions over time without review. The signal is in `AuditLogs` under `Add delegated permission grant` without a corresponding `AgentPermissionApproved` event — that absent join is the drift indicator. Caveat: `AgentPermissionApproved` is not confirmed to exist (see the note in Step 6), so as written every grant appears unapproved.

3. **Applicable Microsoft controls:** Entra Agent ID establishes a manageable identity per agent, separate from generic service principals. Copilot Studio governance enables the pre-publication approval flow. Foundry RBAC restricts operations in Azure AI. Power Platform DLP classifies and blocks connectors by category (Business / Non-business / Blocked).

4. **`grantControls: mfa` is invalid for agents:** Agents cannot complete interactive MFA. A CA policy with this control on agent identities appears active but generates no enforcement. Only `block` or `sessionControls` are valid for policies targeting `clientApplications.includeAgentIdServicePrincipals`.

5. **Multi-agent trust boundaries:** In multi-agent architectures, an agent can invoke another (orchestrator → sub-agent). If the orchestrating agent is compromised, it can use its permissions to invoke sub-agents with a larger blast radius. The correct governance principle: every agent-to-agent call must be treated as an untrusted call. Each agent needs its own Entra Agent ID — identities cannot be shared — and permissions are not inherited between agents without explicit user authorization.

6. **Tiered Autonomy as a governance configuration:** Without an explicitly assigned tier, all production agents default to "full automation" — the most common gap. For a SOC engineer this means: (1) *Full automation* → analytics rules can execute automatic containment (isolate host, block IP); (2) *Human approval* → the agent generates the recommendation and waits for portal approval before executing; (3) *Human-led* → the agent only presents evidence, the analyst takes all action. When creating Sentinel analytics rules with Logic Apps, the autonomy tier must be an explicit playbook parameter — not a default value.

---

## Background

### The Agent Builder bypass — the most common governance gap

Agent Builder (available in M365 Copilot) lets any licensed user create and publish an agent **immediately**, without passing through the Copilot Studio Requests approval flow. The agent appears in Agent 365 Registry but has no Entra Agent ID, no technical owner, and no DLP policy review. This is the most frequent shadow AI vector in tenants with M365 E5.

### Why `grantControls: mfa` doesn't work for agents

When configuring Conditional Access for agents, `grantControls: {"builtInControls": ["mfa"]}` is **invalid for agent identities** — agents cannot complete interactive MFA. The policy appears to save but creates no enforcement. Only `block` or absence of `grantControls` are valid options. This applies to CA policies targeting `clientApplications.includeAgentIdServicePrincipals`. Documented in [Microsoft Entra CA for workload identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity).

### Entra Agent ID vs. Service Principal

| Property | Service Principal | Entra Agent ID |
|----------|------------------|----------------|
| `agentType` claim | Not present | Present |
| Lifecycle management | Manual | Managed via Agent 365 |
| Appears in Agent 365 Registry | No | Yes |
| CA policy targeting | `includeServicePrincipals` | `includeAgentIdServicePrincipals` |
| Detectable in KQL via | `AppId` | `EntraAgentID` field in `AgentsInfo` |

---

## Lab

### Step 1 — Create an Entra Agent ID for a demo agent

1. In **Entra ID** → **App registrations** → **New registration**
   - Name: `demo-sales-agent`
   - Account type: Single tenant
   - Click **Register**
2. Note the **Application (client) ID** and **Directory (tenant) ID**
3. Go to **Certificates & secrets** → **New client secret** → add a 6-month secret; copy the value
4. Go to **API permissions** → **Add a permission** → **Microsoft Graph** → **Application permissions**
   - Add only: `Sites.Read.All`
   - Click **Grant admin consent**
5. Under **Manifest**, add the following to mark this as an agent identity:

```json
"tags": ["agent365", "EntraAgentID"]
```

6. Save the manifest

**Verify:** Go to **Agent 365 admin center** (M365 Admin Center → Agents → Registry) and confirm `demo-sales-agent` appears.

---

### Step 2 — Enable Copilot Studio approval flow

1. In **Copilot Studio admin center** → **Settings** → **Agent publishing**
2. Enable: **Require admin approval before publishing agents to the organization**
3. Set approvers: add your demo admin account as approver
4. Save

**Test:** In Copilot Studio, attempt to publish a new agent. Verify it enters "Pending approval" status instead of activating immediately.

**Note the gap:** Agents created via **Agent Builder** (M365 Copilot → Copilot → Agent Builder) still activate immediately. This bypass is by design at current product state — document it as a known gap.

---

### Step 3 — Create a Power Platform DLP policy

1. In **Power Platform admin center** → **Policies** → **Data policies** → **New policy**
2. Name: `Agentic AI — Restrict External Connectors`
3. In **Prebuilt connectors**, move to **Blocked**:
   - HTTP (generic)
   - HTTP with Azure AD
   - Any connector classified as "Non-business" that your org doesn't approve
4. Keep in **Business** (approved):
   - SharePoint
   - Microsoft Teams
   - Outlook
5. Apply scope: **All environments** (or specific environment if running isolated demo)
6. Save policy

**Verify:** Attempt to add an HTTP connector to a Power Automate flow in the demo environment. The connector should be blocked.

---

### Step 4 — KQL: Detect agents without Entra Agent ID

```kql
AgentsInfo
| where Timestamp > ago(30d)
| where isempty(EntraAgentID)
| extend OwnersStr = tostring(Owners)
| extend OwnerDisplay = iff(OwnersStr == "" or OwnersStr == "[]", "UNASSIGNED", OwnersStr)
| extend IdentityState = iff(isnotempty(EntraBlueprintID), "BlueprintOnly", "NoEntraIdentity")
| distinct AgentId, Name, Platform, OwnerDisplay, IdentityState, LifecycleStatus, PublishedStatus
| extend RiskNote = iff(IdentityState == "NoEntraIdentity",
    "No Entra identity: no agent identity and no blueprint — identity laundering risk",
    "Blueprint only: no agent identity in this tenant — confirm how the agent authenticates")
| sort by IdentityState desc, Platform asc
```

**Expected output:** List of agents with no agent identity — your identity orphan inventory — each marked `NoEntraIdentity` (neither an agent identity nor a blueprint: identity laundering risk) or `BlueprintOnly` (a blueprint exists but no agent identity in this tenant: confirm how it authenticates). Agents that have an `EntraAgentID` are excluded.

---

### Step 5 — KQL: Copilot Studio agents created, published or shared

> **Not verified on a live tenant (Oct 2026).** `PowerPlatformAdminActivity` exists in the validation workspace, with the columns Learn lists, but has no rows (the Power Platform connectors are not ingesting), so the operation names and the keys inside `Properties` were not seen on live events. The earlier version of this step read `AuditLogs` for `AgentPublished`, an operation that does not exist in Entra audit logs.

> **Where the events are (Microsoft Learn).** Copilot Studio authoring events (`BotCreate`, `BotUpdateOperation-BotPublish`, `BotUpdateOperation-BotShare`) are Power Platform administrator activity in the Purview audit log. In Sentinel they arrive through the **Microsoft Power Platform Admin Activity** connector, table `PowerPlatformAdminActivity`, with the operation in `EventOriginalType`. Learn's sample-queries page for that table still shows the old name `PowerPlatformAdministratorActivity`, which does not resolve.

> **Two paths (Microsoft Learn, July 2026).** An Agent Builder agent reaches other users by sharing, which has no admin review and applies updates at once, or by submission to the organization catalog (Agent Store), which an admin reviews and approves in the Microsoft 365 admin center. Sharing limits set by an admin do not restrict who can add the Agent Store version. The gap in this step is the sharing path.

> **What this step cannot see.** No Copilot Studio event records an approval, so "without approval" cannot be read from these events alone: compare each publish or share with your approval record. An admin approval of an org-catalog submission is `DeployedAgent` in the Microsoft 365 admin center agent management activities (Purview audit log). No audit operation for sharing an Agent Builder agent is documented in the Learn pages reviewed (Oct 2026): after sharing one, search the Purview audit log for the maker and the time, and note the operation name. `CopilotActivity` is not a source for this: its `CopilotAgentManagement` record is Security Copilot agent management (it shares its second with a `CopilotForSecurityTrigger` record) and carries no operation.

```kql
PowerPlatformAdminActivity
| where TimeGenerated > ago(30d)
| where EventOriginalType in (
    "BotCreate",
    "BotUpdateOperation-BotPublish",
    "BotUpdateOperation-BotShare")
| where EventResult == "Succeeded"
| project
    TimeGenerated,
    EventOriginalType,
    ActorName,
    ActorUserType,
    EnvironmentId,
    EventResult,
    Properties
| sort by TimeGenerated desc
```

**Expected output:** one row per Copilot Studio agent creation, publish or share, with the maker (`ActorName`) and the environment: the list to check against your approval process.

---

### Step 6 — KQL: Graph drift — permission grants without approval correlation

> **Not verified (Oct 2026).** The grant side (`Add delegated permission grant`, `Add app role assignment to service principal`) uses real Entra operations. The approval side (`AgentPermissionApproved`) is not confirmed to exist, so as written every grant is reported as "without approval". Use this as an inventory of grants, not as proof of a missing approval. The grant side was run on a Sentinel workspace (Oct 2026): in these events `TargetResources[0]` is the resource that receives the grant and `TargetResources[1]` is the client service principal, and the permission is in the property `DelegatedPermissionGrant.Scope` or `AppRole.Value`, not in `modifiedProperties[0]`.

```kql
AuditLogs
| where TimeGenerated > ago(30d)
| where OperationName in (
    "Add delegated permission grant",
    "Add app role assignment to service principal"
)
| extend ResourceName = tostring(TargetResources[0].displayName)
| extend AgentObjectId = tostring(TargetResources[1].id)
| mv-apply MP = TargetResources[0].modifiedProperties on (
    where tostring(MP.displayName) in ("DelegatedPermissionGrant.Scope", "AppRole.Value")
    | summarize NewPermission = take_any(tostring(MP.newValue)))
| extend GrantedBy = coalesce(tostring(InitiatedBy.user.userPrincipalName), tostring(InitiatedBy.app.displayName))
| join kind=leftouter (
    AuditLogs
    | where OperationName == "AgentPermissionApproved"
    | distinct CorrelationId
) on CorrelationId
| where isempty(CorrelationId1)
| project
    TimeGenerated,
    AgentObjectId,
    ResourceName,
    NewPermission,
    GrantedBy,
    RiskNote = "Permission granted without corresponding approval event"
| sort by TimeGenerated desc
```

**Expected output:** Permission grants to agent identities that have no corresponding approval event — the mechanism behind graph drift.

---

## Playbook Section 2 — Document Your Findings

```markdown
## Section 2: Governance Gap Inventory

### Configuration Deployed
- [ ] Entra Agent ID created for demo agent
- [ ] Copilot Studio approval flow enabled
- [ ] Power Platform DLP policy: Agentic AI — Restrict External Connectors

### Known Gaps Documented
- [ ] Agent Builder bypass: agents activate immediately without approval
  - Affected agents: [LIST]
  - Mitigation: [conditional access policy targeting Agent Builder app ID]

### Governance KQL Queries (add to Sentinel)
- [ ] Agents with no Entra identity, and blueprint-only agents reviewed separately (daily)
- [ ] Copilot Studio agents created, published or shared, checked against approvals (daily)
- [ ] Permission grants without approval correlation (weekly)

### Findings
| Agent | Gap | Risk | Owner |
|-------|-----|------|-------|
| | | | |
```

---

## Closing Questions

- What technical difference did you observe between an agent with `EntraAgentID` field populated vs. one where it is empty? What does that mean for a forensic investigation when you try to attribute an action to a specific agent?
- If you needed to create a Sentinel analytics rule that fires when an agent is published via Agent Builder (bypassing approval), which table would you use and what field would you filter on?

---

## Connection to Module 03

Governance without access control is incomplete. Agents with proper Entra Agent ID still need policies that govern what they can access — and they cannot complete interactive MFA. The next module covers Conditional Access specifically designed for agent identities.

→ [Module 03 — Secure Access](./Module-03-SecureAccess.md)
