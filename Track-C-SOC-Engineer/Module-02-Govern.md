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

2. **Identity graph drift:** Agents accumulate OAuth permissions over time without review. The signal is in `AuditLogs` under `Add delegated permission grant` without a corresponding `AgentPermissionApproved` event — that absent join is the drift indicator.

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
| distinct AgentId, Name, Platform, OwnerDisplay, LifecycleStatus, PublishedStatus
| extend RiskNote = "Agent operates without dedicated Entra Agent ID — identity laundering risk"
| sort by Platform asc
```

**Expected output:** List of agents running without dedicated identity — your identity orphan inventory.

---

### Step 5 — KQL: Detect agents published without approval

```kql
AuditLogs
| where TimeGenerated > ago(30d)
| where OperationName == "AgentPublished"
| extend AgentSource = tostring(AdditionalDetails["AgentSource"])
| extend ApprovalStatus = tostring(AdditionalDetails["ApprovalStatus"])
| where AgentSource == "AgentBuilder"
    or ApprovalStatus == "Bypassed"
    or isempty(ApprovalStatus)
| project
    TimeGenerated,
    AgentId = tostring(TargetResources[0].id),
    AgentName = tostring(TargetResources[0].displayName),
    PublishedBy = tostring(InitiatedBy.user.userPrincipalName),
    AgentSource,
    ApprovalStatus
| sort by TimeGenerated desc
```

**Expected output:** Agents that activated without passing through the approval flow — the Agent Builder bypass in action.

---

### Step 6 — KQL: Graph drift — permission grants without approval correlation

```kql
AuditLogs
| where TimeGenerated > ago(30d)
| where OperationName in (
    "Add delegated permission grant",
    "Add app role assignment to service principal"
)
| extend AgentObjectId = tostring(TargetResources[0].id)
| extend NewPermission = tostring(TargetResources[0].modifiedProperties[0].newValue)
| extend GrantedBy = tostring(InitiatedBy.user.userPrincipalName)
| join kind=leftouter (
    AuditLogs
    | where OperationName == "AgentPermissionApproved"
    | distinct CorrelationId
) on CorrelationId
| where isempty(CorrelationId1)
| project
    TimeGenerated,
    AgentObjectId,
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
- [ ] Agents without Entra Agent ID (daily)
- [ ] Agents published without approval (daily)
- [ ] Permission grants without approval correlation (weekly)

### Findings
| Agent | Gap | Risk | Owner |
|-------|-----|------|-------|
| | | | |
```

---

## Closing Questions

- What technical difference did you observe between an agent with `EntraAgentId` populated vs. one with `Inherited`? What does that mean for a forensic investigation?
- If you needed to create a Sentinel analytics rule that fires when an agent is published via Agent Builder (bypassing approval), which table would you use and what field would you filter on?

---

## Connection to Module 03

Governance without access control is incomplete. Agents with proper Entra Agent ID still need policies that govern what they can access — and they cannot complete interactive MFA. The next module covers Conditional Access specifically designed for agent identities.

→ [Module 03 — Secure Access](./Module-03-SecureAccess.md)
