---
name: detect-sentinel-mcp-server
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Configura el MCP server nativo de Microsoft Sentinel para habilitar agentes
  de seguridad (Security Copilot o agentes custom) que consulten incidentes,
  ejecuten KQL y actualicen el estado de investigaciones desde contexto conversacional.
tags: [detect, sentinel, mcp-server, security-copilot, aisoc, agentic-soc]
atlas_techniques: [AML.T0054]
d3fend_techniques: [D3-NTA, D3-SBV]
nist_ai_rmf: [MANAGE-3.2, MANAGE-4.1]
nist_csf: [DE.CM-01, RS.AN-03, RS.CO-02]
ms_license: [Microsoft Sentinel, Microsoft Security Copilot]
ms_roles: [Microsoft Sentinel Contributor, Security Operator]
effort_hours: 3
---

## When to use

- To enable agentic incident investigation from Security Copilot without switching interfaces
- When the SOC needs custom agents to query Sentinel state in real time
- To build an agentic triage flow that accelerates MTTD and MTTR on AI incidents
- As part of the AISOC architecture where agents are both the target and the responder

## Prerequisites

- Microsoft Sentinel workspace activo con datos de agentes
- Microsoft Security Copilot (for the primary use case) or a custom agent with Graph API access
- Microsoft Sentinel Contributor role for the principal running the MCP server
- Conexión entre Security Copilot y el workspace de Sentinel configurada

## Conceptos clave: Sentinel como plataforma dual

Microsoft Sentinel en el contexto AISOC tiene dos roles simultáneos:

| Rol | Descripción |
|-----|-------------|
| **Target** | SIEM que detecta ataques **contra** agentes (jailbreak, exfiltración, anomalías) |
| **Platform** | Entorno donde operan agentes de seguridad (Security Copilot, agentes custom) para investigar y responder |

The native MCP server enables the second role: security agents can query Sentinel data directly from their own context

## Workflow

### Step 1 — Conectar Security Copilot con Sentinel

1. En **Microsoft Security Copilot** → **Sources** → **Microsoft Sentinel**
2. Seleccionar el workspace de Sentinel
3. Configure the access level: Read (for investigation) or Read/Write (for response)
4. Verify the connection with a test query: Show me the last 5 high severity incidents in Sentinel

### Step 2 — Habilitar el MCP server nativo de Sentinel

El MCP server nativo expone los siguientes endpoints para agentes externos:

```json
{
  "mcpServer": {
    "name": "microsoft-sentinel",
    "capabilities": [
      "list_incidents",
      "get_incident_details",
      "run_kql_query",
      "update_incident_status",
      "add_incident_comment",
      "get_entity_insights"
    ]
  }
}
```

For custom agents (not Security Copilot), use the Sentinel REST API:

```http
GET https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.OperationalInsights/workspaces/{workspace}/providers/Microsoft.SecurityInsights/incidents
?api-version=2023-09-01-preview
&$filter=properties/severity eq 'High' and properties/status eq 'New'
&$orderby=properties/createdTimeUtc desc
&$top=10
```

### Step 3 — Crear prompt de triage agentic para incidentes de IA

Prompt de referencia para Security Copilot:

```
Rol: Eres un analista SOC especializado en incidentes de agentes de IA.

Para el incidente [INCIDENT_ID] en Microsoft Sentinel:
1. Describe el incidente y su severidad
2. Identifica el agente involucrado (AgentId, AgentName, Platform)
3. Run this KQL to get context: [KQL from P05-Jailbreak-Detection.kql]
4. Determine whether the pattern is a real jailbreak attempt or a false positive
5. If real: recommend the containment steps from the detect-respond-playbook-agent-containment playbook
6. Actualiza el incidente con tus hallazgos y ciérralo o escálalo
```

### Step 4 — KQL: Identificar incidentes de agentes sin respuesta automatizada

```kql
SecurityIncident
| where TimeGenerated > ago(30d)
| where Title has_any ("agent", "copilot", "AI", "jailbreak", "Agentic")
| where Status != "Closed"
| extend DaysOpen = datetime_diff('day', now(), CreatedTime)
| summarize
    Count = count(),
    AvgDaysOpen = avg(DaysOpen),
    OldestIncident = min(CreatedTime)
    by Title, Severity
| where Count > 3 or AvgDaysOpen > 2
| sort by Count desc
```

Incidents that fire frequently without closing are **structural false negatives** — detection without enforcement.

### Step 5 — Medir MTTD y MTTR para incidentes agentic

```kql
SecurityIncident
| where TimeGenerated > ago(90d)
| where Title has_any ("Agentic AI", "agent", "jailbreak")
| extend MTTD_hours = datetime_diff('hour', TimeGenerated, CreatedTime)
| extend MTTR_hours = datetime_diff('hour', ClosedTime, CreatedTime)
| where isnotempty(ClosedTime)
| summarize
    AvgMTTD = avg(MTTD_hours),
    AvgMTTR = avg(MTTR_hours),
    P90MTTR = percentile(MTTR_hours, 90),
    TotalIncidents = count()
    by bin(TimeGenerated, 7d)
| sort by TimeGenerated asc
```

## Verification

- [ ] Security Copilot conectado al workspace de Sentinel y retornando datos
- [ ] Prompt de triage agentic validado contra un incidente de prueba
- [ ] KQL de falsos negativos estructurales ejecutada — resultado documentado
- [ ] MTTD y MTTR baseline establecido para incidentes de agentes
- [ ] Playbook de respuesta (`detect-respond-playbook-agent-containment`) integrado en el flujo de triage

## Implementation notes

- The native Sentinel MCP server is the mechanism that turns Sentinel into an AISOC platform — not just a receptive SIEM
- Security Copilot has access to Sentinel incidents and entities but does not run arbitrary KQL by default — enable that capability explicitly
- A security agent with write access to Sentinel can update incidents, add comments, and change state — if that agent is compromised, so is the record
- Combine with `detect-respond-playbook-agent-containment` for the full cycle: detection → agentic triage → automated enforcement
