# Pilar 2 — Govern & Control

Objetivo: establecer controles sobre qué agentes pueden existir, cómo acceden a recursos,
y qué pasa con ellos a lo largo de su ciclo de vida.

## Secuencia recomendada

```
INPUT: Risk register del Pilar 1
        ↓
[1] govern-agent365-approval-flow          ← cerrar el gap de shadow AI (preventivo)
        ↓
[2] govern-ca-policy-workload-identity     ← controles de acceso para agentes de riesgo Alto
        ↓
[3] govern-pim-agent-roles                 ← eliminar privilegio permanente
        ↓
[4] govern-dlp-policy-copilot-prompts      ← protección de datos en prompts
        ↓
[5] govern-lifecycle-decommission-agent    ← operación continua + higiene
        ↓
OUTPUT: Agentes bajo control formal → input para Pilar 3 (Secure) y Pilar 4 (Protect)
```

## Skills

| Skill | Producto MS | KQL disponible |
|---|---|---|
| `govern-agent365-approval-flow` | Agent 365, Power Platform | No |
| `govern-ca-policy-workload-identity` | Entra ID, Graph API | sentinel-ca-monitoring.kql |
| `govern-pim-agent-roles` | Entra PIM | sentinel-pim-activations.kql |
| `govern-dlp-policy-copilot-prompts` | Purview Compliance | sentinel-dlp-agents.kql |
| `govern-lifecycle-decommission-agent` | Power Platform, Graph API | sentinel-inactive-agents.kql |

## Restricciones conocidas del stack Microsoft

| Restricción | Impacto | Workaround |
|---|---|---|
| `grantControls: mfa` inválido en CA para workload identities | CA policy falla en creación | Usar solo `block` |
| `continuousAccessEvaluation` + `reportOnly` incompatibles | Error al crear policy | Usar `disabled` o `enabled` |
| PIM para SP requiere Workload ID Premium | Sin licencia, no disponible para SPs | Usar role assignments con expiración |
| Purview auto-labeling via API limitada | Algunas políticas no crean via ARM | Usar Compliance Portal |
| Agent Builder bypass de Requests | Shadow AI no controlado por Agent 365 | Power Platform DLP o CA en M365 Copilot |
