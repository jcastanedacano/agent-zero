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

   **Closing the local agent blind spot with Intune and Microsoft Defender for Endpoint:** For organizations with managed devices, two controls extend discovery to endpoint-hosted agents. (a) **Microsoft Defender for Endpoint** (MDE) discovers unsanctioned local agents running on managed devices and can apply security baselines that restrict common agent execution paths — if an MDE policy is active, a local LLM script running outside approved paths generates an alert. (b) **Intune** device compliance policies can require that local AI agents run inside **Windows Execution Containers** — Windows-based isolation environments where the agent is assigned a distinct Entra Agent ID and is subject to the same Conditional Access policies as cloud agents. Without Execution Containers, a local agent inherits the device user's identity and is invisible to CA. This is the only mechanism that brings local agents into the same governance perimeter as tenant-registered agents. Reference: [Zero Trust security for AI agents](https://techcommunity.microsoft.com/blog/microsoftmechanicsblog/zero-trust-security-for-ai-agents/4533091) (Microsoft Mechanics, 2026).

   ```mermaid
   flowchart TB
       A1["Copilot Studio and<br/>Azure AI Foundry agents"]
       A2["Power Automate<br/>with AI steps"]
       A3["Local agents<br/>Claude Code, MCP servers, LLM scripts"]
       S1["Telemetry in the<br/>AgentsInfo table"]
       S2["Events in the<br/>CloudAppEvents table"]
       S3["No cloud signal without an<br/>active endpoint connector<br/>structural blind spot"]
       MDE["Defender for Endpoint<br/>discovers unsanctioned local agents<br/>security baselines restrict<br/>execution paths"]
       INT{"Agent inside a Windows<br/>Execution Container?"}
       ALT["Alert when a local LLM script<br/>runs outside approved paths,<br/>if an MDE policy is active"]
       YES["Own Entra Agent ID, same<br/>Conditional Access as<br/>cloud agents"]
       NO["Inherits the device user<br/>identity, invisible to<br/>Conditional Access"]
       A1 --> S1
       A2 --> S2
       A3 --> S3
       S3 -- "managed devices" --> MDE
       S3 -- "managed devices: Intune can require it" --> INT
       MDE --> ALT
       INT -- "Yes" --> YES
       INT -- "No" --> NO
       classDef blue fill:#0078D4,stroke:#333,color:#fff
       classDef purple fill:#5E2750,stroke:#333,color:#fff
       classDef green fill:#107C10,stroke:#333,color:#fff
       classDef orange fill:#FF8C00,stroke:#333,color:#24292f
       class A1,A2,A3,S1,S2 blue
       class S3,NO orange
       class MDE,INT purple
       class ALT,YES green
   ```

   **How to read it.** Follow each agent type down its column: the signal it leaves and what remains uncovered. Copilot Studio, Foundry and Power Automate with AI steps leave a cloud signal, while local agents leave none until an endpoint control is in place. The Execution Container branch is the only one that gives a local agent its own Entra Agent ID and puts it under the same Conditional Access as tenant-registered agents.

2. **Shadow AI as the default state:** Agent Builder (M365 Copilot) allows any licensed user to create and share agents without admin review; only submitting an agent to the organization catalog (Agent Store) goes through admin approval in the Microsoft 365 admin center (Microsoft Learn, July 2026). These agents appear in Agent 365 Registry but without an Entra Agent ID, no technical owner, and no DLP review. They are not exceptions — they are the baseline case in any M365 E5 tenant with Copilot enabled.

3. **Applicable Microsoft controls:** Purview DSPM for AI maps agent interactions with sensitive data — it complements but does not replace identity inventory. Defender AI Agent Inventory requires active connectors per platform. SharePoint Advanced Management audits which sites are accessed by agents. Agent 365 is the central registry, but only covers registered agents.

   > **DSPM version note (GA May 2026):** Microsoft Purview shipped a new, unified version of Data Security Posture Management that supersedes the classic "DSPM for AI" this module has referenced. The new version covers both AI apps/agents and traditional data stores in one experience, extends to third-party SaaS and IaaS (Google Cloud Platform, Snowflake, Databricks), and integrates partner risk data (Varonis, Cyera, BigID, OneTrust). The classic DSPM for AI experience still exists and still works for tenants that haven't migrated, but new features land only in the unified version going forward. When configuring the lab, confirm which version the demo tenant is on before following portal navigation steps — menu paths differ between classic and unified. Reference: [Learn about Data Security Posture Management](https://learn.microsoft.com/purview/data-security-posture-management-learn-about), Microsoft Learn.

4. **The cost of an incomplete inventory:** An agent not listed in the inventory does not appear in Conditional Access policies, has no technical owner for escalation, and is not subject to Sentinel analytics rules. The inventory gap is the gap across every subsequent security layer.

