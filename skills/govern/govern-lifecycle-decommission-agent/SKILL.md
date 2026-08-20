---
name: govern-lifecycle-decommission-agent
version: "1.0"
pillar: govern
subdomain: ms-copilot-studio
description: >-
  Manages the full lifecycle of AI agents from approval through
  descomisión, incluyendo detección de agentes huérfanos con acceso activo,
  revocación de permisos y eliminación de service principals en Entra ID.
tags: [govern, copilot-studio, entra, lifecycle, decommission, agent-hygiene]
atlas_techniques: [AML.T0040]
d3fend_techniques: [D3-UAP, D3-AM]
nist_ai_rmf: [GOVERN-1.4, MANAGE-4.1]
nist_csf: [PR.AA-01, ID.AM-01]
ms_license: [M365 E3, Power Platform]
ms_roles: [Power Platform Administrator, Application Administrator]
effort_hours: 4
---

## When to use

- Auditoría periódica (mensual/trimestral) de agentes activos
- Cuando un empleado que creó un agente abandona la organización
- Post-proyecto: agentes creados para casos de uso temporales
- Detección de agentes sin actividad en 30+ días con conectores activos

## Prerequisites

- Lista de agentes del Pilar 1 (con owner y fecha de creación)
- Power Platform Admin Center accesible
- Graph API para revocar permisos en Entra ID
- Proceso de offboarding que incluya revisión de agentes del empleado

## Workflow

### Step 1 — Identificar agentes candidatos a descomisión

Criterios:
- Sin actividad en los últimos 30 días (cruzar con KQL en `queries/`)
- Owner/creador fuera de la organización (verificar en Entra)
- Caso de uso original completado (verificar con business owner)
- Proyecto finalizado al que estaba asociado

```kql
// Ver queries/sentinel-inactive-agents.kql
```

### Step 2 — Notificar a owner y confirmar

Antes de descomisionar, confirmar con:
- Owner directo del agente
- The owner manager if the owner is no longer with the organization
- Business owner del caso de uso

Plazo de respuesta: 5 días hábiles. Sin respuesta = proceder con descomisión.

### Step 3 — Deshabilitar agente en Copilot Studio

```
Copilot Studio → [Agent] → Settings → General → Status → Disabled
```

O via Power Platform Admin Center:
```
Environments → [Env] → Copilot Studio → Agents → [Agent] → Disable
```

Mantener deshabilitado 7 días antes de eliminar (ventana de rollback).

### Step 4 — Revocar OAuth consent grants en Entra ID

```http
# Obtener consent grants del service principal
GET https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/oauth2PermissionGrants

# Revocar cada grant
DELETE https://graph.microsoft.com/v1.0/oauth2PermissionGrants/{grant-id}
```

### Step 5 — Revocar app role assignments

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/appRoleAssignments

# Por cada assignment:
DELETE https://graph.microsoft.com/v1.0/servicePrincipals/{resource-sp-id}/appRoleAssignedTo/{assignment-id}
```

### Step 6 — Eliminar service principal y app registration

```http
# Eliminar service principal
DELETE https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}

# Eliminar app registration (si aplica — confirmar que no hay otras instancias)
DELETE https://graph.microsoft.com/v1.0/applications/{app-object-id}
```

### Step 7 — Documentar en registro de governance

Registrar en log:
- Fecha de descomisión
- Owner notificado
- Motivo
- Recursos revocados
- Ejecutado por

## Verification

- [ ] Agente en estado Disabled (no Deleted) por 7 días
- [ ] OAuth consent grants revocados (GET retorna array vacío)
- [ ] App role assignments revocados
- [ ] Service principal eliminado (GET retorna 404)
- [ ] Entrada en log de governance creada

## Implementation notes

- Do not delete production SPs during testing — use dedicated test agents to validate the decommission process
- Verify the SP is not shared with other applications before deleting it: `GET /servicePrincipals/{id}/appRoleAssignedTo` to see all assignments
- Graph API `DELETE /servicePrincipals/{id}` deletes the SP immediately — the process is irreversible; document state before proceeding
