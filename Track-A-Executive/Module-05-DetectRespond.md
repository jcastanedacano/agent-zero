# Module 05 — Detect & Respond | Track A

**Module duration:** 45 minutes

**Learning objective:**
By the end of this module, participants will be able to evaluate their organization's detection and response capability against agentic incidents, identify gaps between the current detection posture and what an AI agent integrated into the SOC requires, and make investment and prioritization decisions to reduce response time for agent-generated incidents.

**Module agenda:**

| Time | Activity | Type |
|------|----------|------|
| 10 min | Agents as a security signal: why the SOC needs an agentic AI-specific layer | Presentation |
| 10 min | Structural false negatives: why generic detections fall short for agents | Presentation |
| 20 min | Exercise: Crisis table — agentic incident decision simulation | Roleplay |
| 5 min | Wrap-up and Risk Posture Map consolidation | Discussion |

---

**Core content (points the facilitator must cover):**

1. **Jailbreak as an incident vector:** A successful jailbreak converts the agent into an executor of malicious instructions with legitimate system access. Unlike malware, a compromised agent operates within authorized channels — making perimeter defenses insufficient.

2. **Agent anomaly vs. user anomaly:** Detection tools calibrated for human behavior generate structural false negatives when monitoring agents. An agent making 5,000 SharePoint calls in an hour may be operating normally or executing an attack — the difference is in the pattern, not the volume.

3. **Applicable Microsoft controls:** Defender XDR integrates agent behavioral signals. Microsoft Sentinel with the native MCP server allows querying agent status from within an active investigation context. Security Copilot accelerates triage of agentic incidents. Purview Audit provides the forensic chain of custody. Agent 365 correlates incident events with the agent ownership registry.

4. **MTTR targets for agents:** A SOC's standard human response time (30 min – 2 hours for containment) may be inadequate for a compromised agent acting in seconds. The target should be automated initial containment with subsequent human review.

---

**Exercise:**

- **Name:** Crisis table: agentic incident
- **Format:** Group (full room, facilitator as moderator)
- **Description:**
  1. Facilitator presents the scenario: "At 2:47 AM, an on-call analyst receives a Sentinel alert: the customer service agent attempted to access a SharePoint site classified as Confidential 847 times in 3 minutes. The agent has read permission on that site, so the alert does not block access."
  2. Facilitator asks key questions to the group: Do you revoke the agent token immediately? Do you escalate to CISO? Do you notify customers?
  3. Group debates each decision; facilitator records points of disagreement
  4. Facilitator reveals the outcome: the access was legitimate — a scheduled indexing process. But the organization had no documentation of the agent's expected behavior. Discussion: how would you have differentiated a real incident from a false positive?
  5. Each participant records in their Risk Posture Map: does their organization have a documented baseline of expected behavior for its agents?
- **Required tools:** Scenario description (projected); whiteboard or digital board to record group decisions
- **Deliverable:** Completed Risk Posture Map with all 5 sections filled in (one per module) — the final Track A deliverable

---

**Closing questions for the facilitator:**
- Does your SOC today have specific alerts for anomalous AI agent behavior, or does it use the same alerts configured for human users?
- If you had to revoke a compromised agent's access in the next 5 minutes, do you know who would need to do what, and in which system?

**Track A consolidation:**
This module closes the Risk Posture Map. Participants should now have:
- An agent visibility score (Domain 01)
- A governance maturity level (Domain 02)
- A documented access decision (Domain 03)
- A prioritized SharePoint site list for remediation (Domain 04)
- A detection and response capability status (Domain 05)

The completed Risk Posture Map is the input for commissioning Track B (architects) and Track C (SOC engineers) within the participant's organization.
