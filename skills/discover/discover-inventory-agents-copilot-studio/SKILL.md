---
name: discover-inventory-agents-copilot-studio
version: "1.0"
pillar: discover
subdomain: ms-copilot-studio
description: >-
  Enumera todos los agentes activos en Copilot Studio y Agent 365, detectando
  agentes creados sin aprobación IT (Agent Builder bypass del flujo Requests)
  que representan el gap central de shadow AI en M365.
tags: [discover, copilot-studio, shadow-ai, agent-inventory, m365-admin]
atlas_techniques: [AML.T0054, AML.T0051]
d3fend_techniques: [D3-AM, D3-SFA]
nist_ai_rmf: [MAP-1.1, GOVERN-1.2]
nist_csf: [ID.AM-01, GV-OC-01]
ms_license: [M365 Copilot, M365 E3]
ms_roles: [Microsoft 365 Administrator, Power Platform Administrator]
effort_hours: 4
---

## When to use

- Primer paso de cualquier AI security assessment
- Se detecta actividad inusual de agentes en Power Platform logs
- Pre-requisito para skills de govern y secure

Gap crítico a documentar: agentes creados desde Agent Builder (M365 Copilot)
are activated immediately without going through the Requests flow in Agent 365.
Registry and Map in Agent 365 show agents; Requests only shows the approved ones.
La diferencia = shadow AI.

## Prerequisites

- M365 Admin Center con rol de administrador
- Power Platform Admin Center accesible
- Agent 365 habilitado (tabs Registry / Map / Requests visibles)
- Entra ID: permisos para consultar service principals

## Workflow

### Step 1 — Agent 365 en M365 Admin Center

```
M365 Admin Center → Settings → Agent 365
```

Revisar tres tabs y registrar counts:
- **Registry**: total de agentes registrados
- **Map**: agentes con conexiones activas a datos
- **Requests**: agentes que pasaron por aprobación

`shadow_ai_count = Registry_count - Requests_count`

### Step 2 — Power Platform Admin Center

```
Power Platform Admin Center → Environments → [Env] → Copilot Studio → Agents
```

Exportar lista completa. Comparar displayName contra Registry.
Agentes en PP Admin ausentes en Requests = shadow AI confirmado.

### Step 3 — Microsoft Graph API

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals
  ?$filter=tags/any(t:t eq 'WindowsAzureActiveDirectoryIntegratedApp')
  &$select=displayName,appId,createdDateTime,tags
  &$orderby=createdDateTime desc
```

Filter for those created in the last 30 days to detect new unreported agents.

### Step 4 — Clasificar por nivel de riesgo

| Criterio | Alto | Medio | Bajo |
|---|---|---|---|
| Conectores | SharePoint / Email / CRM | Datos públicos | Sin conectores |
| Creador | Usuario no IT | Power User | IT |
| Aprobación | Sin Requests | Requests pendiente | Aprobado |

### Step 5 — Correlacionar con Sentinel (si connector activo)

Ejecutar queries en `queries/sentinel-inventory.kql`.

## Verification

- [ ] Count de agentes por fuente (Agent 365 / PP Admin / Graph)
- [ ] Shadow AI count calculado (Registry - Requests)
- [ ] Clasificación de riesgo por agente
- [ ] Agentes con acceso a datos sensibles identificados

## Implementation notes

- Activate the Copilot Studio connector in Sentinel so inventory queries return data in real time
- Agents created via Agent Builder (M365 Copilot) do not appear in Copilot Studio Requests — always verify directly in the Power Platform admin center
- Combine this skill with `discover-enumerate-foundry-agents` to cover the full cloud agent landscape
