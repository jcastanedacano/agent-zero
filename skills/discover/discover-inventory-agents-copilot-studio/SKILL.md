---
name: discover-inventory-agents-copilot-studio
version: "1.0"
pillar: discover
subdomain: ms-copilot-studio
description: >-
  Inventories the agents in the tenant from the sources Microsoft Learn documents
  (agent registry and Agent Map in the Microsoft 365 admin center, Power Platform
  inventory, Entra agent identities) and flags the ones that need review: shared by
  their creator, without owner, or unmanaged.
tags: [discover, copilot-studio, shadow-ai, agent-inventory, m365-admin]
atlas_techniques: [AML.T0103]
d3fend_techniques: [D3-AI, D3-AM]
nist_ai_rmf: [GOVERN-1.6, MAP-1.1]
nist_csf: [ID.AM-02, ID.AM-05]
ms_license: [M365 Copilot, M365 E3]
ms_roles: [AI Administrator, Power Platform Administrator]
effort_hours: 4
---

## When to use

- The first step of any AI security assessment
- Unusual agent activity is detected in Power Platform logs
- A prerequisite for the govern and secure skills

Critical gap to document: an agent shared from Agent Builder (M365 Copilot) never goes to the Requests
queue. It appears in the agent registry as **Shared by creator**. The inventory question is therefore not
"Registry minus Requests": Requests holds the submissions that wait for an admin, and the registry also lists
Microsoft, partner-built and organization-published agents. The question is which agents are shared by their
creator, have no owner, or are unmanaged.

## Prerequisites

- Microsoft 365 admin center with the **AI Administrator** role (Global Reader and AI Reader can view the registry)
- Power Platform admin center access: Global, Power Platform or Dynamics 365 administrator see every resource; AI
  Administrator and AI Reader see agents, agentic apps, agent flows and environments only
- Entra ID: permission to read service principals
- An E7 or Agent 365 license for the **Unmanaged agents** count, agent risk signals and the Map usage filters

## Workflow

### Step 1 — Registry and Agent Map in the Microsoft 365 admin center

```
Microsoft 365 admin center → Agents → All agents → Registry
```

Record the counts:
- **Total agents**, and the count per type: Microsoft, External partner-built, **Published by your org**,
  **Shared by creator**
- **Agents without owners**
- **Unmanaged agents** (created or managed outside Agent 365; needs the license above)

The **Agent Map** shows the same agents grouped by platform (Copilot Studio, Agent Builder in Microsoft Copilot,
Microsoft Foundry, SharePoint, Microsoft 365 Agents Toolkit, Amazon Bedrock, other) with filters for status,
publisher type, channel, data source and usage. Export the list to Excel.

The **Requests** tab only shows what waits for approval: note the pending count, but do not subtract it.

`review_set = Shared by creator + Agents without owners + Unmanaged agents`

### Step 2 — Power Platform inventory

```
Power Platform admin center → Manage → Inventory   (or Manage → Copilot Studio)
```

The inventory lists the agents created in Copilot Studio and in Agent Builder, drafts included, with owner,
creation and publication dates, channels, authentication and (preview) the connectors each agent uses. Download
the CSV. Use it to see what the registry does not show (drafts, connector footprint, ownership); a difference with
the registry is not shadow AI by itself.

To script it, query the Power Platform inventory API (token for `https://api.powerplatform.com/`, Power
Platform or Dynamics 365 administrator role) or Azure Resource Graph (resource type
`microsoft.copilotstudio/agents`) (Microsoft Learn, Power Platform inventory).

### Step 3 — Programmatic and identity sources

Registry through Microsoft Graph (preview; permission `CopilotPackages.Read.All`, AI Administrator role):

```http
GET https://graph.microsoft.com/v1.0/copilot/admin/catalog/packages
```

Not run on the validation tenant: the app used there is not granted that permission (403).

Entra agent identities (the identities of agents built on Entra Agent ID):

```http
GET https://graph.microsoft.com/beta/servicePrincipals/microsoft.graph.agentIdentity
  ?$filter=createdDateTime ge 2026-09-06T00:00:00Z
  &$orderby=createdDateTime desc&$count=true
  &$select=displayName,createdDateTime,appId
ConsistencyLevel: eventual
```

Replace the date with 30 days ago. Run on the validation tenant: it lists the agent identities created in the
window. It covers agents with an Entra agent identity, not every agent.

### Step 4 — Classify by risk level

| Criterion | High | Medium | Low |
|---|---|---|---|
| Connectors | SharePoint / Email / CRM | Public data | No connectors |
| Creator | Non-IT user | Power User | IT |
| Distribution | Shared by creator, no owner | Submitted (request pending) | Published by your org (approved) |

### Step 5 — Correlate with Sentinel (if the connectors are active)

Run the queries in `queries/sentinel-inventory.kql`. They read the Power Platform Admin Activity connector
(`PowerPlatformAdminActivity`) and the Microsoft Copilot connector (`CopilotActivity`). KQL Library P01-Q1
(`AgentsInfo`), P01-Q7 (AI applications in use) and P02-Q2 (Copilot Studio agents created, published or shared)
cover the same ground in Defender advanced hunting.

## Verification

- [ ] Agent count per source (registry / Power Platform inventory / Entra agent identities)
- [ ] Review set identified (Shared by creator, without owners, unmanaged)
- [ ] Risk classification per agent
- [ ] Agents with access to sensitive data identified

## Implementation notes

- Activate the **Microsoft Power Platform Admin Activity** and **Microsoft Copilot** connectors in Sentinel so the
  queries return data
- Agents created in Agent Builder do appear in the registry (as **Shared by creator**) and in the Power Platform
  inventory; they do not appear in Requests unless they are submitted to the organization catalog
- Combine this skill with `discover-enumerate-foundry-agents` to cover the full cloud agent landscape
- Removed in this version, because Microsoft Learn (Oct 2026) documents none of them: `Registry_count - Requests_count`
  as a shadow AI count, "Requests: agents that went through approval", "Map: agents with active data connections",
  the path "Settings → Agent 365" and the Power Platform path "Environments → [Env] → Copilot Studio → Agents", and a
  Graph query on the `WindowsAzureActiveDirectoryIntegratedApp` tag (it returns Microsoft enterprise apps: 62 of 1,067
  service principals on the validation tenant, none of them agents)
