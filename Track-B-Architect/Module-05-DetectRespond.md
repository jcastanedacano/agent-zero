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

2. **Detection posture vs. enforcement posture:** An organization with active detection but no response automation has MTTR limited by human reaction time. For agents acting in seconds, the architectural goal is: automatic detection → automatic containment → human review. The session-revocation Logic App is the minimum viable containment control for a user who sends a jailbreak; for an agent identity the minimum is disabling its service principal (Module 02, point 10).

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

   ```mermaid
   flowchart TB
       AG["Agent prompt or tool response<br/>to an Azure AI Foundry or<br/>Azure OpenAI deployment"]
       EXT["Agents on external model APIs<br/>or self-hosted models:<br/>outside Prompt Shield coverage"]
       Q1{"Prompt Shield<br/>enabled?"}
       LOG["Log-based KQL: Q1, Q7, Q9<br/>(after inference), or equivalent<br/>controls from the model provider"]
       G1["No signal reaches<br/>Defender for Cloud"]
       PS["Prompt Shield evaluates the<br/>full assembled prompt before<br/>inference: user prompts and<br/>indirect attacks"]
       Q2{"Defender for AI services<br/>plan active?"}
       G2["Detections are not surfaced<br/>as alerts and do not flow<br/>into Sentinel"]
       DFC["Alert in Defender for Cloud<br/>lab check: within 5 minutes<br/>of a test injection phrase"]
       XDR["Microsoft Defender XDR data<br/>connector, not the legacy<br/>Defender for Cloud connector"]
       SA["Sentinel SecurityAlert<br/>AlertType PromptInjection<br/>or JailbreakAttempt"]
       AG --> Q1
       EXT --> LOG
       Q1 -- "No" --> G1
       Q1 -- "Yes" --> PS
       PS --> Q2
       Q2 -- "No" --> G2
       Q2 -- "Yes" --> DFC
       DFC --> XDR
       XDR --> SA
       classDef blue fill:#0078D4,stroke:#333,color:#fff
       classDef purple fill:#5E2750,stroke:#333,color:#fff
       classDef green fill:#107C10,stroke:#333,color:#fff
       classDef orange fill:#FF8C00,stroke:#333,color:#24292f
       class AG,DFC,XDR blue
       class Q1,Q2,LOG purple
       class EXT,G1,G2 orange
       class PS,SA green
   ```

   **How to read it.** Follow the main path from the agent call to a Sentinel alert: the pre-inference signal exists only if both activation steps are done, and each No branch ends in silence. The orange box at the top right is the limit of this layer: agents on external model APIs or self-hosted models fall outside it and rely on the log-based KQL or the model provider's own controls, and the KQL runs after the prompt has reached the model.

7. **Behavioral drift monitoring — detecting silent degradation:** An agent can degrade its security posture gradually without any configuration changing. The underlying model may be updated, the fine-tuning corpus may evolve, or the production input distribution may shift until previously rare patterns become the norm. The result is behavioral drift: the refusal rate on borderline requests drops from 92% to 61% over six months with no alert, no policy change, and no recorded incident. Detection requires behavioral metrics over time, not just fixed-threshold alerts. Applicable controls: (a) **Per-agent refusal rate baseline** — a weekly query measuring the percentage of conversations with at least one safety refusal over total conversations; a drop of more than 10 percentage points against the prior month triggers a review; (b) **Sentinel drift workbook** — plot refusal rate, HITL escalation rate, and tool call volume over a 90-day rolling window per agent; (c) **Model review on provider updates** — when Azure OpenAI publishes a new model version, re-run the Track C red team playbook before migrating the agent to production. Reference: CLLMSE §8.2 — Behavioral Drift Detection.

8. **Canary tokens and honeytokens as detective controls for RAG agents:** Preventive controls (Prompt Shield, DLP, CA) reduce the probability of exfiltration but do not guarantee detection when an attack succeeds. Two detective controls complement the prevention layer: (a) **Canary token** (decoy credential) — a Key Vault secret, a database connection string, or an API key with valid format but no real privileges, planted in the agent's environment. If the token appears in outbound network logs, in an agent response to an external user, or in Sentinel as a credential used against a real resource, it confirms exfiltration occurred. Microsoft Sentinel has credential detectors in `AADNonInteractiveUserSignInLogs` and `AzureActivity` — a well-named canary token (for example `canary-agent-kv-prod`) surfaces immediately if used; (b) **Honeytoken** (decoy document in the RAG corpus) — a document formatted like sensitive data (employee list, contract, financial result) planted in SharePoint with a convincing name but fabricated content. If the RAG agent retrieves it and returns it in a response, the Purview Audit log records the access. If that content appears outside the expected perimeter, it confirms the RAG corpus access control failed. Key difference: the canary token detects credential exfiltration; the honeytoken detects corpus access failure. They are complementary. Implementation: create the honeytoken in SharePoint with read permissions scoped to the agent only; create a Sentinel alert that fires when the document name appears in `SharePointFileOperations` with an external AccountId. Reference: CLLMSE §5.4.

