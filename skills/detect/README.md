# Pilar 5 — Detect & Respond

Objetivo: detectar amenazas activas sobre agentes AI en tiempo real y contener
agentes comprometidos antes de que el daño sea irreversible.

## Secuencia de implementación (por ROI y dependencias)

```
INPUT: Datos protegidos con visibilidad activa (output Pilar 4)
        ↓
[1] detect-alert-prompt-injection-sentinel   ← regla de firma, mayor ROI inmediato
        ↓
[2] detect-agent-identity-abuse              ← agent spawning = vector crítico
        ↓
[3] detect-data-exfiltration-agent           ← requiere DLP Pilar 4 para correlación
        ↓
[4] detect-anomalous-agent-behavior          ← requiere 7-14 días de baseline
        ↓
[5] detect-respond-playbook-agent-containment ← orquesta respuesta a todos los anteriores
        ↓
OUTPUT: AISOC operacional → retroalimenta Pilar 1 (Discover) con nuevos agentes detectados
```

## Skills

| Skill | Tipo detección | Reglas Sentinel | KQL |
|---|---|---|---|
| `detect-alert-prompt-injection-sentinel` | Firma | 1 regla scheduled | sentinel-prompt-injection.kql |
| `detect-anomalous-agent-behavior` | Comportamental/baseline | 3 reglas + UEBA | sentinel-agent-baseline.kql |
| `detect-data-exfiltration-agent` | Correlación volumétrica | 3 reglas | sentinel-exfiltration.kql |
| `detect-agent-identity-abuse` | Firma + anomalía identidad | 4 reglas | sentinel-identity-abuse.kql |
| `detect-respond-playbook-agent-containment` | Respuesta (Logic App) | 1 playbook | sentinel-ir-hunting.kql |

## Cobertura MITRE ATLAS

| Técnica ATLAS | Skill que la cubre |
|---|---|
| AML.T0051 — LLM Prompt Injection | `detect-alert-prompt-injection-sentinel` |
| AML.T0054 — LLM Plugin Compromise | `detect-alert-prompt-injection-sentinel` |
| AML.T0048 — Exfiltration via Inference API | `detect-data-exfiltration-agent` |
| AML.T0057 — LLM Data Leakage | `detect-data-exfiltration-agent` |
| AML.T0040 — ML Model Inference API Access | `detect-anomalous-agent-behavior` |
| AML.T0046 — Exfiltration via ML Model | `detect-agent-identity-abuse` |
| AML.T0056 — Discover AI Model Capabilities | `detect-agent-identity-abuse` |

## Known constraints

| Restricción | Impacto |
|---|---|
| Sentinel validates _CL tables at rule creation time | Fails if there is no data — verify BEFORE |
| UEBA requiere habilitación explícita | `BehaviorAnalytics` no disponible por default |
| `InitiatedBy.app` in AuditLogs is not always populated | Agent spawning may have false negatives |
| Baseline requiere mínimo 7 días de datos | Reglas de anomalía no efectivas antes |
| Power Platform API to disable an agent requires a PP Admin token | Not available via Lokka-Microsoft MCP |

## Cierre del ciclo del framework

```
Detect & Respond → retroalimenta → Discover & Prioritize
                                           ↓
                             Nuevos agentes detectados via IR
                             se agregan al risk register del Pilar 1
                             y reciben controles de Pilares 2-4
```

El ciclo completo:
Discover → Govern → Secure → Protect → Detect → [volver a Discover]
