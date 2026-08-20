# Pilar 1 — Discover & Prioritize

Objective: know which AI agents exist, who created them, what data they touch, and what their risk level is.

## Recommended sequence

```
[1] discover-inventory-agents-copilot-studio   ← punto de entrada
        ↓
[2] discover-enumerate-foundry-agents          ← ampliar scope a Azure AI
        ↓
[3] discover-shadow-ai-entra-principals        ← surface no cubierto por los anteriores
        ↓
[4] discover-classify-agent-connectors         ← matriz de exposición de datos
        ↓
    OUTPUT: Risk register de agentes AI → input para Pilar 2 (Govern)
```

## Skills

| Skill | Producto MS | Conectores Sentinel | KQL |
|---|---|---|---|
| `discover-inventory-agents-copilot-studio` | Agent 365, PP Admin, Graph | CopilotStudio_CL | sentinel-inventory.kql |
| `discover-enumerate-foundry-agents` | Azure AI Foundry, Azure CLI | FoundryAgents_CL | sentinel-foundry.kql |
| `discover-shadow-ai-entra-principals` | Entra ID, Graph API | AuditLogs, AADServicePrincipalSignInLogs | sentinel-shadow-principals.kql |
| `discover-classify-agent-connectors` | Power Platform Admin Center | — | — |

## Output esperado del pilar

Risk register con columnas mínimas:

| AgentName | Source | CreatedBy | ApprovalStatus | Connectors | DataCategories | RiskLevel |
|---|---|---|---|---|---|---|

Este register es el input directo para:
- `govern-ca-policy-workload-identity` (Pilar 2)
- `protect-purview-ai-hub-monitoring` (Pilar 4)
- `detect-alert-prompt-injection-sentinel` (Pilar 5)
