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

6. **The compromised monitoring agent problem (MAESTRO Layer 5):** The CSA MAESTRO framework identifies a class of threat specific to Layer 5 (Evaluation & Observability): the monitoring agent itself becomes a target. When Security Copilot or a custom triage agent ingests alert context, that context can contain adversarially crafted content — LPCI via tool responses (KQL P05-Q7) is the most concrete example. An agent that processes alert summaries containing injected instructions may suppress, misclassify, or modify incident records. The control is the same as for all agent safety: the monitoring agent's actions must be evaluated by a policy layer independent of the content it just ingested. For Security Copilot specifically: validate that automated actions (incident closure, severity downgrade) require a second confirmation step not driven by the same alert content that triggered the action. Reference: CSA MAESTRO (2025), Layer 5 — Compromised Monitoring Agents.

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
