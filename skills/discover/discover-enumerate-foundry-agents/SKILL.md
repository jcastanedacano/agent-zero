---
name: discover-enumerate-foundry-agents
version: "1.0"
pillar: discover
subdomain: ms-foundry
description: >-
  Enumera agentes desplegados en Azure AI Foundry (proyectos y endpoints activos)
  correlacionando con Entra ID para detectar identidades sin managed identity
  asignada o con acceso excesivo a recursos Azure.
tags: [discover, foundry, azure-ai, agent-inventory, managed-identity]
atlas_techniques: [AML.T0040, AML.T0056]
d3fend_techniques: [D3-AM, D3-UAP]
nist_ai_rmf: [MAP-1.1, MAP-2.2]
nist_csf: [ID.AM-01, ID.AM-02]
ms_license: [Azure AI Foundry, Azure Subscription]
ms_roles: [Azure AI Developer, Reader (subscription scope)]
effort_hours: 3
---

## Cuándo usar

- Complemento de `discover-inventory-agents-copilot-studio` para cubrir el stack Azure
- Antes de implementar controles de Entra Workload ID sobre agentes Foundry
- Auditoría de managed identities en la suscripción

## Prerrequisitos

- Azure CLI autenticado en subscription `{subscription-id}`
- Rol Reader a nivel de suscripción o RG {resource-group}
- Az CLI: `az extension add --name ml` (Azure AI Foundry CLI extension)

## Workflow

### Paso 1 — Listar proyectos AI Foundry en la suscripción

```bash
az ml workspace list \
  --subscription {subscription-id} \
  --query "[].{Name:name, RG:resourceGroup, Kind:kind}" \
  --output table
```

Filtrar por `kind == "Hub"` o `kind == "Project"`.

### Paso 2 — Listar deployments (agentes activos)

```bash
# Por cada proyecto identificado en Paso 1
az ml online-endpoint list \
  --workspace-name {workspace-name} \
  --resource-group {resource-group} \
  --query "[].{Name:name, State:provisioning_state, AuthMode:auth_mode}" \
  --output table
```

`auth_mode: key` = riesgo alto (sin Entra ID). `auth_mode: aad_token` = correcto.

### Paso 3 — Verificar managed identity por endpoint

```bash
az resource show \
  --ids "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.MachineLearningServices/workspaces/{ws}/onlineEndpoints/{endpoint}" \
  --query "identity"
```

Sin `identity` o `type: None` = endpoint sin identidad gestionada = riesgo.

### Paso 4 — Correlacionar con Sentinel (conector Foundry_Agents)

Ejecutar `queries/sentinel-foundry.kql` para ver actividad de inferencia reciente.

### Paso 5 — Matriz de riesgo

| Criterio | Alto | Medio | Bajo |
|---|---|---|---|
| Auth mode | key | aad_token sin CA | aad_token + CA |
| Managed Identity | Sin asignar | System-assigned | User-assigned específica |
| Acceso a datos | Storage/KeyVault | Solo modelo | Sin acceso externo |

## Verificación

- [ ] Lista completa de proyectos Foundry en la suscripción
- [ ] Todos los endpoints tienen auth_mode documentado
- [ ] Managed identity status por endpoint
- [ ] Endpoints con `auth_mode: key` marcados para remediación

## Notas de implementación

- Si no hay proyectos de Azure AI Foundry activos en el tenant: usar datos sintéticos via Custom Log ingestion para validar las queries antes de desplegar en producción
- El conector de Foundry en Sentinel debe estar activo para que las queries KQL retornen datos — verificar en Data Connectors antes de crear analytics rules
- Los proyectos de Foundry heredan permisos del resource group — revisar los role assignments a nivel de RG además de los del proyecto
