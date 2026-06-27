---
name: secure-ca-policy-agents
version: "1.0"
pillar: secure
subdomain: ms-entra
description: >-
  Crea y valida políticas de Conditional Access específicas para identidades
  de agentes de IA usando clientApplications.includeAgentIdServicePrincipals,
  evitando la misconfiguration crítica de grantControls mfa inválido para agentes.
tags: [secure, entra, conditional-access, workload-identity, least-privilege, mfa-trap]
atlas_techniques: [AML.T0012, AML.T0040]
d3fend_techniques: [D3-MAN, D3-UAP]
nist_ai_rmf: [GOVERN-2.1, MANAGE-2.4]
nist_csf: [PR.AA-05, PR.AC-04]
ms_license: [Microsoft Entra ID P1, Entra Workload ID Premium]
ms_roles: [Conditional Access Administrator, Security Administrator]
effort_hours: 3
---

## Cuándo usar

- Al registrar cualquier agente con Entra Agent ID — la CA policy va inmediatamente después
- Cuando se detectan agentes con acceso no restringido por CA (resultado de `govern-ca-policy-workload-identity`)
- Para migrar de policies heredadas de usuario a policies específicas de agente
- Como prerequisito antes de habilitar cualquier agente en producción

## Prerrequisitos

- Entra ID P1 mínimo (Workload ID Premium para condiciones de riesgo)
- Rol Conditional Access Administrator
- Agentes registrados con Entra Agent ID (ver `govern-entra-agent-id`)
- Acceso a Entra ID → Security → Conditional Access

## La trampa crítica: `grantControls: mfa`

```json
// ❌ INCORRECTO — no usar para agentes
{
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["mfa"]
  }
}

// ✅ CORRECTO — bloqueo explícito para agentes con riesgo
{
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["block"]
  }
}
```

`grantControls: mfa` es **silenciosamente inválido** para identidades de agente — los agentes no pueden completar MFA interactivo. La policy aparece activa pero no genera ningún enforcement. El único control válido para bloqueo es `block`.

## Workflow

### Paso 1 — Crear la CA policy Blueprint-level

```json
POST https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies
Content-Type: application/json

{
  "displayName": "Agentic AI — Risk-Based Access Control",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "clientApplications": {
      "includeServicePrincipals": [],
      "excludeServicePrincipals": [],
      "includeAgentIdServicePrincipals": "All"
    },
    "signInRiskLevels": ["high", "medium"]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["block"]
  }
}
```

### Paso 2 — Validar con la herramienta What If

1. Entra ID → Security → Conditional Access → **What If**
2. Configurar:
   - User: `None (service principal)`
   - Cloud app: seleccionar el SP del agente
   - Sign-in risk: `Medium`
3. Ejecutar — confirmar que la policy aparece como **Applied** con acción **Block**
4. Repetir con una cuenta de usuario humano — confirmar que la policy **NO aplica**

### Paso 3 — Validar que `grantControls: mfa` no aplica

1. Crear una segunda policy de prueba con `"builtInControls": ["mfa"]`
2. Ejecutar What If con el SP del agente
3. Confirmar que la policy aparece como **Not applied** o no genera enforcement
4. **Eliminar la policy de prueba** — documentar el hallazgo

### Paso 4 — Pasar a Enforced después del período de report-only

Después de 7 días en `enabledForReportingButNotEnforced`:

```http
PATCH https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policy-id}
Content-Type: application/json

{
  "state": "enabled"
}
```

### Paso 5 — KQL: Monitorear aplicaciones de CA policy en Sentinel

```kql
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(7d)
| where ConditionalAccessStatus == "failure"
| extend PolicyName = tostring(ConditionalAccessPolicies[0].displayName)
| extend PolicyResult = tostring(ConditionalAccessPolicies[0].result)
| summarize
    BlockedAttempts = count(),
    LastAttempt = max(TimeGenerated),
    SourceIPs = make_set(IPAddress, 10)
    by ServicePrincipalName, PolicyName, PolicyResult
| sort by BlockedAttempts desc
```

## Verificación

- [ ] CA policy creada con `includeAgentIdServicePrincipals: "All"`
- [ ] What If confirma que policy aplica al SP del agente con riesgo Medium
- [ ] What If confirma que policy NO aplica a cuentas de usuario
- [ ] `grantControls: mfa` validado como inefectivo y documentado
- [ ] Policy en report-only durante mínimo 7 días antes de enforce
- [ ] KQL de monitoreo corriendo en Sentinel como Scheduled Rule

## Notas de implementación

- Blueprint-level CA (`includeAgentIdServicePrincipals: "All"`) cubre todos los agentes actuales y futuros — es el patrón de escala correcto vs. per-instance
- `Entra Workload ID Premium` es necesario para agregar condiciones de riesgo de service principal (sign-in risk) — sin esta licencia solo está disponible el bloqueo incondicional
- Documentar siempre el resultado del What If como evidencia en el Gap Assessment Template — es el único mecanismo de validación sin necesidad de generar tráfico real
- Referencia oficial: [Conditional Access for workload identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity)
