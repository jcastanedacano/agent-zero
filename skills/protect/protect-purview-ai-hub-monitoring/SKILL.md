---
name: protect-purview-ai-hub-monitoring
version: "1.0"
pillar: protect
subdomain: ms-purview-ai
description: >-
  Habilita y opera Microsoft Purview AI Hub para obtener visibilidad centralizada
  of every interaction with AI agents in the tenant, including prompts,
  respuestas y datos accedidos, como base de auditoría y detección de uso indebido.
tags: [protect, purview, ai-hub, monitoring, audit, copilot-studio, m365-copilot]
atlas_techniques: [AML.T0057, AML.T0048]
d3fend_techniques: [D3-PA, D3-NTA]
nist_ai_rmf: [MEASURE-2.5, MEASURE-2.6]
nist_csf: [DE.CM-01, ID.RA-01]
ms_license: [Microsoft Purview E3, M365 E5 Compliance]
ms_roles: [Compliance Administrator, Security Reader]
effort_hours: 3
---

## When to use

- Primer control de visibilidad antes de implementar DLP o sensitivity labels
- When there is no auditing of AI agent interactions in the tenant
- Prerequisito para correlación con Sentinel: AI Hub genera eventos que el
  conector Purview envía al workspace

## Qué captura AI Hub

- Prompts enviados por usuarios a agentes M365 Copilot y Copilot Studio
- Respuestas generadas por los agentes
- Archivos y datos referenciados durante la interacción
- Sensitive information types detectados en prompts/respuestas
- Usuario, timestamp, agente involucrado

## Limitación conocida

AI Hub no captura interacciones de agentes autónomos (non-human triggered).
For agents operating without user interaction, coverage is partial.
Complementar con logs de Foundry y Sentinel analytics.

## Workflow

### Step 1 — Habilitar AI Hub en Purview Compliance Portal

```
Microsoft Purview Compliance Portal (compliance.microsoft.com)
→ Solutions → AI Hub (preview)
→ Get started → Enable AI Hub
```

If it does not appear in the menu: verify the M365 E5 Compliance or Purview E3 license.

### Step 2 — Configurar qué interacciones capturar

```
AI Hub → Settings → Data capture
```

Opciones:
- **M365 Copilot interactions**: prompts y respuestas en Copilot para M365
- **Copilot Studio interactions**: conversaciones con agentes Copilot Studio
- **Third-party AI apps**: requiere conector adicional

Habilitar todo lo disponible en el tenant.

### Step 3 — Revisar dashboard de actividad

```
AI Hub → Overview
```

Métricas disponibles:
- Total de interacciones (últimos 30 días)
- Sensitive information types detectados
- Top usuarios por volumen de interacciones
- Agentes más utilizados

### Step 4 — Configurar políticas de AI Hub

```
AI Hub → Policies → Create policy
```

Tipos de política disponibles:
- **Sensitive data**: alertar cuando se detecte PII, datos financieros, etc.
- **Prompt injection indicators**: patrones de instrucciones maliciosas
- **Restricted topics**: temas que el agente no debe tratar

### Step 5 — Conectar con Sentinel

AI Hub genera eventos en el `MicrosoftDataLossPrevention` y `PurviewAuditLog` tables.
Verify the Purview connector is active in {workspace-name} and that events are flowing.

```kql
// Verificar flujo de eventos desde AI Hub
PurviewAuditLog
| where TimeGenerated > ago(24h)
| where Workload has "Copilot"
| summarize count() by OperationName
```

### Step 6 — Exportar a Sentinel para correlación avanzada

```kql
// Ver queries/sentinel-ai-hub-activity.kql
```

## Verification

- [ ] AI Hub habilitado y visible en Compliance Portal
- [ ] Data capture activo para M365 Copilot y Copilot Studio
- [ ] Dashboard muestra interacciones de los últimos 7 días
- [ ] Al menos una política de AI Hub creada
- [ ] Eventos visibles en Sentinel (`PurviewAuditLog` tiene filas recientes)

## Implementation notes

- Verify the Purview Audit connector is active in Sentinel — without it, `PurviewAuditLog` will have no data for the monitoring queries
- AI Hub is in preview — validate functionality against Microsoft Learn documentation before writing it into production runbooks
- If AI Hub is unavailable in the tenant: use `MicrosoftDataLossPrevention` as an alternative table to correlate interactions
