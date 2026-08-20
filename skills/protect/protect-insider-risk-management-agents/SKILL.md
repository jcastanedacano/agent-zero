---
name: protect-insider-risk-management-agents
version: "1.0"
pillar: protect
subdomain: ms-purview
description: >-
  Configura Microsoft Purview Insider Risk Management para detectar patrones
  de exfiltración de datos a través de agentes de IA, correlacionando actividad
  de agentes con indicadores de riesgo de usuario e identidad de agente.
tags: [protect, purview, insider-risk, exfiltration, behavioral-analytics, agent-activity]
atlas_techniques: [AML.T0057, AML.T0025]
d3fend_techniques: [D3-DAM, D3-UBA]
nist_ai_rmf: [MEASURE-2.6, MANAGE-3.2]
nist_csf: [DE.CM-03, PR.DS-05]
ms_license: [Microsoft 365 E5, Microsoft 365 E5 Insider Risk Management]
ms_roles: [Insider Risk Management, Compliance Administrator]
effort_hours: 4
---

## When to use

- When KQL-based exfiltration detection generates too many false positives for manual review
- To cover the sustained low-volume exfiltration vector (below Sentinel alert thresholds)
- In organizations with acceptable use policies that include AI agents
- As a complement to `detect-data-exfiltration-agent` for slow-vector coverage

## Prerequisites

- M365 E5 o Microsoft 365 E5 Insider Risk Management
- Insider Risk Management role (a standalone role, not included in Compliance Admin by default)
- Purview Audit habilitado y retención configurada (mínimo 90 días)
- Microsoft 365 Copilot or Copilot Studio active in the tenant to generate agent activity signals

## Workflow

### Step 1 — Habilitar indicadores de actividad de IA en IRM

1. **Microsoft Purview** → **Insider Risk Management** → **Settings** → **Policy indicators**
2. En la sección **AI activity indicators**, habilitar:
   - `Sensitive info types accessed by AI`
   - `AI interactions with high volume`
   - `Files accessed by AI without sensitivity label`
3. Guardar

### Step 2 — Crear política de detección de exfiltración via agentes

1. **Insider Risk Management** → **Policies** → **Create policy**
2. Seleccionar template: **Data leaks by risky users**
3. Ajustar con indicadores de IA:
   - Incluir: AI activity indicators del Paso 1
   - Umbral de detección: 3 desviaciones estándar del baseline del usuario
   - Ventana: 30 días rolling

### Step 3 — Correlacionar señales de IRM con actividad de agentes en Sentinel

```kql
// Correlate IRM alerts with agent activity in the same period
let IRMAlerts = SecurityAlert
    | where TimeGenerated > ago(30d)
    | where ProductName == "Microsoft 365 Insider Risk Management"
    | project AlertTime = TimeGenerated, AffectedUser = tostring(Entities[0].Name), AlertName;
let AgentActivity = CloudAppEvents
    | where TimeGenerated > ago(30d)
    | where ActionType == "AgentInteraction"
    | summarize AgentCalls = count(), UniqueAgents = dcount(tostring(RawEventData["AgentId"]))
        by UserId, bin(TimeGenerated, 1h);
IRMAlerts
| join kind=inner (AgentActivity) on $left.AffectedUser == $right.UserId
| project AlertTime, AffectedUser, AlertName, AgentCalls, UniqueAgents
| sort by AgentCalls desc
```

### Step 4 — Configurar umbrales de volumen adaptativo

```kql
// Establecer baseline de interacciones normales por usuario
CloudAppEvents
| where TimeGenerated between (ago(30d) .. ago(1d))
| where ActionType == "AgentInteraction"
| summarize
    DailyAvg = avg(count()),
    DailyP90 = percentile(count(), 90)
    by UserId, bin(TimeGenerated, 1d)
| summarize
    UserBaseline = avg(DailyAvg),
    UserP90 = avg(DailyP90)
    by UserId
| where UserP90 > 0
| sort by UserP90 desc
```

Usar `UserP90` como umbral de alerta en lugar de umbrales fijos.

### Step 5 — Integrar casos IRM con incidentes de Sentinel

1. En **Sentinel** → **Analytics** → crear regla de tipo **Microsoft Security**
2. Fuente: **Microsoft 365 Insider Risk Management**
3. Filtro de severidad: **Medium** y **High**
4. This automatically creates Sentinel incidents from IRM alerts for unified investigation

## Verification

- [ ] Indicadores de actividad de IA habilitados en IRM Settings
- [ ] Política de detección creada y en estado Active
- [ ] At least one IRM case generated (may require real or synthetic data)
- [ ] Correlación KQL entre alertas IRM y actividad de agentes validada
- [ ] Integración con Sentinel configurada para investigación unificada

## Implementation notes

- IRM requiere Purview Audit habilitado con retención de al menos 90 días — configurar antes de habilitar IRM
- Los indicadores de actividad de IA en IRM están en preview en algunos tenants — verificar disponibilidad en IRM Settings
- IRM generates sustained-behavior alerts that Sentinel does not detect well (slow exfiltration below volume thresholds) — this is the complement
- IRM cases are confidential by design — only the Insider Risk Management role can view them, not even Security Admin has access
