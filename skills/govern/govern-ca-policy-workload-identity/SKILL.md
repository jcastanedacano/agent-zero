---
name: govern-ca-policy-workload-identity
version: "1.0"
pillar: govern
subdomain: ms-entra
description: >-
  Implementa Conditional Access policies en Entra ID para workload identities
  de agentes AI, bloqueando acceso fuera de rangos IP corporativos y aplicando
  controles de sesión. grantControls mfa es inválido para non-human identities;
  solo block o sin grantControls aplica.
tags: [govern, entra, conditional-access, workload-identity, agent-identity]
atlas_techniques: [AML.T0056, AML.T0046]
d3fend_techniques: [D3-UAP, D3-NTF]
nist_ai_rmf: [GOVERN-2.2, MANAGE-1.3]
nist_csf: [PR.AA-05, PR.AC-01]
ms_license: [Microsoft Entra ID P1, Microsoft Entra Workload ID]
ms_roles: [Conditional Access Administrator, Security Administrator]
effort_hours: 8
---

## Cuándo usar

- Post Pilar 1: agentes clasificados como riesgo Alto requieren controles de acceso
- Cliente tiene Entra ID P1 (prerequisito duro para CA)
- Workload ID license requerida para CA policies en service principals específicos

## Restricciones críticas de implementación

**`grantControls: mfa` es INVÁLIDO para workload identities.** Solo aplica:
- `grantControls: { builtInControls: ["block"] }` — bloqueo total
- Sin `grantControls` + `sessionControls` — restricciones de sesión

**`continuousAccessEvaluation`** no puede estar en `enabledForReportingButNotEnforced`.
Debe ser `disabled` o `enabled` directamente.

Iniciar siempre en `enabledForReportingButNotEnforced` → monitorear 5-7 días → activar.

## Prerrequisitos

- Service principals de agentes identificados (output de Pilar 1)
- Named Locations configurados con IPs corporativas del tenant
- Entra Workload ID license asignada (para CA en non-human identities)

## Workflow

### Paso 1 — Obtener object ID del service principal

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals
  ?$filter=displayName eq '{AgentDisplayName}'
  &$select=id,appId,displayName
```

Registrar `id` (object ID) — no el `appId`.

### Paso 2 — Crear Named Location (si no existe)

```http
POST https://graph.microsoft.com/v1.0/identity/conditionalAccess/namedLocations
Content-Type: application/json

{
  "@odata.type": "#microsoft.graph.ipNamedLocation",
  "displayName": "Corporate Network - {TenantName}",
  "isTrusted": true,
  "ipRanges": [
    {
      "@odata.type": "#microsoft.graph.iPv4CidrRange",
      "cidrAddress": "10.0.0.0/8"
    }
  ]
}
```

Registrar el `id` del Named Location creado.

### Paso 3 — Crear CA policy en report-only

```http
POST https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies
Content-Type: application/json

{
  "displayName": "AISEC-Block-Agents-Outside-CorpNetwork",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "clientApplications": {
      "includeServicePrincipals": ["{service-principal-object-id}"]
    },
    "locations": {
      "includeLocations": ["All"],
      "excludeLocations": ["{named-location-id}"]
    }
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["block"]
  }
}
```

### Paso 4 — Monitorear en Sign-in logs (5-7 días)

```
Entra ID → Monitoring → Sign-in logs
→ Filter: Service principal sign-ins
→ Buscar: Conditional Access = "Report-only: Would be blocked"
```

Confirmar que no hay falsos positivos (accesos legítimos que serían bloqueados).

### Paso 5 — Activar enforcement

```http
PATCH https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policy-id}
Content-Type: application/json

{
  "state": "enabled"
}
```

## Verificación

- [ ] Named Location creado con IPs correctas
- [ ] Policy en report-only sin falsos positivos después de 5-7 días
- [ ] Policy activada (`state: enabled`)
- [ ] Sign-in logs muestran bloqueos desde IPs externas
- [ ] Sin impacto en accesos legítimos de agentes

## Notas de implementación

- Error conocido `AADSTS500011`: el resource principal no existe en el tenant — verificar que el SP del agente existe con `GET /servicePrincipals/{id}` antes de crear la policy de CA
- Mantener las CA policies de agentes en modo report-only durante al menos 7 días para identificar falsos positivos antes de pasar a enforce
- Blueprint-level CA (aplicar a grupos de SPs via `includeAgentIdServicePrincipals`) escala mejor que per-instance — usar este patrón desde el inicio
- `grantControls: mfa` es inválido para identidades de agente — usar únicamente `block` o `sessionControls`
