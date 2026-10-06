# Pillar 1 — Discover & Prioritize

Objective: know which AI agents exist, who created them, what data they touch, and what their risk level is.

## Recommended sequence

```
[1] discover-inventory-agents-copilot-studio   ← entry point
        ↓
[2] discover-enumerate-foundry-agents          ← expand scope to Azure AI
        ↓
[3] discover-shadow-ai-entra-principals        ← surface not covered by the above
        ↓
[4] discover-classify-agent-connectors         ← data exposure matrix
        ↓
    OUTPUT: AI agent risk register → input for Pillar 2 (Govern)
```

## Skills

| Skill | MS product | Sentinel connectors | KQL |
|---|---|---|---|
| `discover-inventory-agents-copilot-studio` | M365 admin center registry, Power Platform inventory, Graph | PowerPlatformAdminActivity, CopilotActivity | sentinel-inventory.kql |
| `discover-enumerate-foundry-agents` | Microsoft Foundry (Control Plane), Azure CLI | AzureDiagnostics, AgentsInfo | sentinel-foundry.kql |
| `discover-shadow-ai-entra-principals` | Entra ID, Graph API | AuditLogs, AADServicePrincipalSignInLogs | sentinel-shadow-principals.kql |
| `discover-classify-agent-connectors` | Power Platform Admin Center | — | — |

## Expected pillar output

Risk register with, at minimum, these columns:

| AgentName | Source | CreatedBy | ApprovalStatus | Connectors | DataCategories | RiskLevel |
|---|---|---|---|---|---|---|

This register is the direct input for:
- `govern-ca-policy-workload-identity` (Pillar 2)
- `protect-purview-ai-hub-monitoring` (Pillar 4, DSPM for AI)
- `detect-alert-prompt-injection-sentinel` (Pillar 5)
