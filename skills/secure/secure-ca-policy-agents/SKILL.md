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

## When to use

- When registering any agent with Entra Agent ID — the CA policy comes immediately after
- When agents are found with access unrestricted by CA (output of `govern-ca-policy-workload-identity`)
- Para migrar de policies heredadas de usuario a policies específicas de agente
- Como prerequisito antes de habilitar cualquier agente en producción

## Prerequisites

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

`grantControls: mfa` is **silently invalid** for agent identities — agents cannot complete interactive MFA. The policy appears active but enforces nothing.

## Workflow

### Step 1 — Crear la CA policy Blueprint-level

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

### Step 2 — Validar con la herramienta What If

1. Entra ID → Security → Conditional Access → **What If**
2. Configurar:
   - User: `None (service principal)`
   - Cloud app: seleccionar el SP del agente
   - Sign-in risk: `Medium`
3. Ejecutar — confirmar que la policy aparece como **Applied** con acción **Block**
4. Repeat with a human user account — confirm the policy does **NOT** apply

### Step 3 — Validar que `grantControls: mfa` no aplica

1. Crear una segunda policy de prueba con `"builtInControls": ["mfa"]`
2. Ejecutar What If con el SP del agente
3. Confirm the policy shows as **Not applied** or generates no enforcement
4. **Eliminar la policy de prueba** — documentar el hallazgo

### Step 4 — Pasar a Enforced después del período de report-only

Después de 7 días en `enabledForReportingButNotEnforced`:

```http
PATCH https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policy-id}
Content-Type: application/json

{
  "state": "enabled"
}
```

### Step 5 — KQL: Monitorear aplicaciones de CA policy en Sentinel

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

## Verification

- [ ] CA policy creada con `includeAgentIdServicePrincipals: "All"`
- [ ] What If confirms the policy applies to the agent SP at Medium risk
- [ ] What If confirma que policy NO aplica a cuentas de usuario
- [ ] `grantControls: mfa` validado como inefectivo y documentado
- [ ] Policy en report-only durante mínimo 7 días antes de enforce
- [ ] KQL de monitoreo corriendo en Sentinel como Scheduled Rule

## Implementation notes

- Blueprint-level CA (`includeAgentIdServicePrincipals: All`) covers all current and future agents — this is the correct scaling pattern vs. per-instance
- `Entra Workload ID Premium` is required to add service principal risk conditions (sign-in risk) — without this license only the base condition is available
- Always document the What If result as evidence in the Gap Assessment Template — it is the only validation mechanism that does not require generating real traffic
- Referencia oficial: [Conditional Access for workload identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity)
