---
name: govern-agent365-approval-flow
version: "1.0"
pillar: govern
subdomain: ms-copilot-studio
description: >-
  Configures and operates the AI agent approval flow in Agent 365 (M365 Admin
  Center), establishing policies so new agents go through Requests
  before activation, closing the Agent Builder gap that activates agents without approval.
tags: [govern, copilot-studio, agent365, approval-flow, shadow-ai-prevention]
atlas_techniques: [AML.T0054]
d3fend_techniques: [D3-UAP, D3-SFA]
nist_ai_rmf: [GOVERN-1.2, GOVERN-2.1]
nist_csf: [GV-PO-01, PR.AA-05]
ms_license: [M365 Copilot, M365 E3]
ms_roles: [Microsoft 365 Administrator, Teams Administrator]
effort_hours: 6
---

## When to use

- After identifying shadow AI in Pillar 1 (the Registry vs Requests gap)
- When the tenant has no formal agent approval process
- As a preventive control before Agent Builder usage proliferates

## Critical gap to close

Agents created from **Agent Builder** (inside M365 Copilot) are activated
immediately without generating a Request in Agent 365. This is the primary vector
for shadow AI in organizations with M365 Copilot.

The Requests flow applies to agents created directly in Copilot Studio,
not to those from Agent Builder. Both channels require different controls.

## Prerequisites

- M365 Admin Center with administrator role
- Agent 365 enabled in the tenant
- An organizational decision: mandatory approval policy or post-hoc review?

## Workflow

### Step 1 — Configure the agent policy in Agent 365

```
M365 Admin Center → Settings → Agent 365 → Policies
```

Available options:
- **Allow all agents**: no control (default)
- **Block all agents**: full block
- **Allow specific agents**: allowlist
- **Require admin approval**: enables the Requests flow

Select **Require admin approval** for effective control.

### Step 2 — Configure the Requests workflow

```
Agent 365 → Requests → Settings
```

Define:
- **Approvers**: the IT/Security team's security group
- **Auto-approve criteria**: agents with no external connectors (low risk)
- **Notification settings**: email to approvers when a Request is received

### Step 3 — Close the Agent Builder gap

The Agent Builder bypass cannot be closed from within Agent 365. Alternative controls:

**Option A — Power Platform DLP Policy** (recommended):
```
Power Platform Admin Center → Policies → Data policies
→ Create a policy restricting connectors in production environments
→ Assign it to environments where M365 Copilot operates
```

**Option B — Conditional Access on M365 Copilot**:
Block Agent Builder for users not in the approved AI Builders group:
```
CA policy → Cloud apps: Microsoft Copilot →
  Exclude: AI-Builders-Approved-Group
  Grant: block
```

**Option C — License restriction**:
Assign the M365 Copilot license only to users going through formal approval.

### Step 4 — Operational approval process

Flow for each Request received:

1. Review the agent's name and description
2. Verify the creator (department, role)
3. Review requested connectors (cross-reference with the `discover-classify-agent-connectors` skill)
4. Assess accessible data by sensitivity category
5. Approve with conditions or reject with documented justification
6. Record the decision in the governance log (SharePoint list or custom table)

### Step 5 — Monthly audit

Review the **Registry** vs **Requests** tabs monthly to detect agents that
bypassed the process. Any discrepancy = a shadow AI incident.

## Verification

- [ ] "Require admin approval" policy enabled in Agent 365
- [ ] Approver group defined and notifications active
- [ ] At least one control for the Agent Builder gap implemented (A, B, or C)
- [ ] Operational process documented in a runbook
- [ ] Monthly audit scheduled

## Implementation notes

- Verify Agent 365 is configured in the tenant before enabling the approval flow — the central registry is not active by default
- To demonstrate the Agent Builder bypass gap: create an agent via Agent Builder and compare its state in Agent 365 Registry vs. Copilot Studio Requests
- Power Platform DLP is the most effective compensating control for mitigating the Agent Builder bypass in enterprise environments where you cannot restrict it directly
