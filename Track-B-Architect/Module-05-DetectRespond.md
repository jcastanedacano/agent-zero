# Module 05 — Detect & Respond | Track B

**Module duration:** 90 minutes

**Learning objective:**
By the end of this module, participants will be able to design a detection and response architecture specific to AI agents, integrate agentic behavioral signals into Microsoft Sentinel, create analytics rules with automated enforcement via Logic App, identify structural false negatives in the current detection model, and complete the Gap Assessment with a prioritized 90-day implementation roadmap.

**Module agenda:**

| Time | Activity | Type |
|------|----------|------|
| 20 min | SOC architecture for agents: signal sources, tables, detection-to-enforcement chain | Presentation |
| 15 min | Structural false negatives: why human-calibrated detections fail for agents | Presentation |
| 45 min | Lab: Sentinel analytics rules + Logic App enforcement + detection KQL | Lab |
| 10 min | Gap Assessment consolidation and 90-day roadmap | Discussion |

---

**Core content (points the facilitator must cover):**

1. **Structural false negatives from human calibration:** Detection rules calibrated for human behavior generate false negatives when monitoring agents. An agent making 5,000 SharePoint calls per hour may be operating normally or executing an exfiltration — the difference is in the delta against its baseline, not in the absolute volume. Without a per-agent baseline, any fixed threshold generates either false positives or false negatives.

2. **Detection posture vs. enforcement posture:** An organization with active detection but no response automation has MTTR limited by human reaction time. For agents acting in seconds, the architectural goal is: automatic detection → automatic containment → human review. The token revocation Logic App is the minimum viable containment control.

3. **Applicable Microsoft controls:** Defender XDR integrates agent behavioral signals with identity and device context. Microsoft Sentinel with its native MCP server allows querying agent status from within an active investigation. Security Copilot accelerates triage of complex incidents. Purview Audit provides the forensic chain of custody with immutability. Agent 365 correlates incident events with the agent ownership registry.

4. **The Sentinel native MCP server as an architectural differentiator:** Sentinel's MCP server allows a security agent (Security Copilot or custom) to query incident status, run KQL queries, and update investigation state directly from the conversation context — without leaving the triage interface. This is the bridge between agentic detection and agentic response.

5. **Single-turn detection blind spot — composite and decomposed injection attacks:** Q1 (Jailbreak-Detection) and Q7 (LPCI) are single-turn detectors: they score each prompt or tool response independently against a threshold. CrowdStrike's 2025 prompt injection taxonomy (200+ techniques) documents two evasion patterns that specifically defeat single-turn scoring: (a) **Algorithmic Payload Decomposition (PT0200)** — a malicious instruction is split into fragments across 2–5 consecutive prompts, each scoring below threshold individually; when the agent's context window accumulates the full session, the composite instruction activates; (b) **Trigger-Activated Rule Addition (PT0201)** — a dormant instruction is planted early in the session and only fires when a trigger phrase appears in a later user message or tool response. Both techniques are invisible to per-prompt keyword rules. The counter-architecture is session-level aggregation: KQL P05-Q9 implements cumulative fragment scoring across a session window, surfacing decomposed payloads that would each score below the Q1 threshold. Detection for PT0201 requires correlating a rule-planting event early in a session with a trigger event later in the same session — a two-pass join not possible in a single-turn query. Prompt Shield in Azure AI Foundry evaluates the full assembled prompt before inference and is the complementary preventive control that catches what log-based detection sees only retrospectively.

