# Pilar 4 — Protect Data

Objective: ensure that the data AI agents access, process, and generate
estén clasificados, protegidos y no puedan exfiltrarse hacia destinos no autorizados.

## Recommended sequence

```
INPUT: Agentes con superficie reducida (output Pilar 3)
        ↓
[1] protect-purview-ai-hub-monitoring       ← visibilidad base de interacciones
        ↓
[2] protect-sensitivity-labels-ai-outputs   ← clasificar outputs automáticamente
        ↓
[3] protect-data-loss-prevention-agent-outputs ← bloquear exfiltración de outputs
        ↓
[4] protect-information-barriers-agents     ← aislar segmentos organizacionales
        ↓
OUTPUT: Protected data with active visibility and controls → input for Pillar 5 (Detect)
```

## Skills

| Skill | Producto MS | Licencia mínima | KQL disponible |
|---|---|---|---|
| `protect-purview-ai-hub-monitoring` | Purview AI Hub | Purview E3 | sentinel-ai-hub-activity.kql |
| `protect-sensitivity-labels-ai-outputs` | Purview, AIP | Purview E3 + AIP P2 | sentinel-label-coverage.kql |
| `protect-data-loss-prevention-agent-outputs` | Purview DLP | Purview E3 | sentinel-dlp-outputs.kql |
| `protect-information-barriers-agents` | Purview IB | M365 E5 Compliance | sentinel-information-barriers.kql |

## Distinción DLP prompts vs DLP outputs

| Skill | Qué protege | Ubicación del control |
|---|---|---|
| `govern-dlp-policy-copilot-prompts` (P2) | Sensitive data the user sends to the agent | In the input prompt, in real time |
| `protect-data-loss-prevention-agent-outputs` (P4) | Archivos y contenido que el agente genera | En SharePoint / OneDrive / Exchange, post-generación |

Ambas skills son complementarias — cubren vectores distintos.

## Known constraints

| Restricción | Impacto | Workaround |
|---|---|---|
| Purview auto-labeling vía API: soporte limitado | Algunas configuraciones no disponibles via Graph | Usar Compliance Portal para configuración inicial |
| Graph labels endpoint: `/beta` only | Not production-ready for automation | Accept and document, monitor for GA |
| IB: requiere Security & Compliance PowerShell | No accesible via Lokka-Microsoft MCP | Ejecutar PowerShell directamente |
| IB SharePoint: propagación hasta 24h | Control no inmediato | Planificar ventana de implementación |
| AI Hub: preview feature | May change without notice | Validate against MS Learn before documenting |
| IB for agent SPs: requires Entra attributes | Without attributes, SPs are not filterable | Establish a naming convention for agent SPs |
