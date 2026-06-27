# Pilar 4 — Protect Data

Objetivo: garantizar que los datos que los agentes AI acceden, procesan y generan
estén clasificados, protegidos y no puedan exfiltrarse hacia destinos no autorizados.

## Secuencia recomendada

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
OUTPUT: Datos protegidos con visibilidad y controles activos → input para Pilar 5 (Detect)
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
| `govern-dlp-policy-copilot-prompts` (P2) | Datos sensibles que el usuario envía al agente | En el prompt de entrada, en tiempo real |
| `protect-data-loss-prevention-agent-outputs` (P4) | Archivos y contenido que el agente genera | En SharePoint / OneDrive / Exchange, post-generación |

Ambas skills son complementarias — cubren vectores distintos.

## Restricciones conocidas

| Restricción | Impacto | Workaround |
|---|---|---|
| Purview auto-labeling vía API: soporte limitado | Algunas configuraciones no disponibles via Graph | Usar Compliance Portal para configuración inicial |
| Graph labels endpoint: solo `/beta` | No producción-ready para automatización | Aceptar y documentar, monitorear GA |
| IB: requiere Security & Compliance PowerShell | No accesible via Lokka-Microsoft MCP | Ejecutar PowerShell directamente |
| IB SharePoint: propagación hasta 24h | Control no inmediato | Planificar ventana de implementación |
| AI Hub: feature en preview | Puede cambiar sin aviso | Validar contra MS Learn antes de documentar |
| IB para SPs de agentes: requiere atributos Entra | Sin atributos, los SPs no son filtrables | Establecer naming convention para SPs de agentes |
