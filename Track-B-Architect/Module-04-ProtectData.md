# Module 04 — Protect Data | Track B

**Module duration:** 90 minutes

**Learning objective:**
By the end of this module, participants will be able to design a data protection architecture for AI agents covering classification, DLP on interactions, and exfiltration auditing; configure a Purview DLP policy for AI interactions in a demo tenant; audit oversharing on SharePoint sites used as knowledge sources; and document the correct remediation order before enabling retrieval.

**Module agenda:**

| Time | Activity | Type |
|------|----------|------|
| 20 min | Data protection architecture for agents: layers, vectors, and the oversharing multiplier effect | Presentation |
| 15 min | Purview DLP for AI interactions: differences vs. traditional DLP, coverage, and limitations | Presentation |
| 45 min | Lab: DLP policy for AI interactions + sensitivity label audit + exfiltration KQL | Lab |
| 10 min | Gap assessment: data protection and labeling roadmap | Discussion |

---

**Core content (points the facilitator must cover):**

1. **The oversharing multiplier effect:** An ACL error in SharePoint that exposes a confidential site to all users is a manageable risk for humans — it requires someone to actively search. For an agent with retrieval enabled, that error is amplified to every user who interacts with the agent: exposure is passive and automatic. The agent does not discriminate between sensitive and non-sensitive content — it indexes everything it can read.

2. **Prompt injection over a poisoned corpus:** An attacker with write access to SharePoint documents can embed malicious instructions that the agent executes as if they came from a legitimate user. The agent does not validate the source of instructions — it simply executes them. This vector generates no alerts in standard user activity logs.

3. **Applicable Microsoft controls:** Purview DLP configured on "AI interactions" covers prompts and responses in Microsoft 365 Copilot and other agents — not just documents and emails. Sensitivity labels applied to SharePoint sites restrict the agent's index. SharePoint Advanced Management audits and remediates oversharing at the site and site collection level. Insider Risk Management detects exfiltration patterns by volume and data type.

4. **Remediation order as an architectural control:** Enabling retrieval before applying labels and remediating ACLs creates an active exposure window that can last weeks. The correct order is: (1) classify and label all candidate sites, (2) audit and remediate ACL errors, (3) enable agent retrieval. Inverting this order is the most common error in agent deployments that access SharePoint.

5. **Three levels of corpus/memory poisoning:** (a) SharePoint corpus: malicious documents the agent indexes — detectable with P04 KQL Library Q3. (b) Memory/session poisoning: malicious instructions injected into the agent's persistent memory — affects all future user interactions. (c) Model supply chain: Souly et al. document that roughly 250 poisoned training documents suffice to backdoor models up to 13B parameters, with persistence through safety training — critically, the number is near-constant rather than proportional to model size or dataset volume, so scaling the model does not dilute the attack ([arXiv:2510.07192](https://arxiv.org/abs/2510.07192)) — not detectable with KQL; requires provider evaluation and post-deployment behavioral drift monitoring (P05-Q6 KQL Library).

6. **Context as the new attack surface — the context gap:** Protecting data at the output layer (DLP on responses) is necessary but not sufficient. The input layer — what data the agent receives as context — is an equally critical attack surface. Researchers document production cases where AI agents in autonomous SOC workflows made catastrophically wrong decisions because the context they received was stale, misrouted, or acted on the wrong data object. The agent was doing exactly what it was designed to do; the data was wrong. Three controls address this: (a) **Data classification before context injection** — label and classify all data before it enters any agent workflow; an ungoverned document that reaches an agent's context window is an unguarded perimeter. (b) **Data minimization at the data-to-agent boundary** — pass only the fields and records the agent strictly requires for its assigned task; full-document retrieval expands blast radius unnecessarily. (c) **Attribute-based access control (ABAC) for agents** — access decisions must evaluate content sensitivity, agent role, and workflow context simultaneously, not just identity. ABAC is more precise than role-based access alone for the dynamic, multi-step nature of agentic workflows. Audit logs must capture not just what the agent *did* but what data it *saw as context* — this is the evidence required for post-incident reconstruction.

