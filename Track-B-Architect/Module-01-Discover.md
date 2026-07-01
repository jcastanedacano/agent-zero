# Module 01 — Discover & Prioritize | Track B

**Module duration:** 90 minutes

**Learning objective:**
By the end of this module, participants will be able to design an agent inventory architecture covering cloud sources and endpoints, configure Defender AI Agent Inventory and Purview DSPM for AI in a demo tenant, identify structural inventory blind spots, and produce a visibility gap assessment for their organization.

**Module agenda:**

| Time | Activity | Type |
|------|----------|------|
| 20 min | Discovery architecture: sources, tables, connectors, and blind spots by agent type | Presentation |
| 15 min | Walk-through of `AgentsInfo`: schema, key fields, documented limitations | Presentation |
| 45 min | Lab: Activate Defender AI Agent Inventory + inventory KQL | Lab |
| 10 min | Gap assessment: design the organization's visibility map | Discussion |

---

**Core content (points the facilitator must cover):**

1. **Discovery topology by agent type:** Copilot Studio and Azure AI Foundry generate telemetry in `AgentsInfo`. Power Automate with AI steps appears in `CloudAppEvents`. Local agents (Claude Code, MCP servers, LLM scripts) generate no cloud signal without an active endpoint connector — this is the structural blind spot that no Purview or Defender control resolves on its own.

2. **Shadow AI as the default state:** Agent Builder (M365 Copilot) allows any licensed user to create and publish agents without approval. These agents appear in Agent 365 Registry but without an Entra Agent ID, no technical owner, and no DLP review. They are not exceptions — they are the baseline case in any M365 E5 tenant with Copilot enabled.

3. **Applicable Microsoft controls:** Purview DSPM for AI maps agent interactions with sensitive data — it complements but does not replace identity inventory. Defender AI Agent Inventory requires active connectors per platform. SharePoint Advanced Management audits which sites are accessed by agents. Agent 365 is the central registry, but only covers registered agents.

4. **The cost of an incomplete inventory:** An agent not listed in the inventory does not appear in Conditional Access policies, has no technical owner for escalation, and is not subject to Sentinel analytics rules. The inventory gap is the gap across every subsequent security layer.

---

**Exercise / Lab:**

- **Name:** Agent inventory architecture design
- **Format:** Pairs
- **Description:**
  1. Open Microsoft Defender XDR → AI Agent Inventory; verify which connectors are active and which tables return data
  2. In Sentinel → Logs, run the full `AgentsInfo` inventory query from the KQL Library (P01-Agent-Discovery.kql) and document the count by platform and lifecycle status
  3. Identify which categories of agents in the organization's environment will NOT appear in this inventory (local agents, third-party without connector, etc.) — document as blind spots
  4. Design a telemetry flow diagram: which agent → which connector → which table → which query detects it → which control applies
  5. Complete the "Domain 1 — Discover" section of the Gap Assessment Template
- **Required tools:** Microsoft Defender XDR (AI Agent Inventory), Microsoft Sentinel (Logs), KQL Library (repository), Gap Assessment Template
- **Deliverable:** Telemetry flow diagram + Domain 1 section of the Gap Assessment completed with real agent count, identified blind spots, and control recommendations

---

**Closing questions for the facilitator:**
- In your diagram, how many agent types fell outside the cloud inventory? What endpoint architecture (MDE onboarding, local sensor) would close those blind spots?
- If you had to present the agent inventory to a risk committee next week, what result from the query you ran would generate the most questions from the committee, and how would you answer?

**Connection to the next domain:** Inventory is the input to the governance process. Without knowing which agents exist, it is not possible to assign owners or create policies. Domain 2 takes the agent list from inventory and answers: who is responsible for each one, what process approves them, and how is their lifecycle managed?

→ [Module 02 — Govern & Control](./Module-02-Govern.md)
