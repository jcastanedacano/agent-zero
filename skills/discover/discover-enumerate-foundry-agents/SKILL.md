---
name: discover-enumerate-foundry-agents
version: "1.0"
pillar: discover
subdomain: ms-foundry
description: >-
  Enumerates agents deployed in Azure AI Foundry (active projects and
  endpoints), correlating with Entra ID to detect identities with no
  assigned managed identity or with excessive access to Azure resources.
tags: [discover, foundry, azure-ai, agent-inventory, managed-identity]
atlas_techniques: [AML.T0040, AML.T0056]
d3fend_techniques: [D3-AM, D3-UAP]
nist_ai_rmf: [MAP-1.1, MAP-2.2]
nist_csf: [ID.AM-01, ID.AM-02]
ms_license: [Azure AI Foundry, Azure Subscription]
ms_roles: [Azure AI Developer, Reader (subscription scope)]
effort_hours: 3
---

## When to use

- Complement to `discover-inventory-agents-copilot-studio` to cover the Azure stack
- Before implementing Entra Workload ID controls over Foundry agents
- Managed identity audit across the subscription

## Prerequisites

- Azure CLI authenticated to subscription `{subscription-id}`
- Reader role at subscription or {resource-group} resource group scope
- Az CLI: `az extension add --name ml` (Azure AI Foundry CLI extension)

## Workflow

### Step 1 — List AI Foundry projects in the subscription

```bash
az ml workspace list \
  --subscription {subscription-id} \
  --query "[].{Name:name, RG:resourceGroup, Kind:kind}" \
  --output table
```

Filter by `kind == "Hub"` or `kind == "Project"`.

### Step 2 — List deployments (active agents)

```bash
# For each project identified in Step 1
az ml online-endpoint list \
  --workspace-name {workspace-name} \
  --resource-group {resource-group} \
  --query "[].{Name:name, State:provisioning_state, AuthMode:auth_mode}" \
  --output table
```

`auth_mode: key` = high risk (no Entra ID). `auth_mode: aad_token` = correct.

### Step 3 — Verify managed identity per endpoint

```bash
az resource show \
  --ids "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.MachineLearningServices/workspaces/{ws}/onlineEndpoints/{endpoint}" \
  --query "identity"
```

No `identity` or `type: None` = an endpoint with no managed identity = risk.

### Step 4 — Correlate with Sentinel (Foundry_Agents connector)

Run `queries/sentinel-foundry.kql` to see recent inference activity.

### Step 5 — Risk matrix

| Criterion | High | Medium | Low |
|---|---|---|---|
| Auth mode | key | aad_token without CA | aad_token + CA |
| Managed Identity | Not assigned | System-assigned | User-assigned, specific |
| Data access | Storage/KeyVault | Model only | No external access |

## Verification

- [ ] Complete list of Foundry projects in the subscription
- [ ] Every endpoint has a documented auth_mode
- [ ] Managed identity status per endpoint
- [ ] Endpoints with `auth_mode: key` flagged for remediation

## Implementation notes

- If there are no active Azure AI Foundry projects in the tenant: use synthetic data via Custom Log ingestion to validate the queries before deploying to production
- The Foundry connector in Sentinel must be active for the KQL queries to return data — verify under Data Connectors before creating analytics rules
- Foundry projects inherit permissions from the resource group — review role assignments at the RG level in addition to those on the project
