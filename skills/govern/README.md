# Pillar 2 — Govern & Control

Objective: establish controls over which agents may exist, how they access resources,
and what happens to them across their lifecycle.

## Recommended sequence

```
INPUT: Pillar 1 risk register
        ↓
[1] govern-agent365-approval-flow          ← close the shadow AI gap (preventive)
        ↓
[2] govern-ca-policy-workload-identity     ← access controls for High-risk agents
        ↓
[3] govern-pim-agent-roles                 ← eliminate standing privilege
        ↓
[4] govern-dlp-policy-copilot-prompts      ← data protection in prompts
        ↓
[5] govern-lifecycle-decommission-agent    ← ongoing operation + hygiene
        ↓
OUTPUT: Agents under formal control → input for Pillar 3 (Secure) and Pillar 4 (Protect)
```

## Skills

| Skill | MS product | KQL available |
|---|---|---|
| `govern-agent365-approval-flow` | Agent 365, Power Platform | No |
| `govern-ca-policy-workload-identity` | Entra ID, Graph API | sentinel-ca-monitoring.kql |
| `govern-pim-agent-roles` | Entra PIM | sentinel-pim-activations.kql |
| `govern-dlp-policy-copilot-prompts` | Purview DLP for Microsoft 365 Copilot | sentinel-dlp-agents.kql |
| `govern-lifecycle-decommission-agent` | M365 admin center, Power Platform, Graph API | sentinel-inactive-agents.kql |
| `govern-foundry-rbac` | Microsoft Foundry, Azure RBAC, Azure Policy | sentinel-foundry-rbac.kql |

## Known constraints in the Microsoft stack

| Constraint | Impact | Workaround |
|---|---|---|
| `grantControls: mfa` invalid in CA for workload identities | CA policy fails on creation | Use `block` only |
| `continuousAccessEvaluation` + `reportOnly` are incompatible | Error when creating the policy | Use `disabled` or `enabled` |
| PIM for SPs requires Workload ID Premium | Without the license, unavailable for SPs | Use role assignments with expiration |
| Purview auto-labeling via API is limited | Some policies cannot be created via ARM | Use the Compliance Portal |
| Agent Builder sharing creates no request (open by default) | Agents shared with the whole organization without admin review | Restrict who can share and block agents in the Microsoft 365 admin center; Power Platform DLP for Copilot Studio connectors |
