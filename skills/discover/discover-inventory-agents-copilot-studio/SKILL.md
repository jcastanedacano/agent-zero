---
name: discover-inventory-agents-copilot-studio
version: "1.0"
pillar: discover
subdomain: ms-copilot-studio
description: >-
  Enumerates all active agents in Copilot Studio and Agent 365, detecting
  agents created without IT approval (Agent Builder bypassing the Requests
  flow) which represent the central shadow AI gap in M365.
tags: [discover, copilot-studio, shadow-ai, agent-inventory, m365-admin]
atlas_techniques: [AML.T0054, AML.T0051]
d3fend_techniques: [D3-AM, D3-SFA]
nist_ai_rmf: [MAP-1.1, GOVERN-1.2]
nist_csf: [ID.AM-01, GV-OC-01]
ms_license: [M365 Copilot, M365 E3]
ms_roles: [Microsoft 365 Administrator, Power Platform Administrator]
effort_hours: 4
---

## When to use

- The first step of any AI security assessment
- Unusual agent activity is detected in Power Platform logs
- A prerequisite for the govern and secure skills

Critical gap to document: agents created from Agent Builder (M365 Copilot)
are activated immediately without going through the Requests flow in Agent 365.
Registry and Map in Agent 365 show agents; Requests only shows the approved ones.
That difference is shadow AI.

## Prerequisites

- M365 Admin Center with administrator role
- Power Platform Admin Center access
- Agent 365 enabled (Registry / Map / Requests tabs visible)
- Entra ID: permissions to query service principals

## Workflow

### Step 1 — Agent 365 in M365 Admin Center

```
M365 Admin Center → Settings → Agent 365
```

Review the three tabs and record the counts:
- **Registry**: total registered agents
- **Map**: agents with active data connections
- **Requests**: agents that went through approval

`shadow_ai_count = Registry_count - Requests_count`

### Step 2 — Power Platform Admin Center

```
Power Platform Admin Center → Environments → [Env] → Copilot Studio → Agents
```

Export the full list. Compare displayName against Registry.
Agents present in PP Admin but absent from Requests = confirmed shadow AI.

### Step 3 — Microsoft Graph API

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals
  ?$filter=tags/any(t:t eq 'WindowsAzureActiveDirectoryIntegratedApp')
  &$select=displayName,appId,createdDateTime,tags
  &$orderby=createdDateTime desc
```

Filter for those created in the last 30 days to detect new unreported agents.

### Step 4 — Classify by risk level

| Criterion | High | Medium | Low |
|---|---|---|---|
| Connectors | SharePoint / Email / CRM | Public data | No connectors |
| Creator | Non-IT user | Power User | IT |
| Approval | No Requests | Requests pending | Approved |

### Step 5 — Correlate with Sentinel (if the connector is active)

Run the queries in `queries/sentinel-inventory.kql`.

## Verification

- [ ] Agent count per source (Agent 365 / PP Admin / Graph)
- [ ] Shadow AI count calculated (Registry - Requests)
- [ ] Risk classification per agent
- [ ] Agents with access to sensitive data identified

## Implementation notes

- Activate the Copilot Studio connector in Sentinel so inventory queries return data in real time
- Agents created via Agent Builder (M365 Copilot) do not appear in Copilot Studio Requests — always verify directly in the Power Platform admin center
- Combine this skill with `discover-enumerate-foundry-agents` to cover the full cloud agent landscape
