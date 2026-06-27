---
name: govern-foundry-rbac
version: "1.0"
pillar: govern
subdomain: ms-foundry
description: >-
  Configura RBAC y controles a nivel de API en Azure AI Foundry para limitar
  qué modelos, conexiones y herramientas puede usar cada agente, implementando
  el principio de least privilege en el plano de control de Foundry.
tags: [govern, foundry, rbac, api-controls, least-privilege, azure-ai]
atlas_techniques: [AML.T0012, AML.T0040, AML.T0056]
d3fend_techniques: [D3-MAN, D3-UAP]
nist_ai_rmf: [GOVERN-2.1, GOVERN-4.2, MAP-1.5]
nist_csf: [PR.AA-04, PR.AC-04, PR.AC-06]
ms_license: [Azure AI Foundry, Azure subscription]
ms_roles: [Azure AI Developer, Cognitive Services Contributor]
effort_hours: 3
---

## Cuándo usar

- Al configurar un proyecto de Azure AI Foundry para un agente nuevo
- Cuando múltiples agentes comparten un proyecto y necesitan permisos diferenciados
- Para auditar qué conexiones externas (APIs, búsqueda) tiene disponibles cada agente
- Como parte del proceso de governance review periódico del pilar 02

## Prerrequisitos

- Azure subscription con acceso a Azure AI Foundry
- Rol Owner o User Access Administrator en el resource group del proyecto Foundry
- Proyecto de Azure AI Foundry existente con al menos un agente desplegado
- Azure CLI o acceso a Azure Portal

## Arquitectura RBAC de Foundry

| Rol | Scope | Acceso |
|-----|-------|--------|
| `Azure AI Foundry Owner` | Hub | Gestión completa del hub y todos los proyectos |
| `Azure AI Foundry Contributor` | Hub o Proyecto | Crear y gestionar recursos, sin asignar roles |
| `Azure AI Developer` | Proyecto | Desplegar modelos, crear agentes, usar conexiones |
| `Azure AI Inference Deployment Operator` | Proyecto | Solo deployment de inferencia, sin acceso a datos |

## Workflow

### Paso 1 — Auditar roles actuales en el proyecto Foundry

```bash
az role assignment list \
  --scope /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.MachineLearningServices/workspaces/{project-name} \
  --output table \
  --query "[].{Principal:principalName, Role:roleDefinitionName, Type:principalType}"
```

Identificar:
- Service principals de agentes con roles más amplios de lo necesario
- Usuarios con `Contributor` que solo necesitan `Azure AI Developer`
- Identidades con roles a nivel de Hub que solo deberían tenerlos a nivel de Proyecto

### Paso 2 — Restringir conexiones disponibles por proyecto

En **Azure AI Foundry** → **Project** → **Settings** → **Connections**:

Para cada conexión existente (Azure OpenAI, AI Search, storage, APIs externas):

```bash
# Ver conexiones del proyecto
az ml connection list --workspace-name {project-name} --resource-group {rg} --output table

# Eliminar una conexión no autorizada
az ml connection delete --name {connection-name} --workspace-name {project-name} --resource-group {rg}
```

Principio: cada agente debe tener acceso solo a las conexiones que su función requiere.

### Paso 3 — Configurar controles a nivel de API (API-level controls)

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

### Paso 4 — Aplicar least privilege a la managed identity del agente

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

### Paso 5 — KQL: Monitorear acceso a Foundry en Sentinel

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

## Verificación

- [ ] Auditoría de roles completada — service principals sin roles excesivos
- [ ] Conexiones de proyectos revisadas — solo conexiones autorizadas por agente
- [ ] Managed identity del agente con rol mínimo necesario (`Inference Deployment Operator`)
- [ ] KQL de monitoreo de actividad Foundry corriendo en Sentinel
- [ ] Findings incorporados a la sección "Domain 2" del Gap Assessment Template

## Notas de implementación

- Los roles de Azure AI Foundry heredan de Azure RBAC — un usuario con `Contributor` a nivel de resource group tiene acceso implícito a todos los proyectos Foundry en ese RG; usar scopes específicos de proyecto
- Las conexiones de Foundry (especialmente a APIs externas y storage) son un vector de exfiltración — auditarlas con la misma prioridad que los permisos de Graph API
- Combinar con `secure-managed-identity-foundry` para el modelo completo: RBAC en Foundry + managed identity en lugar de secrets
- Azure AI Foundry evoluciona rápidamente — validar los nombres de roles y comandos CLI contra la documentación oficial antes de documentarlos en runbooks de producción
