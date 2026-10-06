---
name: govern-agent365-approval-flow
version: "1.0"
pillar: govern
subdomain: ms-copilot-studio
description: >-
  Operates the admin approval queue for agents in the Microsoft 365 admin center
  (Agents > All agents > Requests) and closes the Agent Builder sharing path with
  the controls Microsoft Learn documents: who can share agents, blocking agents, and
  who can access agents.
tags: [govern, copilot-studio, agent365, approval-flow, shadow-ai-prevention]
atlas_techniques: [AML.T0103]
d3fend_techniques: [D3-UAP, D3-SFA]
nist_ai_rmf: [GOVERN-1.2, GOVERN-2.1]
nist_csf: [GV-PO-01, PR.AA-05]
ms_license: [M365 Copilot, M365 E3]
ms_roles: [AI Administrator, Global Administrator]
effort_hours: 6
---

## When to use

- After identifying shadow AI in Pillar 1 (agents in the registry that nobody reviewed)
- When the tenant has no formal agent approval process
- As a preventive control before Agent Builder usage proliferates

## Critical gap to close

An Agent Builder agent reaches other users by two paths (Microsoft Learn, Agent Builder, Oct 2026):

- **Sharing.** By default every user can share an agent with the whole organization, with no admin
  review, and updates apply at once. The shared agent shows in the agent registry as **Shared by
  creator**. An admin can restrict who can share (all users by default, specific users or groups,
  or no users). When sharing is restricted, an admin must approve and deploy the agent before others can
  use it. The restriction applies to new sharing actions: agents already shared stay accessible until
  their owner changes the sharing settings. Sharing limits set by an admin apply only to the shared
  version, not to the Agent Store version.
- **Organization catalog.** Submitting the agent to the organization catalog (Agent Store) sends it to an
  admin review in the Microsoft 365 admin center.

The **Requests** queue (Agents > All agents > Requests) holds agents submitted for admin approval: agents
published from Copilot Studio, and agents from Microsoft Foundry or the Microsoft 365 Agents Toolkit that are
submitted for approval. Sharing never creates a request. The gap this skill closes is the sharing path, and it is a
configurable control, not a fixed product limit.

## Prerequisites

- Microsoft 365 admin center with the **AI Administrator** or **Global Administrator** role: only these two
  can approve requests and manage agent configurations (Global Reader and AI Reader are read-only; Microsoft
  Learn, agent management roles and permissions)
- An organizational decision: restrict sharing now, or review shared agents after the fact?
- Agent risk signals and the unmanaged-agents count in the registry need an E7 or Agent 365 license (Microsoft
  Learn); the controls below do not depend on them

## Workflow

### Step 1 — Decide who can access agents

```
Microsoft 365 admin center → Copilot → Settings → Data access → Agents
```

- Who can access agents: **All users**, **No users** or **Specific users/groups**
- Which types are available: agents created by Microsoft, by external publishers and by your organization

Select the narrowest option your organization accepts and save. This controls access to agents, not who can
share or publish them (Step 3).

### Step 2 — Operate the Requests queue

```
Microsoft 365 admin center → Agents → All agents → Requests
```

1. Filter by state: **Pending review**, **Pending update** or **Pending activate**
2. Open the request and check the agent's description, owner, data sources and the tools and custom actions
   it can invoke
3. **Publish to store** (the wizard sets the users or groups, the protection policy and the permissions) or
   **Reject submission**

The approval authority comes from the role (AI Administrator or Global Administrator). Approver groups,
auto-approve criteria and notification settings are not documented in the Learn pages reviewed (Oct 2026):
confirm them in your tenant before relying on them, and define the review cadence yourself.

### Step 3 — Close the Agent Builder sharing path

**Option A — Restrict who can share agents** (the direct control). In the Microsoft 365 admin center, set who can
share agents with the organization: all users (default), specific users or groups, or no users (Microsoft Learn,
Agent Builder, "Governance and admin controls"). With sharing restricted, an admin must approve and deploy the
agent before others can use it. Learn does not name the exact menu: find it in the Copilot controls for agents.

**Option B — Block an agent.** Agents > All agents > select the agent > **Block**. For Agent Builder and Copilot
Studio agents it removes the agent from Copilot and from other host products such as Outlook and Teams.

**Option C — Limit who can create agents.** Agent Builder is available to users with a Microsoft 365 Copilot
license, or in tenants with pay-as-you-go enabled for Copilot Studio. In a pay-as-you-go tenant it is available
without that license, so license assignment alone does not restrict it.

**Option D — Power Platform DLP policy** (for Copilot Studio agents):
```
Power Platform Admin Center → Policies → Data policies
-> Create a policy restricting connectors in production environments
-> Assign it to the environments where Copilot Studio agents are built
```
The Learn pages reviewed do not say that a Power Platform DLP policy covers Agent Builder agents.

### Step 4 — Operational approval process

Flow for each request received:

1. Review the agent's name, description and owner
2. Verify the creator (department, role)
3. Review the connectors and tools it can invoke (cross-reference with the `discover-classify-agent-connectors` skill)
4. Assess accessible data by sensitivity category
5. Publish with the narrowest audience and a policy template, or reject with documented justification
6. Record the decision in the governance log (SharePoint list or custom table)

### Step 5 — Monthly review of the registry

```
Microsoft 365 admin center → Agents → All agents → Registry
```

Filter by agent type **Shared by creator** (agents shared without a request), open the **Agents without owners**
card and, with an Agent 365 license, **Unmanaged agents**. A shared agent is not a process violation by itself: it
is the sharing path. Compare each one with your sharing policy and decide to keep it, require a catalog
submission, or block it.

For Copilot Studio, KQL Library P02-Q2 lists who created, published or shared agents (not verified: its table
has no rows on the validation workspace). No audit operation for sharing an Agent Builder agent is documented,
so there is no sharing alert to build: review the registry, and check the agent in use in `CopilotActivity`
(`AgentName`, `AgentId`).

## Verification

- [ ] Who can access agents is set in the Copilot controls
- [ ] The Requests queue is reviewed by AI Administrator or Global Administrator role holders, with a defined cadence
- [ ] Sharing is restricted (Option A), or leaving it open is a documented decision
- [ ] Operational process documented in a runbook
- [ ] Monthly registry review scheduled

## Implementation notes

- To demonstrate the sharing path: create an agent in Agent Builder, share it with the organization, and compare
  the registry (type **Shared by creator**) with the Requests queue (nothing there)
- Power Platform DLP complements the controls for Copilot Studio agents; it is not the control for Agent Builder
- Removed in this version, because Microsoft Learn (Oct 2026) documents none of them: a tenant policy named
  "Require admin approval" under Agent 365 settings, an approver group with auto-approve criteria, and a
  Conditional Access policy that targets Agent Builder (Conditional Access documents "Office 365" and "All
  resources" as targets, which would block Copilot as a whole, not agent creation)
