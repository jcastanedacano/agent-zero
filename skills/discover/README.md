# Pillar 1 — Discover & Prioritize

Objective: know which AI agents exist, who created them, what data they touch, and what their risk level is.

## Recommended sequence

```mermaid
flowchart TD
    A["<b>1</b> discover-inventory-agents-copilot-studio<br/>entry point"] --> B["<b>2</b> discover-enumerate-foundry-agents<br/>expand scope to Foundry"]
    B --> C["<b>3</b> discover-shadow-ai-entra-principals<br/>what the first two do not see"]
    C --> D["<b>4</b> discover-classify-agent-connectors<br/>data exposure matrix"]
    D --> OUT[/"AI agent risk register"/]
    OUT --> NEXT["Pillar 2 Govern"]
    X1["discover-purview-dspm-ai<br/>what data agents touch (DSPM for AI)"] -.-> OUT
    X2["discover-third-party-ai-risk<br/>ISV extensions, MCP servers, marketplace agents"] -.-> OUT

    classDef skill fill:#0078D4,stroke:#333,color:#fff
    classDef side fill:#e6f2fb,stroke:#0078D4,color:#24292f
    classDef art fill:#FF8C00,stroke:#333,color:#24292f
    class A,B,C,D skill
    class X1,X2 side
    class OUT art
```

**How to read it.** The solid path is the order to run. Skill 1 is the entry point because the Microsoft 365 admin center registry and the Power Platform inventory are the two official lists; each later skill covers what the earlier ones cannot see. The two dotted skills feed the same register from the side: they are not steps of the sequence.


## Where the inventory comes from

```mermaid
flowchart LR
    subgraph SRC["Sources"]
        S1["Microsoft 365 admin center<br/>Agents registry, Agent Map"]
        S2["Power Platform admin center<br/>inventory, connectors"]
        S3["Sentinel<br/>CopilotActivity, PowerPlatformAdminActivity"]
        S4["Microsoft Graph beta<br/>agentIdentity query"]
        S5["Foundry Control Plane,<br/>az cognitiveservices, projects REST"]
        S6["Sentinel AzureDiagnostics,<br/>Advanced Hunting AgentsInfo"]
        S7["Microsoft Entra<br/>AuditLogs, AADServicePrincipalSignInLogs"]
    end

    K1["discover-inventory-agents-copilot-studio"]
    K2["discover-enumerate-foundry-agents"]
    K3["discover-shadow-ai-entra-principals"]
    K4["discover-classify-agent-connectors"]
    REG[("AI agent risk register")]

    S1 --> K1
    S2 --> K1
    S3 --> K1
    S4 --> K1
    S5 --> K2
    S6 --> K2
    S7 --> K3
    S2 --> K4
    K1 --> REG
    K2 --> REG
    K3 --> REG
    K4 --> REG

    classDef skill fill:#0078D4,stroke:#333,color:#fff
    classDef art fill:#FF8C00,stroke:#333,color:#24292f
    class K1,K2,K3,K4 skill
    class REG art
```

**How to read it.** Each skill reads different sources and none is complete alone. The overlap is intended: an agent that shows up in the registry but has no identity in Entra, or an identity with no registry entry, is exactly what the register has to flag.

## Skills

| Skill | MS product | Sentinel connectors | KQL |
|---|---|---|---|
| `discover-inventory-agents-copilot-studio` | M365 admin center registry, Power Platform inventory, Graph | PowerPlatformAdminActivity, CopilotActivity | sentinel-inventory.kql |
| `discover-enumerate-foundry-agents` | Microsoft Foundry (Control Plane), Azure CLI | AzureDiagnostics, AgentsInfo | sentinel-foundry.kql |
| `discover-shadow-ai-entra-principals` | Entra ID, Graph API | AuditLogs, AADServicePrincipalSignInLogs | sentinel-shadow-principals.kql |
| `discover-classify-agent-connectors` | Power Platform Admin Center | — | — |
| `discover-purview-dspm-ai` | Purview DSPM for AI | — | — |
| `discover-third-party-ai-risk` | Microsoft 365 admin center, Entra ID | — | — |

## Expected pillar output

Risk register with, at minimum, these columns:

| AgentName | Source | CreatedBy | ApprovalStatus | Connectors | DataCategories | RiskLevel |
|---|---|---|---|---|---|---|

This register is the direct input for:
- `govern-ca-policy-workload-identity` (Pillar 2)
- `protect-purview-ai-hub-monitoring` (Pillar 4, DSPM for AI)
- `detect-alert-prompt-injection-sentinel` (Pillar 5)
