---
name: govern-lifecycle-decommission-agent
version: "1.0"
pillar: govern
subdomain: ms-copilot-studio
description: >-
  Gestiona el ciclo de vida completo de agentes AI desde aprobación hasta
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

## Cuándo usar

- Auditoría periódica (mensual/trimestral) de agentes activos
- Cuando un empleado que creó un agente abandona la organización
- Post-proyecto: agentes creados para casos de uso temporales
- Detección de agentes sin actividad en 30+ días con conectores activos

## Prerrequisitos

- Lista de agentes del Pilar 1 (con owner y fecha de creación)
- Power Platform Admin Center accesible
- Graph API para revocar permisos en Entra ID
- Proceso de offboarding que incluya revisión de agentes del empleado

## Workflow

### Paso 1 — Identificar agentes candidatos a descomisión

Criterios:
- Sin actividad en los últimos 30 días (cruzar con KQL en `queries/`)
- Owner/creador fuera de la organización (verificar en Entra)
- Caso de uso original completado (verificar con business owner)
- Proyecto finalizado al que estaba asociado

```kql
// Ver queries/sentinel-inactive-agents.kql
```

### Paso 2 — Notificar a owner y confirmar

Antes de descomisionar, confirmar con:
- Owner directo del agente
- Manager del owner si el owner ya no está en la organización
- Business owner del caso de uso

Plazo de respuesta: 5 días hábiles. Sin respuesta = proceder con descomisión.

### Paso 3 — Deshabilitar agente en Copilot Studio

```
Copilot Studio → [Agent] → Settings → General → Status → Disabled
```

O via Power Platform Admin Center:
```
Environments → [Env] → Copilot Studio → Agents → [Agent] → Disable
```

Mantener deshabilitado 7 días antes de eliminar (ventana de rollback).

### Paso 4 — Revocar OAuth consent grants en Entra ID

```http
# Obtener consent grants del service principal
GET https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/oauth2PermissionGrants

# Revocar cada grant
DELETE https://graph.microsoft.com/v1.0/oauth2PermissionGrants/{grant-id}
```

### Paso 5 — Revocar app role assignments

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/appRoleAssignments

# Por cada assignment:
DELETE https://graph.microsoft.com/v1.0/servicePrincipals/{resource-sp-id}/appRoleAssignedTo/{assignment-id}
```

### Paso 6 — Eliminar service principal y app registration

```http
# Eliminar service principal
DELETE https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}

# Eliminar app registration (si aplica — confirmar que no hay otras instancias)
DELETE https://graph.microsoft.com/v1.0/applications/{app-object-id}
```

### Paso 7 — Documentar en registro de governance

Registrar en log:
- Fecha de descomisión
- Owner notificado
- Motivo
- Recursos revocados
- Ejecutado por

## Verificación

- [ ] Agente en estado Disabled (no Deleted) por 7 días
- [ ] OAuth consent grants revocados (GET retorna array vacío)
- [ ] App role assignments revocados
- [ ] Service principal eliminado (GET retorna 404)
- [ ] Entrada en log de governance creada

## Notas de implementación

- No eliminar SPs de producción durante pruebas — usar agentes de prueba dedicados para validar el proceso de descomisión
- Verificar que el SP no sea compartido con otras aplicaciones antes de eliminarlo: `GET /servicePrincipals/{id}/appRoleAssignedTo` para ver todas las asignaciones
- Graph API `DELETE /servicePrincipals/{id}` elimina el SP inmediatamente — el proceso es irreversible; documentar el estado antes de proceder
