---
name: discover-shadow-ai-entra-principals
version: "1.0"
pillar: discover
subdomain: ms-entra
description: >-
  Detecta service principals en Entra ID creados por agentes AI o aplicaciones
  de AI no documentadas, identificando OAuth consent grants excesivos y
  aplicaciones con permisos Graph API sensibles sin revisión de seguridad.
tags: [discover, entra, shadow-ai, service-principal, oauth, graph-permissions]
atlas_techniques: [AML.T0056, AML.T0040]
d3fend_techniques: [D3-UAP, D3-SFA]
nist_ai_rmf: [MAP-1.1, GOVERN-2.1]
nist_csf: [ID.AM-02, PR.AA-01]
ms_license: [Microsoft Entra ID P1]
ms_roles: [Application Administrator, Security Reader]
effort_hours: 3
---

## Cuándo usar

- Post inventario de Copilot Studio y Foundry — para detectar surface no cubierto
- Cuando hay reportes de aplicaciones OAuth no reconocidas en Sign-in logs
- Auditoría periódica de permisos Graph API en el tenant

## Prerrequisitos

- Microsoft Graph API accesible (Lokka-Microsoft MCP o Graph Explorer)
- Rol Application Administrator o superior
- Entra ID P1 para acceso a sign-in logs completos

## Workflow

### Paso 1 — Service principals creados recientemente

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals
  ?$filter=createdDateTime ge {fecha-30d}
  &$select=displayName,appId,createdDateTime,tags,servicePrincipalType
  &$orderby=createdDateTime desc
```

Filtrar `servicePrincipalType != "ManagedIdentity"` para ver aplicaciones externas.

### Paso 2 — Permisos OAuth2 con acceso sensible

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals/{id}/oauth2PermissionGrants
```

Permisos de riesgo alto a buscar:
- `Mail.ReadWrite`, `Mail.Send` — acceso a email
- `Files.ReadWrite.All` — acceso a SharePoint/OneDrive
- `Calendars.ReadWrite` — acceso a calendarios
- `Directory.ReadWrite.All` — acceso al directorio

### Paso 3 — App role assignments (permisos de aplicación, no delegados)

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals/{id}/appRoleAssignments
```

App roles (sin usuario) son más peligrosos que delegated — el agente actúa solo.

### Paso 4 — Cruzar con AuditLogs en Sentinel

```kql
// Ver queries/sentinel-shadow-principals.kql
```

### Paso 5 — Clasificar por nivel de riesgo

| Condición | Acción recomendada |
|---|---|
| SP con `Mail.ReadWrite` + creado por usuario no IT | Revocar inmediatamente |
| SP con `Files.ReadWrite.All` sin owner documentado | Revisar y documentar |
| SP sin actividad en 30 días con permisos activos | Candidato a descomisión |

## Verificación

- [ ] Lista de SPs creados en últimos 30/60/90 días
- [ ] Permisos sensibles identificados por SP
- [ ] Owners de aplicaciones documentados
- [ ] SPs sin actividad reciente marcados para revisión

## Notas {workspace-name}

- Tenant contoso.com — usar Lokka-Microsoft MCP para Graph API calls directos
- AuditLogs-EntraID conector activo en {workspace-name} — aprovechar para correlación
- Sign-in logs disponibles en Sentinel para detectar SPs con actividad anómala