6. **Defender for Cloud + Prompt Shield — pre-inference detection layer (activation and licensing required):** KQL-based detection (Q1, Q7, Q9) operates post-inference: the prompt already reached the model before the log is written. For two CrowdStrike technique classes that are hard to catch in logs — **PT0198 (Special Token Injection)**, which uses fake structural delimiters (`<|system|>`, `###SYSTEM###`) to elevate untrusted content to system-directive level, and **PT0197 (Cognitive Token Suppression)**, which blocks safety vocabulary to shift the model away from refusal — the correct detection layer is pre-inference, before the model processes the prompt. The Microsoft control for this is **Prompt Shield** (Azure AI Content Safety), surfaced as security alerts through **Defender for Cloud**. Architecture and activation requirements:

   - **Prompt Shield enablement (per deployment):** In Azure AI Foundry → deployment → Safety + Security → Content filters: enable Prompt Shield for (a) user prompts and (b) indirect attacks (documents/tool responses). Without this step, no signal reaches Defender for Cloud. Prompt Shield evaluates the full assembled prompt including injected structural tokens before inference — it catches PT0198 delimiter patterns and PT0197 vocabulary suppression attempts that would evade keyword-matching KQL.
   - **Defender for Cloud — Defender for AI services plan:** In Defender for Cloud → Environment settings → subscription → Defender plans → AI services: enable the plan. This is a paid plan billed per 1,000 API requests to Azure OpenAI / Azure AI Foundry. Without enabling this plan, Prompt Shield detections are not surfaced as security alerts in Defender for Cloud and do not flow into Sentinel.
   - **Sentinel integration:** Defender for Cloud alerts flow into Microsoft Sentinel via the **Microsoft Defender XDR data connector** (not the legacy Defender for Cloud connector). Once connected, Prompt Shield alerts appear as `SecurityAlert` records with `AlertType == "PromptInjection"` or `"JailbreakAttempt"`, available in the same KQL workspace as the P05 queries.
   - **Scope limitation:** Prompt Shield covers Azure AI Foundry and Azure OpenAI deployments only. Agents using external model APIs (OpenAI direct, Anthropic direct) or self-hosted models (Ollama) are outside Prompt Shield coverage — those require the log-based KQL approach (Q1, Q7, Q9) or equivalent controls from the model provider.

   | Detection gap | CrowdStrike technique | Coverage via KQL (P05) | Coverage via Defender for Cloud + Prompt Shield |
   |--------------|----------------------|------------------------|------------------------------------------------|
   | Structural token elevation | PT0198 Special Token Injection | Partial (Q1 keyword match only) | Full — delimiter injection pattern detection pre-inference |
   | Safety vocabulary blocking | PT0197 Cognitive Token Suppression | Not covered | Covered — prompt semantic analysis |
   | Fragmented multi-turn payload | PT0200 Payload Decomposition | Q9 session aggregation | Partial — per-prompt only, not session-aware |
   | Dormant trigger instructions | PT0201 Trigger-Activated Rule Addition | Architecture gap (two-pass join) | Partial — detects trigger content at send time |
   | Indirect injection via trusted data | IM0018 Unwitting User Context Injection | Q7 LPCI (tool responses) | Full — indirect attack mode covers documents |

   **Activation checklist for the lab:** (1) Confirm Azure AI Foundry deployment has Prompt Shield enabled for both prompt and indirect modes; (2) Confirm Defender for Cloud "AI services" plan is active on the subscription; (3) Confirm Sentinel has the Defender XDR connector enabled; (4) Run a test injection phrase in the Foundry Playground and verify the alert appears in Defender for Cloud within 5 minutes.

7. **Behavioral drift monitoring — deteccion de degradacion silenciosa:** Un agente puede degradar su postura de seguridad gradualmente sin que ninguna configuracion cambie. El modelo subyacente puede actualizarse, el corpus de fine-tuning puede evolucionar, o la distribucion de inputs de produccion puede desplazarse hasta hacer que patrones antes raros sean la norma. El resultado es drift de comportamiento: la tasa de rechazo de borderline requests baja de 92% a 61% en seis meses sin ninguna alerta, ningun cambio de policy y ningun incidente registrado. La deteccion requiere metricas de comportamiento en el tiempo, no solo alertas de umbral fijo. Controles aplicables: (a) **Baseline de tasa de rechazo por agente** — query semanal que mide el porcentaje de conversaciones con al menos un safety refusal sobre total de conversaciones; una caida de mas de 10 puntos porcentuales respecto al mes anterior dispara una revision; (b) **Sentinel Workbook de drift** — grafica la tasa de rechazo, tasa de escalacion HITL y volumen de tool calls sobre una ventana rodante de 90 dias por agente; (c) **Revision de modelo ante actualizaciones de proveedor** — cuando Azure OpenAI publica una nueva version del modelo, re-ejecutar el red team playbook del Track C antes de migrar el agente a produccion. Referencia: CLLMSE §8.2 — Behavioral Drift Detection.

8. **Canary tokens y honeytokens como controles detectivos para agentes RAG:** Los controles preventivos (Prompt Shield, DLP, CA) reducen la probabilidad de exfiltracion, pero no garantizan deteccion cuando un ataque tiene exito. Dos controles detectivos complementan la capa de prevencion: (a) **Canary token** (credencial sensuelo) — un secreto de Key Vault, una cadena de conexion de base de datos o una clave de API con formato valido pero sin privilegios reales, plantado en el entorno del agente. Si el token aparece en logs de red salientes, en una respuesta del agente a un usuario externo, o en Sentinel como una credencial usada contra un recurso real, confirma que ocurrio exfiltracion. Microsoft Sentinel tiene detectores de credencial en logs de `AADNonInteractiveUserSignInLogs` y `AzureActivity` — un canary token bien nombrado (por ejemplo `canary-agent-kv-prod`) aparecera de inmediato si es usado; (b) **Honeytoken** (documento sensuelo en el corpus RAG) — un documento con formato de datos sensibles (lista de empleados, contrato, resultado financiero) plantado en SharePoint con un nombre convincente pero contenido fabricado. Si el agente RAG lo recupera y lo devuelve en una respuesta, el Purview Audit log registra el acceso. Si ese contenido aparece fuera del perimetro esperado, confirma que el control de acceso del corpus RAG fallo. Diferencia clave: el canary token detecta exfiltracion de credenciales; el honeytoken detecta fallo de acceso al corpus. Ambos son complementarios. Implementacion: crear el honeytoken en SharePoint con permisos de lectura solo para el agente; crear una alerta en Sentinel que dispare cuando el nombre del documento aparezca en `SharePointFileOperations` con un AccountId externo. Referencia: CLLMSE §5.4.

