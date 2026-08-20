---
name: govern-foundry-rbac
version: "1.0"
pillar: govern
subdomain: ms-foundry
description: >-
  Configures RBAC and API-level controls in Azure AI Foundry to limit which
  models, connections, and tools each agent can use, implementing
  the least privilege principle in the Foundry control plane.
tags: [govern, foundry, rbac, api-controls, least-privilege, azure-ai]
atlas_techniques: [AML.T0012, AML.T0040, AML.T0056]
d3fend_techniques: [D3-MAN, D3-UAP]
nist_ai_rmf: [GOVERN-2.1, GOVERN-4.2, MAP-1.5]
nist_csf: [PR.AA-04, PR.AC-04, PR.AC-06]
ms_license: [Azure AI Foundry, Azure subscription]
ms_roles: [Azure AI Developer, Cognitive Services Contributor]
effort_hours: 3
---

## When to use

- When configuring an Azure AI Foundry project for a new agent
- When multiple agents share a project and need differentiated permissions
- To audit which external connections (APIs, search) each agent has available
- As part of the periodic governance review process in Pillar 02

## Prerequisites

- Azure subscription with access to Azure AI Foundry
- Owner or User Access Administrator role on the Foundry project resource group
- An existing Azure AI Foundry project with at least one deployed agent
- Azure CLI or Azure Portal access

## Foundry RBAC architecture

| Role | Scope | Access |
|-----|-------|--------|
| `Azure AI Foundry Owner` | Hub | Full management of the hub and all projects |
| `Azure AI Foundry Contributor` | Hub or Project | Create and manage resources, cannot assign roles |
| `Azure AI Developer` | Project | Deploy models, create agents, use connections |
| `Azure AI Inference Deployment Operator` | Project | Inference deployment only, no data access |

## Workflow

### Step 1 — Audit current roles in the Foundry project

```bash
az role assignment list \
  --scope /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.MachineLearningServices/workspaces/{project-name} \
  --output table \
  --query "[].{Principal:principalName, Role:roleDefinitionName, Type:principalType}"
```

Identify:
- Agent service principals with broader roles than necessary
- Users with `Contributor` who only need `Azure AI Developer`
- Identities holding Hub-level roles that should only hold them at Project level

### Step 2 — Restrict available connections per project

In **Azure AI Foundry** → **Project** → **Settings** → **Connections**:

For each existing connection (Azure OpenAI, AI Search, storage, external APIs):

```bash
# List the project's connections
az ml connection list --workspace-name {project-name} --resource-group {rg} --output table

# Delete an unauthorized connection
az ml connection delete --name {connection-name} --workspace-name {project-name} --resource-group {rg}
```

Principle: each agent should only have access to the connections its function requires.

### Step 3 — Configure API-level controls

In **Foundry** → **Project** → **Deployments**, for each model deployment:

```bash
# Assign a specific deployment to an agent (model-level least privilege)
az ml online-deployment update \
  --name {deployment-name} \
  --endpoint-name {endpoint-name} \
  --workspace-name {project-name} \
  --resource-group {rg} \
  --set tags.authorized_agents="{agent-id-1},{agent-id-2}"
```

### Step 4 — Apply least privilege to the agent's managed identity

```bash
# Remove the broad role
az role assignment delete \
  --assignee {managed-identity-principal-id} \
  --role "Azure AI Developer" \
  --scope /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.MachineLearningServices/workspaces/{project}

# Assign the minimum required role
az role assignment create \
  --assignee {managed-identity-principal-id} \
  --role "Azure AI Inference Deployment Operator" \
  --scope /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.MachineLearningServices/workspaces/{project}/onlineEndpoints/{endpoint}
```

### Step 5 — KQL: monitor Foundry access in Sentinel

```kql
// See queries/sentinel-foundry.kql
AzureActivity
| where TimeGenerated > ago(30d)
| where ResourceProviderValue == "MICROSOFT.MACHINELEARNINGSERVICES"
| where OperationNameValue has_any ("deployments", "endpoints", "connections")
| extend AgentId = tostring(Properties["agentId"])
| summarize
    OperationCount = count(),
    Operations = make_set(OperationNameValue, 10),
    LastActivity = max(TimeGenerated)
    by CallerIpAddress, Caller, ResourceId
| sort by OperationCount desc
```

## Verification

- [ ] Role audit completed — service principals hold no excessive roles
- [ ] Project connections reviewed — only agent-authorized connections remain
- [ ] Agent managed identity holds the minimum required role (`Inference Deployment Operator`)
- [ ] Foundry activity monitoring KQL running in Sentinel
- [ ] Findings incorporated into the "Domain 2" section of the Gap Assessment Template

## Implementation notes

- Azure AI Foundry roles inherit from Azure RBAC — a user with `Contributor` at resource group level has implicit access to every Foundry project
- Foundry connections (especially to external APIs and storage) are an exfiltration vector — audit them with the same priority as Graph permissions
- Combine with `secure-managed-identity-foundry` for the complete model: RBAC in Foundry plus managed identity instead of secrets
- Azure AI Foundry evolves rapidly — validate role names and CLI commands against official documentation before writing them into production runbooks
