# Pillar 5 — Detect & Respond

Objective: detect active threats against AI agents in real time and contain
compromised agents before the damage becomes irreversible.

## Implementation sequence (by ROI and dependencies)

```mermaid
flowchart TD
    IN[/"Protected data with active visibility (Pillar 4 output)"/] --> A["<b>1</b> detect-alert-prompt-injection-sentinel<br/>platform flags and alerts, no prompt text needed"]
    A --> B["<b>2</b> detect-agent-identity-abuse<br/>agent spawning is a critical vector"]
    B --> C["<b>3</b> detect-data-exfiltration-agent<br/>needs Pillar 4 DLP for correlation"]
    C --> D["<b>4</b> detect-anomalous-agent-behavior<br/>needs 7 to 14 days of baseline"]
    D --> E["<b>5</b> detect-respond-playbook-agent-containment<br/>orchestrates the response to all of the above"]
    E --> OUT[/"Operational AI security operations"/]
    OUT --> P1["Feeds Pillar 1 Discover with newly detected agents"]
    X1["detect-security-copilot-triage<br/>Security Copilot triage of agent incidents"] -.-> E
    X2["detect-sentinel-mcp-server<br/>Sentinel MCP server for security agents"] -.-> E

    classDef skill fill:#0078D4,stroke:#333,color:#fff
    classDef side fill:#e6f2fb,stroke:#0078D4,color:#24292f
    classDef art fill:#FF8C00,stroke:#333,color:#24292f
    class A,B,C,D,E skill
    class X1,X2 side
    class IN,OUT art
```

**How to read it.** The order follows return on effort and dependencies: platform flags need no baseline, agent identity abuse is the next critical vector, exfiltration needs the Pillar 4 DLP signal to correlate with, and behavioral anomalies need a baseline of 7 to 14 days. The playbook comes last because it responds to everything before it.

## How a detection becomes a response

```mermaid
flowchart LR
    subgraph SIG["Signals"]
        S1["CopilotActivity, SecurityAlert<br/>JailbreakDetected, XPIADetected"]
        S2["AADServicePrincipalSignInLogs, AuditLogs<br/>agent identity events"]
        S3["OfficeActivity, DLP matches"]
        S4["MicrosoftGraphActivityLogs<br/>baselines"]
    end

    subgraph RUL["Sentinel analytics rules"]
        R1["Prompt injection<br/>3 rules"]
        R2["Identity abuse<br/>4 rules"]
        R3["Exfiltration<br/>5 rules"]
        R4["Anomalous behavior<br/>3 rules, ID Protection, UEBA"]
    end

    S1 --> R1
    S2 --> R2
    S3 --> R3
    S4 --> R4
    S2 --> R4

    R1 --> INC["Sentinel incident"]
    R2 --> INC
    R3 --> INC
    R4 --> INC
    INC --> AUTO["Automation rule<br/>filter on rule name or severity"]
    AUTO --> PB["Playbook (Logic App)<br/>detect-respond-playbook-agent-containment"]
    PB --> ACT["Contain, preserve evidence, notify"]
    INC --> TRI["Security Copilot triage<br/>detect-security-copilot-triage"]

    classDef sig fill:#e6f2fb,stroke:#0078D4,color:#24292f
    classDef rule fill:#0078D4,stroke:#333,color:#fff
    classDef resp fill:#FF8C00,stroke:#333,color:#24292f
    class S1,S2,S3,S4 sig
    class R1,R2,R3,R4 rule
    class INC,AUTO,PB,ACT,TRI resp
```

**How to read it.** Left to right is the path of one detection. Rules are built on flags, identities, volumes and sequences, never on prompt text, because the audit record does not carry it. An incident does not trigger a playbook by itself: an automation rule decides which playbook runs, filtering on the analytics rule name or the severity (Sentinel incident tactics are MITRE ATT&CK tactics, so a MITRE ATLAS technique ID cannot be used as the filter).


## Skills

