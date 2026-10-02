# Framework coverage

How six published threat models map to the same Microsoft controls. The summary table and the guidance on which one to start with are in the [main README](../README.md#framework-coverage).

<details>
<summary><b>OWASP Top 10 for Agentic Applications (2026)</b> — ASI01–ASI10 · agent system level</summary>

<br>

Published 9 December 2025 by the OWASP GenAI Security Project (100+ contributors, built on real incident data). This table replaces an earlier internal "AG01–AG10" shorthand this repo used before OWASP's official taxonomy shipped — some categories that shorthand listed (model extraction, membership inference, denial of service) turned out to belong to the separate **OWASP Top 10 for LLM Applications**, not this one; see the note below the table.

| OWASP Category | This Framework | Primary Pillar |
|----------------|---------------|----------------|
| ASI01 — Agent Goal Hijack | Tiered Autonomy principle; CA policy enforcement; KQL P05 jailbreak detection; human-in-the-loop controls | 02 Govern / 05 Detect |
| ASI02 — Tool Misuse & Exploitation | CAGE control-plane model (independent evaluation outside agent reasoning); CoreBreak direct tool-invocation defense | 02 Govern |
| ASI03 — Identity & Privilege Abuse | Least Agency; Entra Agent ID scoped permissions; PIM just-in-time | 03 Secure |
| ASI04 — Agentic Supply Chain Vulnerabilities | KQL Q5c behavioral anomaly; Track B/C Module-04 point 6; MCP/vendor supply chain (Module 07) | 04 Protect / 07 Vendor |
| ASI05 — Unexpected Code Execution (RCE) | CoreBreak direct tool invocation + forged-approval defense (Module 02 point 11); OffGuard guardrail RCE (Module 03 point 12) | 02 Govern / 03 Secure |
| ASI06 — Memory & Context Poisoning | KQL Q5a memory/session poisoning; Track B/C Module-04 point 5 | 04 Protect |
| ASI07 — Insecure Inter-Agent Communication | KQL Q5b lateral movement; multi-agent trust boundaries; Track B/C Module-02/04 | 02 Govern / 04 Protect |
| ASI08 — Cascading Failures | MAESTRO cross-layer propagation; multi-agent trust boundary controls (Module 04) | 04 Protect |
| ASI09 — Human-Agent Trust Exploitation | CAGE model — approval screens must show the actual command, not the agent's description of it (Module 02 point 5) | 02 Govern |
| ASI10 — Rogue Agents | Three-level kill switch (Module 02 point 10); ID Protection for agents confirm-compromise workflow (Module 02 point 12) | 02 Govern |

**Two categories from the old AG-list weren't Agentic Applications risks at all — they're OWASP LLM Top 10 (2026) risks, at the model/inference layer, not the agent-system layer:**

| OWASP Category | Old shorthand | This Framework | Primary Pillar |
|----------------|---------------|-----------------|-----------------|
| LLM06 — Unbounded Consumption | (was "AG06 — Model Extraction") | KQL P03-Q6 endpoint query anomaly; Foundry per-identity rate limiting | 03 Secure |
| LLM02 — Sensitive Information Disclosure | (was "AG07 — Membership Inference") | KQL P03-Q7/Q8 (query-pattern + model inversion detection); Foundry RBAC; no fine-tuning on raw PII | 04 Protect |

**One category ("AG09 — Shadow AI / Ungoverned Agents") had no OWASP Top 10 equivalent at all**, in either list — it's a governance/inventory gap, not a runtime vulnerability class. It stays covered here via CIS Controls AI Agent Companion Guide, Control 5 (Account Management), and the Discover pillar (Module 01, KQL P01), without an OWASP tag.

</details>

<details>
<summary><b>OWASP Agentic Skills Top 10 (2026)</b> — AST01–AST10 · skill and plugin layer</summary>

<br>

The [OWASP Agentic Skills Top 10](https://owasp.org/www-project-agentic-skills-top-10/) (AST01–AST10) covers risks specific to the **skill/plugin layer** — the MCP servers, tools, and agent extensions that load into agent runtimes at execution time. Distinct from the OWASP Top 10 for Agentic Applications (ASI01–ASI10) above, which covers the agent system level.

| OWASP AST | Risk | Severity | This Framework |
|-----------|------|----------|----------------|
| AST01 — Malicious Skills | Hidden payloads in skill definitions; credential stealers; SOUL.md/MEMORY.md backdoors | Critical | Track B Module-07 Domain D (MCP server audit); KQL P02 governance gap detection |
| AST02 — Supply Chain Compromise | Registry flooding; dependency confusion; config file hijacking (.claude/settings.json hooks → RCE); open source AI platform RCE (Langflow CVE-2025-3248) | Critical | Track B Module-07 (vendor risk 22-question checklist Domain D + open source platform row); Track C Module-06 Attack 6 (JadePuffer chain) |
| AST03 — Over-Privileged Skills | LPCI (Logic-layer Prompt Control Injection) — injected instructions treated as operator-level commands; arXiv:2507.10457 | High | KQL P05-Q7 (LPCI detection); KQL P05-Q8 (agentic ransomware chain); Track B/C Module-03 Least Agency; Entra Agent ID scoped permissions |
| AST04 — Insecure Metadata | YAML deserialization attacks; brand impersonation; ASCII smuggling; zero-width Unicode in skill definitions | High | Track B Module-07 Domain D-Q4 (MCP server auditability); skills/SCHEMA.md security manifest fields |
| AST05 — Untrusted External Instructions | External URL references becoming instruction sources; rug-pull; bait-and-switch skill behavior | High | Track C Module-06 (attacker perspective: XPIA patterns); KQL P05-Q1 (jailbreak/instruction override) |
| AST06 — Weak Isolation | Host-mode execution without sandbox; 135,000+ exposed agent instances (SecurityScorecard Feb 2026) | High | Track B Module-07 Domain D-Q2 (execution boundary); Track C Module-03 (network isolation) |
| AST07 — Update Drift | No version pinning; silent auto-update; hot-reload abuse in connected MCP servers | Medium | Track B Module-07 Domain D-Q1 (static vs. remotely updated tools); KQL P02-Q3 (agent configuration drift) |
| AST08 — Poor Scanning | Natural-language bypass; scanner evasion in archives; scanner LLM prompt injection (Trail of Bits, Jun 2026) | Medium | Track B Module-07 Domain E-Q2 (AI-specific security policy); skills/SCHEMA.md `scan_status` field |
| AST09 — No Governance | Shadow AI skills; no enterprise skill inventory; skills invisible to endpoint scanners | Medium | Track B Module-02 (govern & control); Track B Module-07 (vendor registry); KQL P01-Q2 (shadow AI) |
| AST10 — Cross-Platform Reuse | Security metadata lost when porting skills across platforms; Universal Skill Format not adopted | Medium | skills/SCHEMA.md (Universal Skill Format security fields: `risk_tier`, `permissions`, `scan_status`, `content_hash`) |

</details>

<details>
<summary><b>MAESTRO (Cloud Security Alliance)</b> — 7 layers · cross-layer threat propagation</summary>

<br>

[MAESTRO](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro) (Multi-Agent Environment, Security, Threat, Risk & Outcome) is the Cloud Security Alliance's structured threat modeling framework for autonomous AI systems. Unlike OWASP (vulnerability taxonomy) or CIS Controls (control catalog), MAESTRO is a **threat modeling methodology**: it provides a 7-layer reference architecture and a 6-step analysis process for identifying how threats originate in one layer and propagate across others. It is the CSA equivalent of STRIDE/PASTA, purpose-built for agentic systems.

The 7 layers, from infrastructure to ecosystem:

| MAESTRO Layer | Threat Focus | This Framework |
|---------------|-------------|----------------|
| **L1 — Foundation Models** | Adversarial inputs, model theft via API (model extraction), training data backdoors, membership inference, denial-of-service via expensive inference | KQL P03-Q6 (model extraction detection); Track B/C Module-03 (rate limiting, Foundry controls); KQL P03-Q7/Q8 (membership inference + model inversion) |
| **L2 — Data Operations** | RAG pipeline poisoning, vector store tampering, training data exfiltration, in-transit data modification, context injection via retrieval | Track B/C Module-04 (Protect Data); KQL P04 (exfiltration); context gap controls (ABAC, data minimization); Purview DLP on AI interactions |
| **L3 — Agent Frameworks** | Supply chain backdoors in orchestration libraries (LangGraph, Flowise, n8n); MCP client injection; input validation flaws enabling code injection; compromised dependencies | Track B Module-07 point 4 (open source AI platform hardening, CVE-2025-3248); skills/SCHEMA.md (`content_hash`, `scan_status`); OWASP AST02/AST04 coverage |
| **L4 — Deployment & Infrastructure** | Malicious container images; orchestration attacks (Kubernetes); IaC tampering; resource hijacking; internet-exposed AI platforms | Track B Module-03 point 6 (CNAPP — Defender for Cloud Containers); Track B Module-07 point 4 (network segmentation, WAF for AI platforms) |
| **L5 — Evaluation & Observability** | Poisoned monitoring data hiding incidents; manipulated metrics; detection evasion (compressed attack chains); compromised monitoring agents receiving contaminated context | KQL P05-Q7 (LPCI detection via tool responses); KQL P05-Q8 (agentic ransomware chain — compressed time density signal); Track C Module-05 (Detect & Respond) |
| **L6 — Security & Compliance** | Bias in AI security decision-making; poisoned threat detection agents; lack of explainability in security determinations; regulatory evasion | Track B Module-06 (Regulatory Frameworks); Track B Module-02 point 5 (CAGE model, independent control plane); Purview Compliance Manager |
| **L7 — Agent Ecosystem** | Agent impersonation in marketplaces; goal manipulation via registry poisoning; malicious agents disguised as legitimate services; Sybil attacks with fake agent identities | Track B Module-07 (MCP server vendor assessment); Track B/C Module-01 (Discover — agent registry + shadow AI); KQL P01 (agent inventory + MCP server audit) |

**Cross-layer threats MAESTRO explicitly calls out** — and where this framework covers them:

| Cross-layer pattern | MAESTRO description | This framework |
|--------------------|---------------------|----------------|
| Supply chain → all layers | L3 compromise propagates downstream to L2 data and L7 ecosystem | Track C Module-06 Attack 6 ( 7-stage chain); OWASP AST02; KQL P05-Q8 |
| Compromised monitoring (L5→L6) | The monitoring agent itself becomes the attack vector when fed contaminated context | Track B Module-02 point 5 (CAGE: control plane independent of reasoning path); KQL P05-Q7 (LPCI in tool responses reaching Security Copilot) |
| Lateral movement between layers | Privilege escalation from L4 (infra) to L3 (frameworks) to L7 (ecosystem) | Track C Module-06 (attacker perspective, lateral movement attack steps); MITRE ATLAS `AML.T0051` |

**MAESTRO 6-step methodology** applied to this framework's lab environment: (1) decompose your demo tenant into MAESTRO's 7 layers — which layer does each Copilot Studio agent, MCP server, and Foundry deployment sit in? (2) run layer-specific KQL queries (P01–P05) to surface threats per layer; (3) trace cross-layer propagation paths; (4) evaluate risk using the P-series severity scores; (5) map mitigations to the Track B/C module controls; (6) deploy Sentinel analytics rules and monitor continuously.

</details>

<details>
<summary><b>PHANTOM-B (Adam Shostack)</b> — 8 threats · the lightest to adopt</summary>

<br>

[PHANTOM-B](https://shostack.org) (Adam Shostack, White Paper #6, July 2026, CC-BY) is a STRIDE-analogous mnemonic for the LLM parts of a system, written by the author of STRIDE itself. It is deliberately the **lightest** framework in this repository: low effort to learn, low effort to use, and scoped to organizations that *call* an LLM rather than train one — which is the position of every enterprise deploying Copilot, Copilot Studio, or Azure AI Foundry agents. Shostack designed it as a set of **prompts, not categories**: the goal is not to file each threat into a bucket but to confirm you considered at least one of each kind. By explicit design it contains no controls or mitigations, which makes it complementary to this framework rather than overlapping with it.

| PHANTOM-B threat | This framework | Coverage |
|-----------------|---------------|----------|
| **P** — Prompt injection | KQL P05-Q1 (jailbreak), P05-Q7 (LPCI via tool responses), P05-Q9 (session aggregation vs. PT0200 decomposition); Track B Module-04 point 2 (poisoned corpus); Module-05 points 5–6 (single-turn blind spot + Prompt Shield pre-inference); Module-05 point 9 (agent-to-agent injection); Track C Module-06 attacks 1 and 5 | Strong |
| **H** — Hallucination | Track B Module-07 point 5 (groundedness detection in Azure AI Foundry content filters) | **Weak — declared gap.** This repo treats hallucination as a safety and quality property, not a security control surface. Groundedness detection is the only lever mapped. |
| **A** — Anthropomorphization | Track B Module-02 point 5 (CAGE — the approval screen must show the actual command, not the agent's description of it); Module-02 point 10 (a "stop" instruction in the system prompt is not a kill switch) | Strong but previously unnamed. Both controls exist precisely because the agent has no intent to appeal to — PHANTOM-B supplies the vocabulary this repo was missing. |
| **N** — Non-explainability | Track B Module-04 point 6 (audit must capture what the agent *saw as context*, not only what it did); Purview Audit immutable chain of custody; Module-06 assurance case structure | Partial |
| **T** — Training issues | Track B Module-04 point 5 (three levels of poisoning; ~250 documents suffice regardless of model size); Module-07 point 8 (AI-BOM: dataset provenance and fine-tuning lineage); Module-07 point 10 (model weight security posture) | Strong |
| **O** — Over-reliance | Track B Module-02 point 6 (Tiered Autonomy); Module-02 point 5 (rubber-stamp approval); Module-02 point 10 (human-on-the-loop for tier 3); Module-06 (EU AI Act Art. 14, NIST GOVERN-6.1) | Strong |
| **M** — Missing security engineering | Track B Modules 01–07 in full; CIS Controls v8.1 coverage map above. This is the catch-all for "did you still do the ordinary engineering after adding the LLM" | Strong |
| **B** — Biases | Not covered | **Declared gap**, consistent with the NIST `MEASURE-2.2` exclusion noted below. Worth flagging that PHANTOM-B argues bias becomes a *security and legal* problem specifically when combined with over-reliance — an agent making hiring or credit decisions unreviewed. Organizations in EU AI Act Annex III domains must close this outside this repository. |

**Where PHANTOM-B and MAESTRO disagree — and why this repo keeps both.** Shostack's comparison table rates MAESTRO as "very high" effort to learn and criticizes it for not aligning to the industry-standard Four Question Framework. That critique is fair on its own terms: MAESTRO is a threat modeling *methodology* with a 7-layer reference architecture, and it costs real time to adopt. But the two tools answer different questions. PHANTOM-B asks what can go wrong with **the LLM call**; MAESTRO asks how a threat **propagates across layers** of a multi-agent system — cross-layer lateral movement and compromised monitoring agents (Layer 5) have no PHANTOM-B equivalent, because PHANTOM-B is scoped to the LLM component and not to agent ecosystems. Practical guidance for this repo: start with PHANTOM-B per agent in Module 01, escalate to MAESTRO when the architecture has multiple agents calling each other.

**Note on the "agentic" label.** PHANTOM-B lists anthropomorphization as a first-class threat and names calling AI "agentic" as an instance of it. This repository uses that term throughout. The critique is included here rather than omitted because it has an operational payload: assuming intent leads directly to approving what an agent *says* it will do and to trusting a system prompt as a control boundary. Track B Module-02 points 5 and 9 exist to counter exactly those two errors.

</details>

<details>
<summary><b>CIS Controls v8.1 — AI Agent Companion Guide</b> — 10 controls · IG1/IG2/IG3 prioritization</summary>

<br>

The [CIS Controls AI Agent Companion Guide](https://www.cisecurity.org/controls/ai-agent-companion-guide) (CIS, 2026) interprets each CIS Control through the lens of autonomous agent systems: their runtimes, orchestration logic, tool interfaces, memory stores, and retrieval pipelines. The table below maps the Controls most relevant to agentic environments to this framework's content.

| CIS Control | Agent Interpretation | This Framework |
|-------------|---------------------|----------------|
| **01 — Inventory and Control of Enterprise Assets** | Agent runtimes, orchestration components, memory stores, and retrieval pipelines are enterprise assets requiring inventory and lifecycle management — including dynamically instantiated cloud workloads and serverless functions | Track B/C Module-01 (Discover); KQL P01 (agent inventory queries); Agent 365 Registry + Defender AI Inventory |
| **02 — Inventory and Control of Software Assets** | Agent software stacks are composite assets: orchestration frameworks, MCP clients/servers, SDKs, LLM clients, and tool dependencies must be versioned and tracked — a change in a SaaS model or local library can alter agent decision-making | Track B Module-07 point 4 (open source AI platform hardening); KQL P01-Q2 (shadow AI / ungoverned agent detection) |
| **03 — Data Protection** | Agents retrieve, process, and act on sensitive data autonomously. Context window content, retrieval outputs, and intermediate reasoning steps constitute data in motion that requires classification, minimization, and DLP controls | Track B Module-04 (Protect Data); KQL P04 (exfiltration detection); Purview DLP + sensitivity labels |
| **05 — Account Management** | Agent identities are accounts: they must be provisioned with scoped permissions, reviewed periodically, and decommissioned with token revocation. "Abandoned" agents with active permissions are accounts that can be taken over | Track B Module-02 point 4 (lifecycle); Track B Module-03 (Entra Agent ID + CA for agents); KQL P02 (governance gaps) |
| **06 — Access Control Management** | Least privilege for agents requires scoping at the OAuth scope level, not only the role level. PIM just-in-time limits the exposure window; Blueprint-level CA scales without per-instance configuration | Track B Module-03 (Secure Access); KQL P03 (access anomalies); Entra CA `clientApplications.includeAgentIdServicePrincipals` |
| **08 — Audit Log Management** | Agent decisions, tool calls, memory updates, and retrieval operations must be logged with enough fidelity to reconstruct the full agent-loop chain after an incident — standard event logs are insufficient without agent-context correlation | KQL Library (all 5 query files); Track C Module-05 (Detect & Respond); Purview Audit; CloudAppEvents `ExecuteToolByGateway` |
| **12 — Network Infrastructure Management** | Agents running on internet-exposed infrastructure (open source AI platforms, self-hosted MCP servers) extend the network attack surface. CVE-2025-3248 class vulnerabilities require WAF and network segmentation at the AI platform layer | Track B Module-03 point 6 (CNAPP for Azure-hosted agents); Track B Module-07 point 4 (open source AI platform hardening); Defender for Cloud Containers |
| **15 — Service Provider Management** | Every external MCP server, foundation model API, and AI-as-a-service provider is a service provider requiring structured assessment. Silent remote tool updates and prompt-logging policies are AI-specific risks not covered by standard vendor questionnaires | Track B Module-07 (22-question vendor evaluation framework, 5 domains); KQL P01-Q6 (MCP server risk scoring) |
| **16 — Application Software Security** | MCP server tool definitions, skill YAML manifests, and orchestration logic are application software that must be reviewed for injection risks, deserialization vulnerabilities, and supply chain integrity | Track B Module-07 Domain D (MCP server-specific questions); skills/SCHEMA.md (security manifest: `content_hash`, `scan_status`, `signature`) |
| **18 — Penetration Testing** | Agentic systems require adversarial testing distinct from traditional pen tests: multi-stage chain simulation, LPCI via tool responses, credential exfiltration through agent context, and autonomous ransomware chain must be part of the scope | Track C Module-06 (6 attacks + red team perspective); KQL P05-Q7/Q8 (LPCI + agentic ransomware detection) |

**Implementation Groups:** The CIS Companion Guide uses the IG1/IG2/IG3 prioritization model. Map to this framework: Track A exercises (IG1 baseline understanding) → Track B Architect labs (IG2 enterprise controls) → Track C SOC engineer detection (IG3 advanced detection and response).

</details>

<details>
<summary><b>HACCA Defense-in-Depth</b> — Delay · Defend · Detect · Disrupt</summary>

<br>

The 2026 policy report *Highly Autonomous Cyber-Capable Agents: Anticipating Capabilities, Tactics, and Strategic Implications* projects the emergence of AI systems able to run end-to-end offensive cyber campaigns for weeks to months without human supervision, at the capability level of an organized criminal group (RAND OC3: ~10 experienced operators, $1M, multi-month). Its practical contribution for defenders is a four-layer framework — **Delay, Defend, Detect, Disrupt** — that organizes countermeasures by strategic objective rather than by product. The table below maps each layer to what this repository already implements and where the gaps sit.

| Layer | Objective | HACCA countermeasures | This framework |
|-------|-----------|----------------------|----------------|
| **Delay** | Slow the proliferation of autonomous offensive capability to malicious actors | Model weight security (tiered security levels, data-center egress limits, insider threat programs), differential access to AI-cyber capability | Track B Module-07 point 10 (model weight security as a vendor question, B5) + AI-BOM (point 8) + 22-question vendor framework. *Mostly out of an enterprise's control — the enterprise-side action is vendor assessment, not implementation.* |
| **Defend** | Reduce the attack surface available to autonomous attackers | Security-by-design for AI-generated code, automated vulnerability discovery and patching, automated red teaming and pentesting | Track B Module-03 (Secure Access, least agency) + Module-04 (Protect Data, ABAC + data minimization) + Module-07 point 4 (open source AI platform hardening) + Track C Module-06 (red team, with the dual-use authorization requirements in point 7) |
| **Detect** | Gain visibility into autonomous operations before objectives are achieved | Detection signatures for autonomous operations, threat intelligence sharing for agent activity, agent honeypots | Track B Module-05 point 11 (sequence signatures: retry-with-variation, inter-action latency, post-access verification) + point 12 (agent honeypot design) + point 8 (canary tokens and honeytokens) + KQL P05-Q8 (compressed multi-stage chain) |
| **Disrupt** | Degrade or neutralize an active autonomous operation | Compute, finance, and model access controls; KYC for agents; network disruption; phased response protocols | Track B Module-02 point 10 (three-level kill switch: session revocation → identity disable → runtime stop, with measured RTO) + Module-07 point 9 (Denial-of-Wallet, APIM rate limiting, cost alerts) + Module-07 point 10 (agent KYC, per-agent attribution via APIM) + Module-05 Logic App containment playbook |

**What the report adds that is not a control:** a strategic frame for the *why now*. Its central empirical anchor is the September 2025 campaign in which AI agents autonomously executed an estimated 80–90% of tactical operations against approximately 30 global targets — the first documented case of the tool becoming the operator. Its second contribution is naming the loss-of-control failure mode as a distinct risk class from the misuse failure mode: a rogue autonomous system is a *threat actor*, not a *threat tool*, and the two require different countermeasures. That distinction maps directly onto MAESTRO Layer 5 (compromised monitoring agents) and onto the kill switch requirement in Module 02.

</details>
