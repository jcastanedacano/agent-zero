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

## Cuándo usar

- Para habilitar investigación de incidentes agentic desde Security Copilot sin cambiar de interfaz
- Cuando el SOC necesita que agentes custom consulten el estado de Sentinel en tiempo real
- Para crear un flujo de triage agentic que acelere MTTD y MTTR en incidentes de IA
- Como parte de la arquitectura AISOC donde los agentes son tanto el objetivo como el respondedor

## Prerrequisitos

- Microsoft Sentinel workspace activo con datos de agentes
- Microsoft Security Copilot (para el caso de uso principal) o agente custom con acceso a Graph API
- Rol Microsoft Sentinel Contributor para el principal que ejecuta el MCP server
- Conexión entre Security Copilot y el workspace de Sentinel configurada

## Conceptos clave: Sentinel como plataforma dual

Microsoft Sentinel en el contexto AISOC tiene dos roles simultáneos:

| Rol | Descripción |
|-----|-------------|
| **Target** | SIEM que detecta ataques **contra** agentes (jailbreak, exfiltración, anomalías) |
| **Platform** | Entorno donde operan agentes de seguridad (Security Copilot, agentes custom) para investigar y responder |

El MCP server nativo habilita el segundo rol: los agentes de seguridad pueden consultar datos de Sentinel directamente desde su contexto de conversación.

## Workflow

### Paso 1 — Conectar Security Copilot con Sentinel

1. En **Microsoft Security Copilot** → **Sources** → **Microsoft Sentinel**
2. Seleccionar el workspace de Sentinel
3. Configurar el nivel de acceso: Read (para investigación) o Read/Write (para respuesta)
4. Verificar conexión con una consulta de prueba: "Show me the last 5 high severity incidents in Sentinel"

### Paso 2 — Habilitar el MCP server nativo de Sentinel

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

Para agentes custom (no Security Copilot), usar el API REST de Sentinel:

```http
GET https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.OperationalInsights/workspaces/{workspace}/providers/Microsoft.SecurityInsights/incidents
?api-version=2023-09-01-preview
&$filter=properties/severity eq 'High' and properties/status eq 'New'
&$orderby=properties/createdTimeUtc desc
&$top=10
```

### Paso 3 — Crear prompt de triage agentic para incidentes de IA

Prompt de referencia para Security Copilot:

```
Rol: Eres un analista SOC especializado en incidentes de agentes de IA.

Para el incidente [INCIDENT_ID] en Microsoft Sentinel:
1. Describe el incidente y su severidad
2. Identifica el agente involucrado (AgentId, AgentName, Platform)
3. Ejecuta esta KQL para obtener contexto: [KQL de P05-Jailbreak-Detection.kql]
4. Determina si el patrón es un intento de jailbreak real o un falso positivo
5. Si es real: recomienda los pasos de contención del playbook detect-respond-playbook-agent-containment
6. Actualiza el incidente con tus hallazgos y ciérralo o escálalo
```

### Paso 4 — KQL: Identificar incidentes de agentes sin respuesta automatizada

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

Incidentes que disparan frecuentemente sin cerrarse son **falsos negativos estructurales** — detección sin enforcement.

### Paso 5 — Medir MTTD y MTTR para incidentes agentic

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

## Verificación

- [ ] Security Copilot conectado al workspace de Sentinel y retornando datos
- [ ] Prompt de triage agentic validado contra un incidente de prueba
- [ ] KQL de falsos negativos estructurales ejecutada — resultado documentado
- [ ] MTTD y MTTR baseline establecido para incidentes de agentes
- [ ] Playbook de respuesta (`detect-respond-playbook-agent-containment`) integrado en el flujo de triage

## Notas de implementación

- El MCP server nativo de Sentinel es el mecanismo que convierte a Sentinel en una plataforma AISOC — no solo un SIEM receptivo
- Security Copilot tiene acceso a incidentes y entidades de Sentinel pero no ejecuta KQL arbitrario por defecto — habilitar la capacidad de KQL en los permisos de la conexión
- Un agente de seguridad con acceso de escritura a Sentinel puede actualizar incidentes, agregar comentarios y cambiar estado — si ese agente es comprometido, tiene acceso a toda la lógica de detección; considerar least privilege también para agentes de seguridad
- Combinar con `detect-respond-playbook-agent-containment` para el ciclo completo: detección → triage agentic → enforcement automatizado