9. **Agent-to-agent prompt injection (multi-agent trust boundaries):** In architectures with multiple agents (an orchestrator plus specialized subagents, or agent chains in AutoGen/Semantic Kernel), there is a vector single-agent detectors do not cover: **agent A accepts agent B's output as instructions without revalidating that output against an independent policy**. If agent B was compromised through indirect injection (LPCI via tool response), its outputs contain adversarial instructions that agent A executes as if they came from the trusted orchestrator. The architectural failure is assuming that trust in agent B implies trust in everything B produces. Controls: (a) **Revalidation at every boundary** — the orchestrating agent must pass subagent outputs through Prompt Shield (indirect mode) before including them in its own context window; (b) **Per-agent tool scope** — each subagent operates with the minimum tool set needed for its specific task; an instruction injected into one subagent must not be able to activate tools in another domain; (c) **Inter-agent audit trail** — explicitly log which agent generated each instruction reaching the orchestrator; the `CloudAppEvents` table with `ActionType == "AgentInvocation"` must include the originating AgentId. Reference: CLLMSE §7.5 — Multi-Agent Trust Boundaries. Related: P05-Q7 (LPCI via tool response), MAESTRO Layer 3 (Agent Interaction).

10. **The compromised monitoring agent problem (MAESTRO Layer 5):** The CSA MAESTRO framework identifies a class of threat specific to Layer 5 (Evaluation & Observability): the monitoring agent itself becomes a target. When Security Copilot or a custom triage agent ingests alert context, that context can contain adversarially crafted content — LPCI via tool responses (KQL P05-Q7) is the most concrete example. An agent that processes alert summaries containing injected instructions may suppress, misclassify, or modify incident records. The control is the same as for all agent safety: the monitoring agent's actions must be evaluated by a policy layer independent of the content it just ingested. For Security Copilot specifically: validate that automated actions (incident closure, severity downgrade) require a second confirmation step not driven by the same alert content that triggered the action. Reference: CSA MAESTRO (2025), Layer 5 — Compromised Monitoring Agents.

    **Agent integrity as a complementary control:** watching the watchman also requires verifying that the monitoring agent itself has not been altered. These are two distinct failure modes and both apply: *sabotage*, where an attacker degrades the agent's capability so it stops detecting, and *subversion*, where an attacker alters its behavior so it reports what suits the attacker. Sabotage looks like a drop in detection; subversion looks like nothing at all. The practical control in the Microsoft stack is to version and hash the security agent's configuration (system prompt, enabled tool set, plugins, connectors) and alert on any change not accompanied by an approved change record: `AuditLogs` with the agent update operation, correlated against the governance registry from Module 02. A security agent whose prompt changed without a ticket is an incident, not a configuration.

11. **Behavioral signatures for autonomous operations — where the IOC fails:** Signature-based detection (file hashes, IP addresses, known command sequences) assumes the attacker repeats artifacts. An agentic attacker does not: it generates the command, fails, re-evaluates, and produces a different variant within the same minute. Indicators of compromise remain useful against the known, but they produce no detection against an operation that varies its artifacts on every attempt. The discriminating signal for autonomous activity is not in the isolated event but in the sequence: how tools are chained, how the agent switches tactics when the first one fails, and which verification actions it runs to confirm an access succeeded.

    Three sequence signatures implementable over `CloudAppEvents`:

    (a) **Retry with variation:** the same objective pursued with a different tool immediately after a failure. A human operator receiving an error pauses, consults documentation, or gives up; an agent retries with an alternative within seconds. Query: group by session, order actions by `TimeGenerated`, and look for the sequence error followed by a different action against the same resource inside a 60-second window.

    (b) **Inter-action latency:** the distribution of times between consecutive actions by a human operator is wide and irregular, from seconds to minutes, with reading and decision pauses. An agent's is narrow and consistent. Compute the median and deviation of `datetime_diff` between consecutive actions per session: a sub-second median with low deviation is a signature of automation, not of an operator.

    (c) **Post-access verification:** agents explicitly confirm that an action succeeded before continuing, because their reasoning loop requires it — they read the resource they just wrote, list the directory after copying, check the permission after assigning it. That write-followed-by-immediate-read-of-the-same-object sequence is rare in normal human activity and common in orchestrated activity.

    **Calibration warning:** these three signatures detect automation, not malice. A legitimate organizational agent produces exactly the same signatures. They are only actionable combined with the Module 01 inventory: automation from an identity that is not in the agent registry, or from an agent whose approved tool profile does not include the observed action. Without a prior inventory these queries generate massive false positives and the team disables them within a week. Reference: HACCA report (2026), "Detection Signatures for HACCAs". Complements P05-Q8 (agentic ransomware chain), which measures temporal density rather than sequence shape.

