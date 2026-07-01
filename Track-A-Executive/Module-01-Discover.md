# Module 01 — Discover & Prioritize | Track A

**Module duration:** 45 minutes

**Learning objective:**
By the end of this module, participants will be able to articulate the shadow AI risk for their organization, identify categories of agents that may be operating without visibility, and make an informed investment decision on inventory capabilities in the context of an enterprise security strategy.

**Module agenda:**

| Time | Activity | Type |
|------|----------|------|
| 10 min | The unmanaged AI problem: why inventory is the starting point of any strategy | Presentation |
| 10 min | Risk categories: Shadow AI, identity exposure, local agents without telemetry | Presentation |
| 20 min | Exercise: Agent risk map for your organization | Exercise |
| 5 min | Wrap-up: reflection questions and connection to Domain 2 | Discussion |

---

**Core content (points the facilitator must cover):**

1. **Shadow AI as the primary vector:** AI agents are being deployed today without formal approval — by business teams, individual developers, and external vendors. The risk is not hypothetical; it is the baseline condition of any organization with active M365 E5.

2. **The local agent blind spot:** Agents running on endpoints (outside the cloud) generate no telemetry in Defender or Purview. The gap is not a policy gap — it is a visibility gap. Without an active endpoint connector, there is no signal.

3. **Applicable Microsoft controls:** Purview DSPM for AI and Defender AI Agent Inventory enable a cloud agent inventory. SharePoint Advanced Management closes the data exposure those agents consume. Agent 365 provides the centralized registry.

4. **The cost of inaction:** Every unmanaged agent accessing SharePoint inherits the ACL errors of the corpus. A single agent with excessive access can expose sensitive data to every user who interacts with it.

---

**Exercise:**

- **Name:** Agent risk map
- **Format:** Individual, then group share-out
- **Description:**
  1. Participants receive a card with 8 possible agent categories (Copilot Studio, Power Automate with AI, third-party agents, local LLM scripts, HR/sales/IT agents, etc.)
  2. Mark which categories they believe exist in their organization today (with or without certainty)
  3. For each one marked: does it have an identified technical owner? Is it in any inventory?
  4. Calculate a "visibility score": percentage of marked agents with a known owner over total marked
  5. Share the result with the group and discuss which category generates the most surprise
- **Required tools:** Printed or digital card with the 8 categories (provided by facilitator); no system access required
- **Deliverable:** Personal visibility score + list of agent categories without an identified owner, added to the participant's Risk Posture Map

---

**Closing questions for the facilitator:**
- If your security team asked tomorrow "how many active AI agents does the organization have?", could you answer with certainty? What would prevent you from answering?
- Which agent category on the card created the most uncertainty, and what executive decision could reduce that uncertainty in the next 30 days?

**Connection to the next domain:** Visibility into the agent landscape is the first step — but visibility without ownership is a list with no accountable party. Domain 2 answers the governance question: who owns each agent, what policy governs it, and how is its lifecycle managed.

→ [Module 02 — Govern & Control](./Module-02-Govern.md)
