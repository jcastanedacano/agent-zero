# Pillar 5 — Detect & Respond

Objective: detect active threats against AI agents in real time and contain
compromised agents before the damage becomes irreversible.

## Implementation sequence (by ROI and dependencies)

```
INPUT: Protected data with active visibility (Pillar 4 output)
        ↓
[1] detect-alert-prompt-injection-sentinel   ← signature rule, highest immediate ROI
        ↓
[2] detect-agent-identity-abuse              ← agent spawning = critical vector
        ↓
[3] detect-data-exfiltration-agent           ← requires Pillar 4 DLP for correlation
        ↓
[4] detect-anomalous-agent-behavior          ← requires 7-14 days of baseline
        ↓
[5] detect-respond-playbook-agent-containment ← orchestrates response to all of the above
        ↓
OUTPUT: Operational AISOC → feeds back into Pillar 1 (Discover) with newly detected agents
```

## Skills

| Skill | Detection type | Sentinel rules | KQL |
|---|---|---|---|
| `detect-alert-prompt-injection-sentinel` | Signature | 1 scheduled rule | sentinel-prompt-injection.kql |
| `detect-anomalous-agent-behavior` | Behavioral/baseline | 3 rules + UEBA | sentinel-agent-baseline.kql |
| `detect-data-exfiltration-agent` | Volumetric correlation | 3 rules | sentinel-exfiltration.kql |
| `detect-agent-identity-abuse` | Signature + identity anomaly | 4 rules | sentinel-identity-abuse.kql |
| `detect-respond-playbook-agent-containment` | Response (Logic App) | 1 playbook | sentinel-ir-hunting.kql |

## MITRE ATLAS coverage

| ATLAS technique | Skill that covers it |
|---|---|
| AML.T0051 — LLM Prompt Injection | `detect-alert-prompt-injection-sentinel` |
| AML.T0054 — LLM Plugin Compromise | `detect-alert-prompt-injection-sentinel` |
| AML.T0048 — Exfiltration via Inference API | `detect-data-exfiltration-agent` |
| AML.T0057 — LLM Data Leakage | `detect-data-exfiltration-agent` |
| AML.T0040 — ML Model Inference API Access | `detect-anomalous-agent-behavior` |
| AML.T0046 — Exfiltration via ML Model | `detect-agent-identity-abuse` |
| AML.T0056 — Discover AI Model Capabilities | `detect-agent-identity-abuse` |

## Known constraints

| Constraint | Impact |
|---|---|
| Sentinel validates _CL tables at rule creation time | Fails if there is no data — verify BEFORE |
| UEBA requires explicit activation | `BehaviorAnalytics` is not available by default |
| `InitiatedBy.app` in AuditLogs is not always populated | Agent spawning may have false negatives |
| Baseline requires a minimum of 7 days of data | Anomaly rules are not effective before that |
| Power Platform API to disable an agent requires a PP Admin token | Not available via Lokka-Microsoft MCP |

## Closing the framework cycle

```
Detect & Respond → feeds back into → Discover & Prioritize
                                           ↓
                             New agents detected via IR
                             are added to the Pillar 1 risk register
                             and receive Pillar 2-4 controls
```

The full cycle:
Discover → Govern → Secure → Protect → Detect → [back to Discover]
