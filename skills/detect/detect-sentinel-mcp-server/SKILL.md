---
name: detect-sentinel-mcp-server
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Configures Microsoft Sentinel's native MCP server to enable security agents
  (Security Copilot or custom agents) to query incidents, run KQL, and update
  investigation state from conversational context.
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

- An active Microsoft Sentinel workspace with agent data
- Microsoft Security Copilot (for the primary use case) or a custom agent with Graph API access
- Microsoft Sentinel Contributor role for the principal running the MCP server
- Connection between Security Copilot and the Sentinel workspace configured

## Key concept: Sentinel as a dual platform

In the AISOC context, Microsoft Sentinel has two simultaneous roles:

| Role | Description |
|-----|-------------|
| **Target** | The SIEM that detects attacks **against** agents (jailbreak, exfiltration, anomalies) |
| **Platform** | The environment where security agents (Security Copilot, custom agents) operate to investigate and respond |

The native MCP server enables the second role: security agents can query Sentinel data directly from their own context

## Workflow

### Step 1 — Connect Security Copilot to Sentinel

1. In **Microsoft Security Copilot** → **Sources** → **Microsoft Sentinel**
2. Select the Sentinel workspace
3. Configure the access level: Read (for investigation) or Read/Write (for response)
4. Verify the connection with a test query: Show me the last 5 high severity incidents in Sentinel

### Step 2 — Enable Sentinel's native MCP server

The native MCP server exposes the following endpoints for external agents:

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

### Step 3 — Create an agentic triage prompt for AI incidents

Reference prompt for Security Copilot:

```
Role: You are a SOC analyst specialized in AI agent incidents.

For incident [INCIDENT_ID] in Microsoft Sentinel:
1. Describe the incident and its severity
2. Identify the involved agent (AgentId, AgentName, Platform)
3. Run this KQL to get context: [KQL from P05-Jailbreak-Detection.kql]
4. Determine whether the pattern is a real jailbreak attempt or a false positive
5. If real: recommend the containment steps from the detect-respond-playbook-agent-containment playbook
6. Update the incident with your findings and close it or escalate it
```

### Step 4 — KQL: identify agent incidents with no automated response

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

### Step 5 — Measure MTTD and MTTR for agentic incidents

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

- [ ] Security Copilot connected to the Sentinel workspace and returning data
- [ ] Agentic triage prompt validated against a test incident
- [ ] Structural-false-negatives KQL executed — result documented
- [ ] MTTD and MTTR baseline established for agent incidents
- [ ] Response playbook (`detect-respond-playbook-agent-containment`) integrated into the triage flow

## Implementation notes

- The native Sentinel MCP server is the mechanism that turns Sentinel into an AISOC platform — not just a receptive SIEM
- Security Copilot has access to Sentinel incidents and entities but does not run arbitrary KQL by default — enable that capability explicitly
- A security agent with write access to Sentinel can update incidents, add comments, and change state — if that agent is compromised, so is the record
- Combine with `detect-respond-playbook-agent-containment` for the full cycle: detection → agentic triage → automated enforcement
