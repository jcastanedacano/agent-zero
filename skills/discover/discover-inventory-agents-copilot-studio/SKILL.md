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

## Cuándo usar

- Primer paso de cualquier AI security assessment
- Se detecta actividad inusual de agentes en Power Platform logs
- Pre-requisito para skills de govern y secure

Gap crítico a documentar: agentes creados desde Agent Builder (M365 Copilot)
se activan inmediatamente sin pasar por el flujo de Requests en Agent 365.
Registry y Map en Agent 365 muestran agentes; Requests solo muestra los aprobados.
La diferencia = shadow AI.

## Prerrequisitos

- M365 Admin Center con rol de administrador
- Power Platform Admin Center accesible
- Agent 365 habilitado (tabs Registry / Map / Requests visibles)
- Entra ID: permisos para consultar service principals

## Workflow

### Paso 1 — Agent 365 en M365 Admin Center

```
M365 Admin Center → Settings → Agent 365
```

Revisar tres tabs y registrar counts:
- **Registry**: total de agentes registrados
- **Map**: agentes con conexiones activas a datos
- **Requests**: agentes que pasaron por aprobación

`shadow_ai_count = Registry_count - Requests_count`

### Paso 2 — Power Platform Admin Center

```
Power Platform Admin Center → Environments → [Env] → Copilot Studio → Agents
```

Exportar lista completa. Comparar displayName contra Registry.
Agentes en PP Admin ausentes en Requests = shadow AI confirmado.

### Paso 3 — Microsoft Graph API

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals
  ?$filter=tags/any(t:t eq 'WindowsAzureActiveDirectoryIntegratedApp')
  &$select=displayName,appId,createdDateTime,tags
  &$orderby=createdDateTime desc
```

Filtrar creados en los últimos 30 días para detectar agentes nuevos no reportados.

### Paso 4 — Clasificar por nivel de riesgo

| Criterio | Alto | Medio | Bajo |
|---|---|---|---|
| Conectores | SharePoint / Email / CRM | Datos públicos | Sin conectores |
| Creador | Usuario no IT | Power User | IT |
| Aprobación | Sin Requests | Requests pendiente | Aprobado |

### Paso 5 — Correlacionar con Sentinel (si connector activo)

Ejecutar queries en `queries/sentinel-inventory.kql`.

## Verificación

- [ ] Count de agentes por fuente (Agent 365 / PP Admin / Graph)
- [ ] Shadow AI count calculado (Registry - Requests)
- [ ] Clasificación de riesgo por agente
- [ ] Agentes con acceso a datos sensibles identificados

## Notas {workspace-name}

- Conector CopilotStudio activo en {workspace-name} — usar Query 1 en `queries/`
- Conector Foundry_Agents también activo — ver skill `discover-enumerate-foundry-agents`
- Workbook "AI Agents Governance Dashboard v2.0" disponible para visualizar resultados
- Agent Builder agents no aparecen en Requests — verificar siempre en PP Admin directamente