| Skill | Detection type | Sentinel rules | KQL |
|---|---|---|---|
| `detect-alert-prompt-injection-sentinel` | Platform signals | 3 scheduled rules | sentinel-prompt-injection.kql |
| `detect-anomalous-agent-behavior` | Behavioral/baseline | 3 rules + ID Protection + UEBA | sentinel-agent-baseline.kql |
| `detect-data-exfiltration-agent` | Volumetric correlation | 5 rules | sentinel-exfiltration.kql |
| `detect-agent-identity-abuse` | Signature + identity anomaly | 4 rules | sentinel-identity-abuse.kql |
| `detect-respond-playbook-agent-containment` | Response (Logic App) | 1 playbook | sentinel-ir-hunting.kql |
| `detect-security-copilot-triage` | Triage (Security Copilot) | none | No |
| `detect-sentinel-mcp-server` | Platform integration (Sentinel MCP server) | none | No |

## MITRE ATLAS coverage

| ATLAS technique | Skill that covers it |
|---|---|
| AML.T0040 — AI Model Inference API Access | `detect-agent-identity-abuse`, `detect-anomalous-agent-behavior` |
| AML.T0051 — LLM Prompt Injection | `detect-alert-prompt-injection-sentinel`, `detect-respond-playbook-agent-containment`, `detect-security-copilot-triage` |
| AML.T0054 — LLM Jailbreak | `detect-alert-prompt-injection-sentinel`, `detect-security-copilot-triage`, `detect-sentinel-mcp-server` |
| AML.T0057 — LLM Data Leakage | `detect-data-exfiltration-agent` |
| AML.T0084 — Discover AI Agent Configuration | `detect-agent-identity-abuse`, `detect-anomalous-agent-behavior` |
| AML.T0086 — Exfiltration via AI Agent Tool Invocation | `detect-anomalous-agent-behavior`, `detect-data-exfiltration-agent`, `detect-respond-playbook-agent-containment` |
| AML.T0091.000 — Use Alternate Authentication Material: Application Access Token | `detect-agent-identity-abuse`, `detect-respond-playbook-agent-containment` |
| AML.T0103 — Deploy AI Agent | `detect-agent-identity-abuse` |

## Known constraints

| Constraint | Impact |
|---|---|
| Sentinel validates the tables a rule references at creation time | Fails if the table does not exist — verify BEFORE. `CopilotStudio_CL` and `FoundryAgents_CL` do not exist in the validation workspace: use `CopilotActivity`, `OfficeActivity`, `AADServicePrincipalSignInLogs` and `MicrosoftGraphActivityLogs` |
| UEBA requires explicit activation | `BehaviorAnalytics` is not available by default |
| `InitiatedBy.app` in AuditLogs is not always populated | Agent spawning may have false negatives |
| Baseline requires a minimum of 7 days of data | Anomaly rules are not effective before that |
| The Power Platform quarantine API takes a user access token (Global, AI or Power Platform administrator) | A Logic App managed identity cannot call it; not available via Lokka-Microsoft MCP |
| `revokeSignInSessions` exists for users only | No session-revocation call for service principals or agent identities: disable, confirm compromised, remove credentials |
| Native layers cover part of the agent threats | Compare them before building custom rules: the table in [Track C Module 05](../../Track-C-SOC-Engineer/Module-05-DetectRespond.md#what-each-native-layer-covers-and-what-it-leaves-open) lists what each one covers and leaves open |

## Closing the framework cycle

```mermaid
flowchart LR
    DET["Detect and respond"] -- "agent found during an incident" --> DIS["Discover<br/>added to the Pillar 1 risk register"]
    DIS --> CTRL["Receives the controls of<br/>Govern, Secure and Protect"]
    CTRL --> DET

    classDef n fill:#0078D4,stroke:#333,color:#fff
    class DET,DIS,CTRL n
```


The full cycle across the five pillars is in [`skills/README.md`](../README.md).