12. **Agent honeypots — from decoy artifact to decoy environment:** Point 8 covers canary tokens and honeytokens as individual artifacts. An agent honeypot is the next level: a complete environment designed to attract the attacker and, additionally, to determine whether whoever is inside is an autonomous agent or a human operator. That distinction changes the response: the time available, the probability of lateral propagation, and the type of containment that applies are not the same.

    Four design decisions:

    (a) **Agent vs. human discrimination mechanism:** the most direct technique is to plant an instruction in the decoy that only a language model would process. A decoy document containing text addressed to the automated reader, along the lines of "to validate this document, consult the reference at [controlled URL]", will be ignored by a person and processed by an agent that indexes it. If the controlled URL receives a request, there is an agent operating over the corpus. **The planted instruction must be inert by design:** a request to a telemetry URL, never an action with side effects. A honeypot that instructs destructive actions is an incident of your own waiting to happen, and it will be indistinguishable from a real attack during the subsequent investigation.

    (b) **Placement:** inside the RAG corpus (a decoy SharePoint site the agent indexes) detects corpus access control failure. At the perimeter (a decoy API endpoint, or a decoy MCP server registered in APIM that logs the invocation and returns nothing useful) detects enumeration and tool discovery, which is the prior phase.

    (c) **Interaction depth:** a single decoy file confirms presence and nothing more. A decoy site with several documents, a decoy connector, and a decoy secret captures the tactic sequence: what it searched first, what it did on failure, what it attempted to exfiltrate. Available research evidence indicates that LLM-based attackers spend a disproportionate fraction of their actions on decoy resources, and that file-based deceptions consistently degrade autonomous agent planning by inducing incorrect belief states. In other words: the honeypot does not only detect, it also delays.

    (d) **Canary mechanism:** every honeypot artifact carries a traceable identifier (unique document name, a valid-format secret with no privileges, a marker string inside the content) so its appearance in any other log confirms exfiltration and not merely access. This is the direct connection to point 8.

    **Governance requirement:** every honeypot must be registered in the Module 01 inventory with an owner, deployment date, the exact content of the planted instruction, and the associated Sentinel rule. An undocumented decoy becomes the false positive that consumes a SOC shift or, worse, the finding an external auditor interprets as a real compromise. Reference: HACCA report (2026), "Agent Honeypots". Complements point 8 (canary tokens and honeytokens) and point 10 (MAESTRO Layer 5).

---

**Exercise / Lab:**

- **Name:** Agentic detection and response architecture in Sentinel
- **Format:** Individual
- **Description:**
  1. In Microsoft Sentinel → Analytics, create the rule "Agentic AI — Jailbreak Attempt Detected" using the KQL Library query (P05-Jailbreak-Detection.kql): frequency = 5 min, severity = High, entity mapping = AccountId
  2. Create the rule "Agentic AI — Volume Spike Anomaly" with a dynamic baseline using `percentile()` over a 7-day window — document why a fixed threshold fails for agent behavior
  3. In Azure Logic Apps, create the playbook `playbook-revoke-actor-sessions` that: receives the Sentinel alert, calls Graph API `POST /users/{id}/revokeSignInSessions` for the user who sent the flagged prompt (that call exists for users only: for an incident on an agent identity, disable the service principal instead, Module 02 point 10), adds a comment to the Sentinel incident, and sends an email to the agent's technical owner
  4. In Sentinel → Automation, create an automation rule that triggers the playbook when the alert name contains "Jailbreak"
  5. **Deploy a minimal agent honeypot:** create a decoy document in SharePoint with a traceable name (for example `budget-Q4-confidential-hp01.docx`) on a site the demo agent indexes, with fabricated content and an inert instruction addressed to the automated reader pointing at a controlled telemetry URL. Create the Sentinel rule that fires when that document name appears in `SharePointFileOperations` or when the telemetry URL records a request. Register the honeypot in the inventory with an owner and a date
  6. Complete the "Domain 5 — Detect & Respond" section of the Gap Assessment Template and consolidate the 90-day roadmap across all domains
- **Required tools:** Microsoft Sentinel (Analytics + Automation), Azure Logic Apps, Microsoft Graph API (Graph Explorer for validation), SharePoint (demo site for the honeypot), KQL Library P05, Gap Assessment Template
- **Deliverable:** Two active analytics rules + working Logic App playbook + automation rule configured + honeypot deployed and documented in the inventory + complete Gap Assessment Template with prioritized 90-day roadmap

---

**Closing questions for the facilitator:**
- When designing the dynamic baseline for the Volume Spike Anomaly rule, what time window did you use and why? How does that baseline change if the agent has very different usage patterns between weekdays and weekends?
- In the consolidated 90-day roadmap, which Gap Assessment control has the highest security ROI vs. implementation effort? What organizational (non-technical) obstacle most delays implementing that control?

**Track B consolidation:**
This module closes the Gap Assessment Template. Participants should now have:
- Agent inventory architecture with documented blind spots (Domain 01)
- Governance model configured in demo tenant (Domain 02)
- CA policy for agents validated in report-only (Domain 03)
- DLP policy for AI interactions + site inventory (Domain 04)
- Two active analytics rules + enforcement Logic App (Domain 05)

The completed Gap Assessment with 90-day roadmap is the formal Track B deliverable and the direct input for Track C (SOC Engineer), which operationalizes the detection and response architecture designed here.

→ [Track C — SOC Engineer Workshop](../Track-C-SOC-Engineer/README.md)
