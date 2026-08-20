---
name: govern-foundry-rbac
version: "1.0"
pillar: govern
subdomain: ms-foundry
description: >-
  Configura RBAC y controles a nivel de API en Azure AI Foundry para limitar
  qué modelos, conexiones y herramientas puede usar cada agente, implementando
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
- Cuando múltiples agentes comparten un proyecto y necesitan permisos diferenciados
- Para auditar qué conexiones externas (APIs, búsqueda) tiene disponibles cada agente
- Como parte del proceso de governance review periódico del pilar 02

## Prerequisites

- Azure subscription con acceso a Azure AI Foundry
- Owner or User Access Administrator role on the Foundry project resource group
- An existing Azure AI Foundry project with at least one deployed agent
- Azure CLI o acceso a Azure Portal

## Arquitectura RBAC de Foundry

| Rol | Scope | Acceso |
|-----|-------|--------|
| `Azure AI Foundry Owner` | Hub | Full management of the hub and all projects |
| `Azure AI Foundry Contributor` | Hub o Proyecto | Crear y gestionar recursos, sin asignar roles |
| `Azure AI Developer` | Proyecto | Desplegar modelos, crear agentes, usar conexiones |
| `Azure AI Inference Deployment Operator` | Project | Inference deployment only, no data access |

## Workflow

### Step 1 — Auditar roles actuales en el proyecto Foundry

```bash
az role assignment list \
  --scope /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.MachineLearningServices/workspaces/{project-name} \
  --output table \
  --query "[].{Principal:principalName, Role:roleDefinitionName, Type:principalType}"
```

Identificar:
- Service principals de agentes con roles más amplios de lo necesario
- Usuarios con `Contributor` que solo necesitan `Azure AI Developer`
- Identities holding Hub-level roles that should only hold them at Project level

### Step 2 — Restringir conexiones disponibles por proyecto

En **Azure AI Foundry** → **Project** → **Settings** → **Connections**:

Para cada conexión existente (Azure OpenAI, AI Search, storage, APIs externas):

```bash
# Ver conexiones del proyecto
az ml connection list --workspace-name {project-name} --resource-group {rg} --output table

# Eliminar una conexión no autorizada
az ml connection delete --name {connection-name} --workspace-name {project-name} --resource-group {rg}
```

Principle: each agent should only have access to the connections its function requires.

### Step 3 — Configurar controles a nivel de API (API-level controls)

En **Foundry** → **Project** → **Deployments**, para cada deployment de modelo:

```bash
# Asignar deployment específico a un agente (least privilege de modelo)
az ml online-deployment update \
  --name {deployment-name} \
  --endpoint-name {endpoint-name} \
  --workspace-name {project-name} \
  --resource-group {rg} \
  --set tags.authorized_agents="{agent-id-1},{agent-id-2}"
```

### Step 4 — Aplicar least privilege a la managed identity del agente

```bash
# Remover rol amplio
az role assignment delete \
  --assignee {managed-identity-principal-id} \
  --role "Azure AI Developer" \
  --scope /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.MachineLearningServices/workspaces/{project}

# Asignar rol mínimo necesario
az role assignment create \
  --assignee {managed-identity-principal-id} \
  --role "Azure AI Inference Deployment Operator" \
  --scope /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.MachineLearningServices/workspaces/{project}/onlineEndpoints/{endpoint}
```

### Step 5 — KQL: Monitorear acceso a Foundry en Sentinel

```kql
// Ver queries/sentinel-foundry.kql
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

- [ ] Auditoría de roles completada — service principals sin roles excesivos
- [ ] Conexiones de proyectos revisadas — solo conexiones autorizadas por agente
- [ ] Managed identity del agente con rol mínimo necesario (`Inference Deployment Operator`)
- [ ] KQL de monitoreo de actividad Foundry corriendo en Sentinel
- [ ] Findings incorporados a la sección "Domain 2" del Gap Assessment Template

## Implementation notes

- Azure AI Foundry roles inherit from Azure RBAC — a user with `Contributor` at resource group level has implicit access to every Foundry project
- Foundry connections (especially to external APIs and storage) are an exfiltration vector — audit them with the same priority as Graph permissions
- Combine with `secure-managed-identity-foundry` for the complete model: RBAC in Foundry plus managed identity instead of secrets
- Azure AI Foundry evoluciona rápidamente — validar los nombres de roles y comandos CLI contra la documentación oficial antes de documentarlos en runbooks de producción
