# Module 04 — Protect Data | Track A

**Module duration:** 45 minutes

**Learning objective:**
By the end of this module, participants will be able to evaluate the data exfiltration risk through AI agents in their organization, identify classification and labeling gaps that amplify that risk, and make investment decisions on data protection controls in the context of a Microsoft Purview environment.

**Module agenda:**

| Time | Activity | Type |
|------|----------|------|
| 10 min | How agents become exfiltration vectors: prompts, responses, and connectors | Presentation |
| 10 min | The unlabeled corpus problem: oversharing and SharePoint as an attack surface | Presentation |
| 20 min | Exercise: Exfiltration scenario analysis and prioritization decision | Exercise |
| 5 min | Wrap-up and connection to Domain 5 | Discussion |

---

**Core content (points the facilitator must cover):**

1. **Prompt injection as an exfiltration vector:** An agent with SharePoint access can be manipulated through instructions embedded in documents it reads — the so-called "poisoned corpus." The agent executes malicious instructions as if they came from a legitimate user, without any alert signal in standard activity logs.

2. **The oversharing multiplier effect:** An ACL error in SharePoint (a site that should be confidential but is shared with everyone) is a manageable problem for human users — only those who actively search will find it. For an agent, that error is amplified: every user who interacts with the agent can retrieve the content through prompts.

3. **Applicable Microsoft controls:** Purview DLP can be configured to detect sensitive data in AI agent interactions (prompts and responses), not just in emails and documents. Sensitivity labels applied to SharePoint sites restrict what the agent can index. SharePoint Advanced Management audits and remediates oversharing at the site and site collection level. Insider Risk Management detects exfiltration patterns by volume and data type.

4. **Remediation order matters:** Enabling agent retrieval on a SharePoint site before applying sensitivity labels and remediating ACL errors creates an active exposure window. The correct order is: label → audit ACLs → enable retrieval.

---

**Exercise:**

- **Name:** Data risk triage
- **Format:** Individual
- **Description:**
  1. Participants receive a list of 6 fictional SharePoint sites with different characteristics: labeled (yes/no), ACL status (clean/with oversharing), and whether the agent already has retrieval enabled
  2. Classify each site on a risk scale: Critical / High / Medium / Low
  3. Prioritize the remediation order for the 3 highest-risk sites, justifying the sequence
  4. Identify which of the 6 sites represents the "poisoned corpus" scenario and explain why
  5. Record the two highest-risk sites in the "Domain 4" section of the Risk Posture Map
- **Required tools:** Fictional site table (provided by facilitator); no system access required
- **Deliverable:** Prioritized remediation list with justification + two highest-risk sites in the Risk Posture Map

---

**Closing questions for the facilitator:**
- Do you today have an inventory of the SharePoint sites you use (or plan to use) as knowledge sources for AI agents? Do you know which ones have sensitivity labels applied?
- If an external auditor asked tomorrow what data your AI agents can access, could you answer with certainty? What would give you that certainty?

**Connection to the next domain:** Protecting data reduces the attack surface, but does not eliminate the possibility of an attack occurring. Domain 5 closes the loop: how to detect when an agent is being manipulated or behaving anomalously, and how to respond with a process the SOC can execute.

→ [Module 05 — Detect & Respond](./Module-05-DetectRespond.md)
