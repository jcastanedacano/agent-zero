---
name: secure-least-privilege-agent-identity
version: "1.0"
pillar: secure
subdomain: ms-entra
description: >-
  Audita y reduce permisos de service principals de agentes AI al mínimo
  necesario, eliminando OAuth2 permission grants excesivos y app role assignments
  unused ones, applying the least privilege principle to non-human identities.
tags: [secure, entra, least-privilege, service-principal, oauth, app-roles]
atlas_techniques: [AML.T0046, AML.T0040]
d3fend_techniques: [D3-UAP, D3-MAN]
nist_ai_rmf: [MANAGE-1.3, GOVERN-2.2]
nist_csf: [PR.AA-05, PR.AC-04]
ms_license: [Microsoft Entra ID P1]
ms_roles: [Application Administrator, Privileged Role Administrator]
effort_hours: 6
---

## When to use

- Post clasificación de conectores (Pilar 1): agentes con permisos excesivos identificados
- Antes de mover agentes a producción
- Auditoría periódica trimestral de permisos de agentes

## Principio central

An AI agent should only hold the permissions it needs to execute
its declared use case, nothing more. Permissions such as `Files.ReadWrite.All`
cuando el caso de uso solo requiere leer un SharePoint específico
es una superficie de ataque innecesaria.

## Workflow

### Step 1 — Auditar permisos actuales del service principal

```http
# OAuth2 delegated permissions (actúan en nombre de un usuario)
GET https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/oauth2PermissionGrants
  ?$select=scope,consentType,principalId

# App role assignments (actúan como la aplicación, sin usuario)
GET https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/appRoleAssignments
  ?$select=appRoleId,resourceDisplayName,principalDisplayName
```

### Step 2 — Mapear permisos al caso de uso real

Para cada permiso, responder:
- ¿El agente usa este permiso activamente? (verificar en logs de uso)
- ¿El caso de uso documentado lo requiere?
- ¿Existe un permiso de menor privilegio que cubra la misma necesidad?

**Tabla de sustituciones comunes:**

| Permiso actual (excesivo) | Reemplazar por |
|---|---|
| `Files.ReadWrite.All` | `Sites.Selected` (SharePoint específico) |
| `Mail.ReadWrite` | `Mail.Read` (si solo lee) |
| `Directory.ReadWrite.All` | `Directory.Read.All` o scope específico |
| `User.ReadWrite.All` | `User.Read` (si solo lee perfil propio) |
| `Group.ReadWrite.All` | `GroupMember.Read.All` |

### Step 3 — Revocar permisos excesivos

```http
# Revocar OAuth2 grant específico
DELETE https://graph.microsoft.com/v1.0/oauth2PermissionGrants/{grant-id}

# Revocar app role assignment
DELETE https://graph.microsoft.com/v1.0/servicePrincipals/{resource-sp-id}/appRoleAssignedTo/{assignment-id}
```

### Step 4 — Asignar permisos granulares de reemplazo

Ejemplo — `Sites.Selected` para acceso a SharePoint específico:

```http
# Paso 4a: Asignar app role Sites.Selected al SP
POST https://graph.microsoft.com/v1.0/servicePrincipals/{sharepoint-sp-id}/appRoleAssignedTo
{
  "principalId": "{agent-sp-object-id}",
  "resourceId": "{sharepoint-sp-id}",
  "appRoleId": "{sites-selected-role-id}"
}

# Paso 4b: Otorgar acceso al site específico via Sites API
POST https://graph.microsoft.com/v1.0/sites/{site-id}/permissions
{
  "roles": ["read"],
  "grantedToIdentities": [{
    "application": {
      "id": "{agent-app-id}",
      "displayName": "{agent-name}"
    }
  }]
}
```

### Step 5 — Verificar funcionalidad post-reducción

Run the agent use case and confirm it works with the reduced permissions.
Monitorear errores de autorización en los primeros 3-5 días.

### Step 6 — Monitorear uso de permisos restantes

```kql
// Ver queries/sentinel-permission-usage.kql
```

## Verification

- [ ] Inventario de permisos pre y post reducción documentado
- [ ] Permisos excesivos revocados (GET retorna array reducido)
- [ ] Permisos granulares de reemplazo asignados
- [ ] Funcionalidad del agente verificada
- [ ] Monitoreo de errores de autorización activo (3-5 días post-cambio)

## Implementation notes

- `Sites.Selected` is the least privilege alternative to `Sites.ReadWrite.All` for agents that only need access to specific sites
- To get the `appRoleId` for `Sites.Selected`, query the SharePoint service principal appRoles via Graph
- Los cambios en permisos de Graph API pueden tardar hasta 60 minutos en propagarse — no asumir aplicación inmediata en pipelines de CI/CD
- Usar Graph Explorer (graph.microsoft.com) para validar el scope mínimo necesario antes de asignar permisos en producción