7. **Cross-tenant vector search leakage — the access control that fails silently (OWASP LLM09:2026):** In multi-tenant deployments using Azure AI Search or any shared vector store, similarity search typically executes across the **entire index before access filters are applied**. The result: a document belonging to Tenant A can be returned as a relevant result for a Tenant B query if both share the same vector index. The model does not distinguish between "this chunk is yours" and "this chunk belongs to another tenant" — it sees tokens, not ACLs. This vector differs from prompt injection (LLM01) because it requires no malicious instruction: it is a geometric failure of the embedding space, not an instruction-following failure. A perfectly benign document can leak across tenants if cosine similarity retrieves it before the access filter runs. Controls in Azure AI Search: (a) **Security trimming** — Azure AI Search supports `$filter` with per-document security fields (a `tenantId` field or a serialized ACL); configure security trimming as a production requirement, not an optional optimization, because without that parameter the search returns results from every tenant; (b) **Separate indexes per tenant** — architecturally the safest option: each tenant gets its own index, eliminating the geometric risk by design at the cost of higher operational complexity; (c) **Row-level access control in the corpus** — every document in the index must carry an `allowedTenants` field or equivalent that the search filter validates on every query; documents without that field should be rejected at ingestion, not silently dropped at search time; (d) **Retrieval audit** — log which documents were retrieved for each query and by which tenant, to detect anomalous cross-tenant retrievals. Reference: OWASP LLM Top 10 2026, LLM09 — Vector and Embedding Weaknesses, Common Example #1 (Cross-Tenant Leakage via Shared Similarity Search).

8. **Multi-agent trust boundaries as an escalation vector:** A compromised agent that can invoke other agents pivots to new blast radii with their own permissions. The correct architectural design treats every agent-to-agent call as an untrusted call: verify explicit user authorization and limit inherited permissions between agents. Reference: Anthropic Zero Trust for AI Agents.

9. **Membership inference — privacy without visible exfiltration:** If a model was fine-tuned with personal data (employee PII, customer data, medical records), an attacker can infer whether a specific record was in the training set by systematically querying the model and analyzing response patterns — without extracting the data directly. The risk is a privacy violation undetectable by DLP or standard Purview audit. Architectural controls: (a) do not fine-tune with PII without differential anonymization, (b) use Foundry RBAC to restrict who can query models fine-tuned with sensitive data, (c) monitor inference volume by identity. OWASP Agentic AG07.

---

**Exercise / Lab:**

- **Name:** Data protection architecture for agents in demo tenant
- **Format:** Individual
- **Description:**
  1. In Microsoft Purview compliance portal → Data loss prevention → Policies, create the policy "Agentic AI — Sensitive Data in AI Interactions": workload = AI interactions, rule = Credit Card Number in prompt or response, action = Block + notify + audit
  2. In SharePoint admin center, use SharePoint Advanced Management to audit oversharing on at least 2 sites in the demo tenant; document which have sensitivity labels applied and which do not
  3. Run the KQL Library queries (P04-Exfiltration-Detection.kql): connector-based exfiltration, unlabeled documents accessed by agents, prompt injection patterns
  4. Design the remediation order for the unlabeled sites identified, justifying the sequence before enabling retrieval
  5. Complete the "Domain 4 — Protect Data" section of the Gap Assessment Template including the site inventory and labeling plan
- **Required tools:** Microsoft Purview compliance portal (DLP), SharePoint admin center (Advanced Management), Microsoft Sentinel (Logs), KQL Library P04, Gap Assessment Template
- **Deliverable:** Active DLP policy documented + site inventory with labeling status + justified remediation order + Domain 4 section of the Gap Assessment completed

---

**Closing questions for the facilitator:**
- When auditing SharePoint sites in the demo tenant, how many had agent retrieval enabled without a sensitivity label applied? What organizational process would have prevented that condition?
- If you had to design a DLP policy covering both agent responses and documents the agent generates or modifies, what workloads would you include and what types of sensitive information would you prioritize?

**Connection to the next domain:** Protecting data reduces the attack surface but does not eliminate the possibility of incidents. Domain 5 closes the security architecture with the detection and response layer: how to integrate agents as an active signal in the SOC, which analytics rules are specific to agentic behavior, and how to automate containment.

→ [Module 05 — Detect & Respond](./Module-05-DetectRespond.md)