9. **Agent-to-agent prompt injection (multi-agent trust boundaries):** En arquitecturas con multiples agentes (orquestador + subagentes especializados, o cadenas de agentes en AutoGen/Semantic Kernel), existe un vector que los detectores de agente unico no cubren: el **agente A acepta como instrucciones el output del agente B sin revalidar ese output contra una policy independiente**. Si el agente B fue comprometido a traves de indirect injection (LPCI via tool response), sus outputs contienen instrucciones adversariales que el agente A ejecuta como si fueran instrucciones del orquestador de confianza. El fallo arquitectonico es asumir que la confianza en el agente B implica confianza en todo lo que B produce. Controles: (a) **Revalidacion en cada boundary** — el agente orquestador debe pasar los outputs de subagentes por Prompt Shield (modo indirect) antes de incluirlos en su propio context window; (b) **Scope de herramientas por agente** — cada subagente opera con el conjunto minimo de herramientas necesario para su tarea especifica; una instruccion inyectada en un subagente no debe poder activar herramientas de otro dominio; (c) **Audit trail entre agentes** — loguear explicitamente qué agente genero cada instruccion que llega al orquestador; la tabla `CloudAppEvents` con `ActionType == "AgentInvocation"` debe incluir el AgentId de origen. Referencia: CLLMSE §7.5 — Multi-Agent Trust Boundaries. Relacionado: P05-Q7 (LPCI via tool response), MAESTRO Layer 3 (Agent Interaction).

10. **The compromised monitoring agent problem (MAESTRO Layer 5):** The CSA MAESTRO framework identifies a class of threat specific to Layer 5 (Evaluation & Observability): the monitoring agent itself becomes a target. When Security Copilot or a custom triage agent ingests alert context, that context can contain adversarially crafted content — LPCI via tool responses (KQL P05-Q7) is the most concrete example. An agent that processes alert summaries containing injected instructions may suppress, misclassify, or modify incident records. The control is the same as for all agent safety: the monitoring agent's actions must be evaluated by a policy layer independent of the content it just ingested. For Security Copilot specifically: validate that automated actions (incident closure, severity downgrade) require a second confirmation step not driven by the same alert content that triggered the action. Reference: CSA MAESTRO (2025), Layer 5 — Compromised Monitoring Agents.

---

**Exercise / Lab:**

- **Name:** Agentic detection and response architecture in Sentinel
- **Format:** Individual
- **Description:**
  1. In Microsoft Sentinel → Analytics, create the rule "Agentic AI — Jailbreak Attempt Detected" using the KQL Library query (P05-Jailbreak-Detection.kql): frequency = 5 min, severity = High, entity mapping = AccountId
  2. Create the rule "Agentic AI — Volume Spike Anomaly" with a dynamic baseline using `percentile()` over a 7-day window — document why a fixed threshold fails for agent behavior
  3. In Azure Logic Apps, create the playbook `playbook-revoke-agent-token` that: receives the Sentinel alert, calls Graph API `POST /users/{id}/revokeSignInSessions`, adds a comment to the Sentinel incident, and sends an email to the agent's technical owner
  4. In Sentinel → Automation, create an automation rule that triggers the playbook when the alert name contains "Jailbreak"
  5. Complete the "Domain 5 — Detect & Respond" section of the Gap Assessment Template and consolidate the 90-day roadmap across all domains
- **Required tools:** Microsoft Sentinel (Analytics + Automation), Azure Logic Apps, Microsoft Graph API (Graph Explorer for validation), KQL Library P05, Gap Assessment Template
- **Deliverable:** Two active analytics rules + working Logic App playbook + automation rule configured + complete Gap Assessment Template with prioritized 90-day roadmap

---

**Closing questions for the facilitator:**
- When designing the dynamic baseline for the Volume Spike Anomaly rule, what time window did you use and why? How does that baseline change if the agent has very different usage patterns between weekdays and weekends?
- In the consolidated 90-day roadmap, which Gap Assessment control has the highest security ROI vs. implementation effort? What organizational (non-technical) obstacle most delays implementing that control?

**Track B consolidation:**
This module closes the Gap Assessment Template. Participants should now have:
- Agent inventory architecture with documented blind spots (Domain 01)
- Governance model configured in demo tenant (Domain 02)
- Valid CA policy for agents validated with What If (Domain 03)
- DLP policy for AI interactions + site inventory (Domain 04)
- Two active analytics rules + enforcement Logic App (Domain 05)

The completed Gap Assessment with 90-day roadmap is the formal Track B deliverable and the direct input for Track C (SOC Engineer), which operationalizes the detection and response architecture designed here.

→ [Track C — SOC Engineer Workshop](../Track-C-SOC-Engineer/README.md)