5. **PHANTOM-B — the threat modeling lens for every agent the inventory finds:** An inventory answers which agents exist. The immediately following question is what can go wrong with each one, and that is where most teams run out of method. PHANTOM-B (Adam Shostack, 2026) is the STRIDE analog for LLMs, written by STRIDE's own author: an eight-threat mnemonic aimed at whoever **consumes** an LLM rather than whoever trains one, which is exactly the position of an organization deploying Copilot or agents on Azure AI Foundry.

   | Letter | Threat | Question it triggers about each agent in the inventory |
   |--------|--------|-------------------------------------------------------|
   | **P** | Prompt injection | Which untrusted inputs reach this agent, directly or via corpus and tool responses? |
   | **H** | Hallucination | What happens downstream if the answer is plausible and wrong? |
   | **A** | Anthropomorphization | Are we assuming intent, guilt, or compliance where there is only token prediction? |
   | **N** | Non-explainability | When do we have to justify the output, to whom, and with what evidence? |
   | **T** | Training issues | What do we know about the model's origin, its data, and its fine-tuning? |
   | **O** | Over-reliance | Which decisions does this agent make without review, and what is the blast radius? |
   | **M** | Missing security engineering | Did we do the ordinary security engineering, or did the LLM displace it? |
   | **B** | Biases | Which biases does it inherit, and in this use case are they acceptable or a legal problem? |

   Three reasons to use it in this module rather than later: (a) it is cheap to learn and cheap to apply, unlike MAESTRO or ATLAS, which makes it the only framework in this series a team can adopt in a single meeting; (b) Shostack designed it as **prompts, not a taxonomy** — the point is not to file each threat into its bucket but to verify that at least one of each kind was considered, which is exactly what is needed when walking a freshly built inventory; (c) it deliberately contains no controls or mitigations, which makes it complementary to Modules 02 through 07 of this track rather than a competitor to them, since those are precisely the controls.

   **The uncomfortable point worth discussing with the group:** Shostack argues that calling AI "agentic" is itself an instance of anthropomorphization, one of his eight threats. That is a direct critique of this workshop's vocabulary, and it is better put on the table than avoided. The operational argument behind it: if you assume the system has intent, you also assume it understands a "do not do X" instruction and will respect it. Two concrete errors follow, both of which this track corrects later: approving what the agent *says* it will do instead of the actual command (Module 02, point 5), and believing that a "stop" in the system prompt is a kill switch (Module 02, point 10).

   Reference: Adam Shostack, "PHANTOM-B: A STRIDE Analog for LLMs", Shostack + Associates White Paper #6, July 2026, CC-BY.

---

**Exercise / Lab:**

- **Name:** Agent inventory architecture design
- **Format:** Pairs
- **Description:**
  1. Open Microsoft Defender XDR → AI Agent Inventory; verify which connectors are active and which tables return data
  2. In Sentinel → Logs, run the full `AgentsInfo` inventory query from the KQL Library (P01-Agent-Discovery.kql) and document the count by platform and lifecycle status
  3. Identify which categories of agents in the organization's environment will NOT appear in this inventory (local agents, third-party without connector, etc.) — document as blind spots
  4. Design a telemetry flow diagram: which agent → which connector → which table → which query detects it → which control applies
  5. **PHANTOM-B pass over the inventory:** pick the three highest-exposure agents from step 2 and, for each one, walk the eight letters answering with a single sentence per threat. Do not aim for exhaustiveness: the goal is to find which of the eight the team has no answer for at all, because that is the real gap. Record the result as a 3-agent by 8-threat matrix
  6. Complete the "Domain 1 — Discover" section of the Gap Assessment Template
- **Required tools:** Microsoft Defender XDR (AI Agent Inventory), Microsoft Sentinel (Logs), KQL Library (repository), PHANTOM-B (table in point 5 of this module), Gap Assessment Template
- **Deliverable:** Telemetry flow diagram + PHANTOM-B matrix of 3 agents x 8 threats + Domain 1 section of the Gap Assessment completed with real agent count, identified blind spots, and control recommendations

---

**Closing questions for the facilitator:**
- In your diagram, how many agent types fell outside the cloud inventory? What endpoint architecture (MDE onboarding, local sensor) would close those blind spots?
- If you had to present the agent inventory to a risk committee next week, what result from the query you ran would generate the most questions from the committee, and how would you answer?

**Connection to the next domain:** Inventory is the input to the governance process. Without knowing which agents exist, it is not possible to assign owners or create policies. Domain 2 takes the agent list from inventory and answers: who is responsible for each one, what process approves them, and how is their lifecycle managed?

→ [Module 02 — Govern & Control](./Module-02-Govern.md)
