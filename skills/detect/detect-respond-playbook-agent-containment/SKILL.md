---
name: detect-respond-playbook-agent-containment
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Playbook de respuesta a incidentes para contener un agente AI comprometido,
  incluyendo suspensión inmediata del agente, revocación de tokens activos,
  preservación de evidencia forense y notificación al equipo de seguridad,
  orquestado via Logic App vinculado a reglas de analítica de Sentinel.
tags: [detect, respond, sentinel, playbook, logic-app, containment, incident-response, aisoc]
atlas_techniques: [AML.T0051, AML.T0048, AML.T0046]
d3fend_techniques: [D3-OTA, D3-RTA, D3-ANET]
nist_ai_rmf: [MANAGE-3.2, MANAGE-4.1]
nist_csf: [RS.RP-01, RS.CO-02, RS.MI-01]
ms_license: [Microsoft Sentinel, Azure Logic Apps]
ms_roles: [Microsoft Sentinel Contributor, Logic Apps Contributor]
effort_hours: 8
---

## Cuándo usar

- Como playbook adjunto a cualquier regla de analítica del Pilar 5
- Activar manualmente cuando se confirma un agente comprometido
- Automatizar para los incidents de severidad High y Critical

## Fases del playbook

```
Detección → Triage → Contención → Preservación → Notificación → Remediación
```

Esta skill cubre las primeras cuatro fases (automatizables).
La remediación requiere revisión humana.

## Acciones de contención por severidad

| Severidad | Acción automática | Requiere aprobación |
|---|---|---|
| Low | Enriquecer incident + notificar | No |
| Medium | Suspender agente + notificar + abrir ticket | No |
| High | Suspender agente + revocar tokens + notificar | Sí (para pasos 3+) |
| Critical | Bloquear SP + revocar tokens + notificar + escalar | Sí |

## Workflow

### Paso 1 — Crear Logic App en Azure

```bash
# Crear Logic App en {workspace-name}
az logic workflow create \
  --resource-group {resource-group} \
  --location centralus \
  --name "la-aisoc-agent-containment" \
  --definition @containment-definition.json
```

### Paso 2 — Trigger: Sentinel incident creation

El trigger es `When a Microsoft Sentinel incident is created or updated`
con filtro en `Tactics contains AML.T0051 OR AML.T0046` o en el nombre de la regla.

### Paso 3 — Acción 1: Enriquecer incident con datos del agente

```http
# Obtener detalles del SP del agente involucrado
GET https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}
  ?$select=displayName,appId,createdDateTime,tags,owners

# Obtener actividad reciente (últimas 8h)
GET https://graph.microsoft.com/v1.0/auditLogs/signIns
  ?$filter=appId eq '{app-id}' and createdDateTime ge {8h-ago}
  &$top=50
```

Agregar resultado como comentario en el incident de Sentinel.

### Paso 4 — Acción 2: Suspender agente en Copilot Studio (si aplica)

Via Power Platform API:
```http
POST https://api.powerplatform.com/appmanagement/environments/{env-id}/bots/{bot-id}/disable
Authorization: Bearer {token}
```

O via Graph si es una app M365 Copilot:
```http
PATCH https://graph.microsoft.com/v1.0/applications/{app-object-id}
{
  "disabledByMicrosoftStatus": "DisabledDueToViolation"
}
```

### Paso 5 — Acción 3: Revocar todos los tokens activos del SP

```http
POST https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/revokeSignInSessions
```

Esto invalida todos los tokens de acceso y refresh tokens actuales.

### Paso 6 — Acción 4: Bloquear SP en Entra ID (Critical only)

```http
PATCH https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}
{
  "accountEnabled": false
}
```

### Paso 7 — Acción 5: Preservar evidencia forense

Exportar a Storage Account antes de que los logs expiren:

```kql
// Ejecutar y exportar via Sentinel → Logs → Export
union CopilotStudio_CL, FoundryAgents_CL, AADServicePrincipalSignInLogs, AuditLogs
| where TimeGenerated > ago(72h)
| where ServicePrincipalName == "{agent-sp-name}"
    or AgentName_s == "{agent-name}"
| extend ForensicCase = "AISOC-{incident-id}"
```

### Paso 8 — Acción 6: Notificación

```
Teams webhook → Canal AISOC-Alertas:
"🚨 AGENTE COMPROMETIDO CONTENIDO
Agente: {agent-name}
Incident: {incident-id} | Severidad: {severity}
Acciones tomadas: Suspendido, Tokens revocados
Requires human review: [link]"
```

### Paso 9 — Configurar aprobación humana para Critical

Para incidents Critical, insertar acción de aprobación antes de `accountEnabled: false`:

```
Logic App → Add action → Approvals → Start and wait for an approval
→ Approvers: security-team@{tenant}
→ Timeout: 4 horas
→ On reject: Solo notificar, no bloquear SP
```

## Verificación

- [ ] Logic App desplegada y en estado Running
- [ ] Trigger conectado a Sentinel correctamente
- [ ] Test: crear incident manual y verificar que Logic App ejecuta
- [ ] Enriquecimiento aparece como comentario en el incident de Sentinel
- [ ] `revokeSignInSessions` ejecuta sin errores (verificar en Graph API response)
- [ ] Notificación llega al canal Teams AISOC-Alertas
- [ ] Log de acciones de contención disponible en Logic App run history

## Notas {workspace-name}

- Lokka-Microsoft MCP puede ejecutar el Graph API de revocación y bloqueo de SP
- Power Platform API para deshabilitar agentes Copilot Studio requiere token de PP Admin
- Para el canal Teams: crear `AISOC-Alertas` en el equipo de seguridad de contoso.com
- La Logic App debe tener managed identity con los roles:
  - Graph API: `Application.ReadWrite.All` (para deshabilitar SP)
  - Sentinel: `Microsoft Sentinel Responder`
- Usar `{storage-account}` para preservar evidencia forense si se requiere retención > 90 días
