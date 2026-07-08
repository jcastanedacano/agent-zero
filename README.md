# Agent Zero Labs

**Practical security workshops for AI agents on the Microsoft stack.**

> A complete framework for securing agentic AI in enterprise Microsoft environments: 19 instructional modules across 3 audience tracks, 30 agent skills in agentskills.io format, 45+ production KQL queries (live-tenant validated against Microsoft 365, June 2026), ARM-deployable Sentinel workspace, and a full facilitator kit — covering the OWASP Agentic Top 10, the OWASP Agentic Skills Top 10 (AST01–AST10), and aligned to MITRE ATLAS, NIST AI RMF, NIST CSF 2.0, ISO 42001, EU AI Act, CIS Controls v8.1 (AI Agent Companion Guide), MAESTRO (CSA 7-layer agentic threat model), and the Microsoft AI Red Team Taxonomy of Failure Modes v2.0 (April 2026).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fjcastanedacano%2Fmicrosoft-agentic-security-labs%2Fmain%2FARM-Templates%2Fazuredeploy.json)

---

## What This Is

A community lab framework covering seven security domains for AI agents on the Microsoft stack:

| # | Domain | Core Question | Outcome |
|---|--------|---------------|---------|
| 01 | **Discover & Prioritize** | What agents are running, and does anyone know? | Complete inventory + risk classification |
| 02 | **Govern & Control** | Who owns each agent, and what's the lifecycle? | Every agent has an owner, policy, and lifecycle score |
| 03 | **Secure Access** | Do agents have only the access they need? | Least privilege verified + forensic identity traceability |
| 04 | **Protect Data** | Can agents exfiltrate data through prompts or connectors? | Data protected with forensic traceability in AI interactions |
| 05 | **Detect & Respond** | Is your SOC ready for agentic incidents? | Agents integrated into SOC: unified detection and response |
| 06 | **Regulatory Compliance** | Which EU AI Act tier applies, and what do DORA, ISO 42001, and NIST AI RMF require? | Compliance gap assessment + Purview Compliance Manager assessment + DORA action plan foundation (ECB/SSM deadline: 31 Oct 2026) |
| 07 | **Vendor & Third-Party AI Risk** | Which external AI vendors and MCP servers are connected, and have they been assessed? | Vendor scorecard (20 questions) + MCP server audit KQL |

---

## Who This Is For

Three parallel tracks — pick the one that fits your role:

| Track | Audience | Format | Duration | Output |
|-------|----------|--------|----------|--------|
| [**A — Executive**](./Track-A-Executive/README.md) | CISO / CTO / Director | Decision exercises, risk scenarios, roleplay — no lab access required | 4 hours | Risk Posture Map + Board Brief |
| [**B — Architect**](./Track-B-Architect/README.md) | Security Architect / Consultant | Hands-on labs in M365 E5 demo tenant + Azure AI Foundry | 10.5 hours | Gap Assessment + 90-day roadmap |
| [**C — SOC Engineer**](./Track-C-SOC-Engineer/README.md) | SOC Analyst / Security Engineer | KQL labs, Sentinel analytics rules, Purview, Entra CA, Logic Apps | 9.5 hours | Agentic incident response playbook |

---

## Repository Structure

```
microsoft-agentic-security-labs/
├── Track-A-Executive/               ← 4h executive track (decision exercises, no lab access)
│   ├── README.md
│   ├── Module-01-Discover.md
│   ├── Module-02-Govern.md
│   ├── Module-03-SecureAccess.md
│   ├── Module-04-ProtectData.md
│   ├── Module-05-DetectRespond.md
│   └── Templates/
│       └── Board-AI-Security-Brief-Template.md  ← NEW: board brief template for CISO/executive
├── Track-B-Architect/               ← 10.5h architect track (hands-on demo tenant labs)
│   ├── README.md
│   ├── Module-01-Discover.md
│   ├── Module-02-Govern.md
│   ├── Module-03-SecureAccess.md
│   ├── Module-04-ProtectData.md
│   ├── Module-05-DetectRespond.md
│   ├── Module-06-RegulatoryFrameworks.md        ← NEW: EU AI Act + NIST AI RMF + ISO 42001
│   ├── Module-07-VendorRisk.md                  ← NEW: third-party AI and MCP server risk
│   └── Templates/
│       └── Gap-Assessment-Template.md
├── Track-C-SOC-Engineer/            ← 9.5h SOC engineer track (KQL, Sentinel, Purview, Entra CA)
│   ├── README.md
│   ├── Module-01-Discover.md
│   ├── Module-02-Govern.md
│   ├── Module-03-SecureAccess.md
│   ├── Module-04-ProtectData.md
│   ├── Module-05-DetectRespond.md
│   ├── Module-06-RedTeamPerspective.md          ← NEW: attacker perspective, 6 attacks (incl. JadePuffer agentic ransomware)
│   └── Templates/
│       └── Incident-Response-Playbook-Template.md
├── KQL-Library/                     ← 40+ production-ready queries for Sentinel + Defender XDR
│   ├── README.md
│   ├── P01-Agent-Discovery.kql
│   ├── P02-Governance-Gaps.kql
│   ├── P03-Access-Anomalies.kql      ← Q7 membership inference + Q8 model inversion added
│   ├── P04-Exfiltration-Detection.kql
│   └── P05-Jailbreak-Detection.kql              ← Q7 LPCI + Q8 agentic ransomware chain (JadePuffer)
├── skills/                          ← 30 agent skills (agentskills.io format, ATLAS + NIST mapped)
│   ├── SCHEMA.md                    ← Universal Skill Format security manifest (OWASP AST04/AST10)
│   ├── discover/   (6 skills)
│   ├── govern/     (7 skills)
│   ├── secure/     (5 skills)
│   ├── protect/    (5 skills)
│   ├── detect/     (7 skills)
│   └── references/
│       └── frameworks.md            ← Cross-reference: ATLAS, D3FEND, NIST AI RMF, NIST CSF
├── ARM-Templates/                   ← Deploy a pre-configured Sentinel workspace in one click
│   ├── README.md
│   └── azuredeploy.json
└── Facilitator-Kit/                 ← Run the workshop: prerequisites, checklist, impact signals
    ├── README.md
    ├── Prerequisites.md
    ├── Lab-Environment-Checklist.md
    └── Impact-Indicators.md
```

---

## Quick Start

### Deploy the lab environment (Track B and C)

```bash
# Option 1 — Deploy to Azure button (above)
# Option 2 — Azure CLI
az deployment group create \
  --resource-group <your-rg> \
  --template-uri https://raw.githubusercontent.com/jcastanedacano/microsoft-agentic-security-labs/main/ARM-Templates/azuredeploy.json \
  --parameters workspaceName=agentic-security-lab
```

The ARM template deploys: Log Analytics workspace + Microsoft Sentinel + 3 pre-configured analytics rules (jailbreak detection, new agent without Entra identity or owner, data exfiltration) + agent watchlist.

### Start the workshop

1. **Facilitators:** Read [`/Facilitator-Kit/Prerequisites.md`](./Facilitator-Kit/Prerequisites.md) and run through [`/Facilitator-Kit/Lab-Environment-Checklist.md`](./Facilitator-Kit/Lab-Environment-Checklist.md) 24 hours before the session.
2. **Track A:** Start at [`Track-A-Executive/Module-01-Discover.md`](./Track-A-Executive/Module-01-Discover.md)
3. **Track B:** Deploy ARM template → start at [`Track-B-Architect/Module-01-Discover.md`](./Track-B-Architect/Module-01-Discover.md)
4. **Track C:** Deploy ARM template → start at [`Track-C-SOC-Engineer/Module-01-Discover.md`](./Track-C-SOC-Engineer/Module-01-Discover.md)

---

## Skills Library

30 agent skills in [agentskills.io](https://agentskills.io) format, mapped to MITRE ATLAS v5.4, D3FEND v1.3, NIST AI RMF, and NIST CSF 2.0.

Each skill includes: YAML frontmatter (pillar, subdomain, tags, framework mappings, license and role requirements), step-by-step workflow, KQL queries, and verification checklist.

| Pillar | Skills |
|--------|--------|
| [01 Discover](./skills/discover/) | `discover-inventory-agents-copilot-studio` · `discover-enumerate-foundry-agents` · `discover-shadow-ai-entra-principals` · `discover-classify-agent-connectors` · `discover-purview-dspm-ai` · `discover-third-party-ai-risk` |
| [02 Govern](./skills/govern/) | `govern-entra-agent-id` · `govern-agent365-approval-flow` · `govern-ca-policy-workload-identity` · `govern-dlp-policy-copilot-prompts` · `govern-lifecycle-decommission-agent` · `govern-pim-agent-roles` · `govern-foundry-rbac` |
| [03 Secure](./skills/secure/) | `secure-least-privilege-agent-identity` · `secure-managed-identity-foundry` · `secure-network-isolation-agent` · `secure-secret-management-keyvault` · `secure-ca-policy-agents` |
| [04 Protect](./skills/protect/) | `protect-data-loss-prevention-agent-outputs` · `protect-sensitivity-labels-ai-outputs` · `protect-purview-ai-hub-monitoring` · `protect-information-barriers-agents` · `protect-insider-risk-management-agents` |
| [05 Detect](./skills/detect/) | `detect-alert-prompt-injection-sentinel` · `detect-anomalous-agent-behavior` · `detect-data-exfiltration-agent` · `detect-agent-identity-abuse` · `detect-respond-playbook-agent-containment` · `detect-sentinel-mcp-server` · `detect-security-copilot-triage` |

→ [Framework cross-reference](./skills/references/frameworks.md) — all 30 skills mapped to ATLAS, D3FEND, NIST AI RMF, and NIST CSF.

---

## KQL Library — Schema Validation Status

All queries in the KQL Library have been validated against a live Microsoft 365 tenant (June 2026) using the Microsoft Graph Security `runHuntingQuery` API.

| File | Tables | Last Validated | Notes |
|------|--------|---------------|-------|
| [P01-Agent-Discovery.kql](./KQL-Library/P01-Agent-Discovery.kql) | `AgentsInfo`, `CloudAppEvents`, `OfficeActivity` | 2026-06-28 | Migrated from `AIAgentsInfo` (deprecated July 1, 2026). Real column is `Name` (not `AgentName`). Q6 added: MCP server + tool count risk. |
| [P02-Governance-Gaps.kql](./KQL-Library/P02-Governance-Gaps.kql) | `AgentsInfo`, `AuditLogs`, `CloudAppEvents` | 2026-06-28 | Migrated from `AIAgentsInfo`. `Owners` (dynamic) cast to string before grouping. Q6 added: compound actions without per-step HITL events (AIRT Taxonomy v2.0 §5.4). |
| [P03-Access-Anomalies.kql](./KQL-Library/P03-Access-Anomalies.kql) | `CloudAppEvents`, `EntraIdSpnSignInEvents`, `AuditLogs` | 2026-06-28 | Migrated from `AADSpnSignInEventsBeta` (deprecated Dec 2025). Field is `Country` (not `Location`). Q5b: capability/architecture disclosure (AIRT Taxonomy v2.0 §4.9). Q7: membership inference detection (privacy classification per Microsoft threat modeling). Q8: model inversion / training data reconstruction. |
| [P04-Exfiltration-Detection.kql](./KQL-Library/P04-Exfiltration-Detection.kql) | `CloudAppEvents`, `MicrosoftPurviewInformationProtection` | — | Sentinel tables — `TimeGenerated` correct. |
| [P05-Jailbreak-Detection.kql](./KQL-Library/P05-Jailbreak-Detection.kql) | `CloudAppEvents`, `BehaviorAnalytics`, `AgentsInfo` | — | Sentinel tables. Q6: goal hijacking via sustained objective drift (AIRT Taxonomy v2.0 §4.4). Q7: LPCI via tool responses (OWASP AST03, arXiv:2507.10457). Q8: agentic ransomware chain detection — JadePuffer pattern (discovery → credential → lateral → encryption in compressed time window). |

**Live tenant findings (June 2026):** P01-Q2 returned shadow AI agents (Mural, Matter, 1Page, Teamflect, Priority Matrix) that had been operating for 951 days without an Entra Agent ID or assigned owner — validating the shadow AI detection logic.

> **Migration note:** `AIAgentsInfo` is deprecated on **July 1, 2026**. All queries in this repository already use `AgentsInfo`. If you have saved queries outside Defender XDR that reference `AIAgentsInfo`, migrate them before that date.

---

## Prerequisites

### Track A — No technical environment required
- Security or technology oversight role
- Familiarity with your organization's current AI tooling (helpful, not required)

### Track B — M365 E5 demo tenant
- Microsoft 365 E5 trial or CDX demo tenant
- **Agent 365 / Microsoft 365 Copilot license** — required for `AgentsInfo` table and agent registry (Modules 01–02). Included in M365 Copilot SKU. Allow 2–4 hours after assignment before lab day.
- Azure subscription with Contributor access
- Roles: Global Reader + Security Reader + Security Admin (demo tenant)
- Portals: Purview compliance, Defender XDR, Entra admin center, Copilot Studio admin, Power Platform admin

### Track C — M365 E5 + Sentinel workspace
- All Track B requirements (including Agent 365 license)
- Sentinel workspace deployed (use ARM template above)
- Roles: Security Admin + Sentinel Contributor + Compliance Administrator
- Portals: All Track B portals + Microsoft Sentinel + Logic Apps

→ Full details: [`/Facilitator-Kit/Prerequisites.md`](./Facilitator-Kit/Prerequisites.md)

---

## Microsoft Controls Coverage

| Domain | Primary Controls |
|--------|-----------------|
| 01 Discover & Prioritize | Purview DSPM for AI · Defender AI Agent Inventory · Agent 365 Registry · SharePoint Advanced Management · CloudAppEvents (third-party agent discovery) |
| 02 Govern & Control | Entra Agent ID · Copilot Studio governance + approval flow · Foundry RBAC + API controls · Power Platform DLP · Tiered Autonomy (Logic Apps playbook tiers) · CAGE model (independent control plane from reasoning path) |
| 03 Secure Access | Entra CA for Agents (`clientApplications.includeAgentIdServicePrincipals`) · Entra ID Protection · PIM just-in-time · Defender for Cloud Apps · Foundry rate limiting (model extraction prevention) · Placeholder token/proxy pattern (non-Azure agents, RFC 8705 mTLS) · Defender for Cloud CNAPP (Azure-hosted agent workloads) |
| 04 Protect Data | Purview DLP (AI interactions workload) · Insider Risk Management · Sensitivity labels · SharePoint Advanced Management · Foundry RBAC (membership inference prevention) · Context governance: ABAC + data minimization at data-to-agent boundary · Context gap detection (audit of what data agent received as input) |
| 05 Detect & Respond | Defender XDR · Microsoft Sentinel + native MCP server · Security Copilot agents · Purview Audit · Agent 365 · Logic Apps (tiered automated response) · KQL P05-Q8 agentic ransomware chain detection |
| 06 Regulatory Compliance | Microsoft Purview Compliance Manager (EU AI Act + ISO 42001 + NIST AI RMF 1.0 templates) · Purview Audit (immutable record keeping) · Copilot Studio disclosure settings (Art. 13) |
| 07 Vendor & Third-Party AI Risk | Power Platform DLP (block unapproved connectors) · Microsoft 365 admin center Agents and Tools (MCP server allow/block) · AgentsInfo.McpServers + CloudAppEvents ExecuteToolByGateway (audit) · Azure AI Foundry model layer controls (prompt shields, content filters, groundedness detection) · Open source AI platform hardening (Langflow, Flowise, n8n) |

---

## Design Principles

Two concepts from Anthropic's [Zero Trust for AI Agents](https://www.anthropic.com/resources/zero-trust-for-ai-agents) inform the architecture of this framework:

**Least Agency** extends least privilege to agentic applications. Where least privilege restricts *what users and systems can access*, least agency goes further — restricting *what each agent tool can do*, *how often*, and *where*. Entra Agent ID + CA for Agents is the Microsoft-native implementation of least agency: the agent gets an identity, scoped permissions, and a policy that defines its blast radius before it ever runs.

**The "impossible vs. tedious" test** distinguishes real controls from friction. Ask of every mitigation: does this make an attack *impossible*, or just *tedious*? Rate limits, extra hops, and SMS-based MFA are tedious for a human attacker. An agentic adversary that can process thousands of steps per minute treats tedious controls as negligible overhead. Design for impossible first; treat tedious as a delay, not a defense.

**The control plane must be independent of the agent's reasoning path.** A policy engine that relies on the same reasoning context that generated the action provides no real safety boundary — if the agent's reasoning is influenced (via prompt injection, poisoned context, or LPCI), the safety evaluation is compromised too. The CAGE model operationalizes this separation: **C**lassify the proposed action, **A**pprove based on risk evidence (showing the actual command, not the agent's description of it), **G**ate execution through policy and least-privilege tools, **E**vidence-log the full chain — request, decision, action, and outcome. Approval screens that show only the agent's explanation become rubber stamps; the control plane must expose the actual execution artifact. Reference: Manoj Verma (2026) — "AI Agents Need a Control Plane Before They Touch Critical Systems."

**Tiered Autonomy** defines when an agent may act unilaterally and when it must stop for human approval. Three tiers: (1) *Full automation* for low-risk, reversible actions with bounded blast radius; (2) *Human approval* for medium-risk actions affecting multiple users, external systems, or sensitive data; (3) *Human-led* for high-risk actions — account disablement, data deletion, policy changes. Without explicit tier assignment, every agent defaults to tier 1, which is the most common governance gap in production deployments. The Microsoft AI Red Team Taxonomy v2.0 (April 2026) extends this with *consent architecture hardening*: HITL invocation must be deterministic (the agent cannot decide when to skip approval), compound actions must be decomposed into individually approvable steps, and action descriptions shown to approvers must resist semantic manipulation ("description laundering"). KQL P02-Q6 surfaces sessions where this decomposition is absent.

---

## OWASP Top 10 for Agentic AI (2026) — Coverage Map

| OWASP Category | This Framework | Primary Pillar |
|----------------|---------------|----------------|
| AG01 — Unsafe Agent Autonomy | Tiered Autonomy principle; CA policy enforcement; human-in-the-loop controls | 02 Govern |
| AG02 — Prompt Injection | KQL P05 jailbreak detection; Track C Module-03 lab; Sentinel analytics rule | 05 Detect |
| AG03 — Excessive Permissions | Least Agency; Entra Agent ID scoped permissions; PIM just-in-time | 03 Secure |
| AG04 — Memory Poisoning | KQL Q5a memory/session poisoning; Track C Module-04 point 5 | 04 Protect |
| AG05 — Supply Chain Compromise | KQL Q5c behavioral anomaly; Track C Module-04 point 6; model supply chain notes | 04 Protect |
| AG06 — Model Extraction | KQL P03-Q6 endpoint query anomaly; Track B/C Module-03 | 03 Secure |
| AG07 — Membership Inference | KQL P03-Q7 (high-volume low-distinctness probing, privacy classification); KQL P03-Q8 (model inversion); Track B/C Module-04 | 04 Protect |
| AG08 — Multi-Agent Trust | KQL Q5b lateral movement; Track B/C Module-02/04; multi-agent trust boundaries | 02 Govern |
| AG09 — Shadow AI / Ungoverned Agents | Discover pillar; Defender AI Inventory; Agent 365 Registry; KQL P01 | 01 Discover |
| AG10 — Denial of AI Service | KQL P03-Q1 scope expansion; rate limit monitoring via Q6 | 03 Secure |

---

## OWASP Agentic Skills Top 10 (2026) — Coverage Map

The [OWASP Agentic Skills Top 10](https://owasp.org/www-project-agentic-skills-top-10/) (AST01–AST10) covers risks specific to the **skill/plugin layer** — the MCP servers, tools, and agent extensions that load into agent runtimes at execution time. Distinct from the Agentic AI Top 10 (AG01–AG10) which covers the agent system level.

| OWASP AST | Risk | Severity | This Framework |
|-----------|------|----------|----------------|
| AST01 — Malicious Skills | Hidden payloads in skill definitions; credential stealers; SOUL.md/MEMORY.md backdoors | Critical | Track B Module-07 Domain D (MCP server audit); KQL P02 governance gap detection |
| AST02 — Supply Chain Compromise | Registry flooding; dependency confusion; config file hijacking (.claude/settings.json hooks → RCE); open source AI platform RCE (Langflow CVE-2025-3248) | Critical | Track B Module-07 (vendor risk 20-question checklist Domain D + open source platform row); Track C Module-06 Attack 6 (JadePuffer chain) |
| AST03 — Over-Privileged Skills | LPCI (Logic-layer Prompt Control Injection) — injected instructions treated as operator-level commands; arXiv:2507.10457 | High | KQL P05-Q7 (LPCI detection); KQL P05-Q8 (agentic ransomware chain); Track B/C Module-03 Least Agency; Entra Agent ID scoped permissions |
| AST04 — Insecure Metadata | YAML deserialization attacks; brand impersonation; ASCII smuggling; zero-width Unicode in skill definitions | High | Track B Module-07 Domain D-Q4 (MCP server auditability); skills/SCHEMA.md security manifest fields |
| AST05 — Untrusted External Instructions | External URL references becoming instruction sources; rug-pull; bait-and-switch skill behavior | High | Track C Module-06 (attacker perspective: XPIA patterns); KQL P05-Q1 (jailbreak/instruction override) |
| AST06 — Weak Isolation | Host-mode execution without sandbox; 135,000+ exposed agent instances (SecurityScorecard Feb 2026) | High | Track B Module-07 Domain D-Q2 (execution boundary); Track C Module-03 (network isolation) |
| AST07 — Update Drift | No version pinning; silent auto-update; hot-reload abuse in connected MCP servers | Medium | Track B Module-07 Domain D-Q1 (static vs. remotely updated tools); KQL P02-Q3 (agent configuration drift) |
| AST08 — Poor Scanning | Natural-language bypass; scanner evasion in archives; scanner LLM prompt injection (Trail of Bits, Jun 2026) | Medium | Track B Module-07 Domain E-Q2 (AI-specific security policy); skills/SCHEMA.md `scan_status` field |
| AST09 — No Governance | Shadow AI skills; no enterprise skill inventory; skills invisible to endpoint scanners | Medium | Track B Module-02 (govern & control); Track B Module-07 (vendor registry); KQL P01-Q2 (shadow AI) |
| AST10 — Cross-Platform Reuse | Security metadata lost when porting skills across platforms; Universal Skill Format not adopted | Medium | skills/SCHEMA.md (Universal Skill Format security fields: `risk_tier`, `permissions`, `scan_status`, `content_hash`) |

---

## MAESTRO — 7-Layer Agentic AI Threat Model Coverage Map

[MAESTRO](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro) (Multi-Agent Environment, Security, Threat, Risk & Outcome) is the Cloud Security Alliance's structured threat modeling framework for autonomous AI systems. Unlike OWASP (vulnerability taxonomy) or CIS Controls (control catalog), MAESTRO is a **threat modeling methodology**: it provides a 7-layer reference architecture and a 6-step analysis process for identifying how threats originate in one layer and propagate across others. It is the CSA equivalent of STRIDE/PASTA, purpose-built for agentic systems.

The 7 layers, from infrastructure to ecosystem:

| MAESTRO Layer | Threat Focus | This Framework |
|---------------|-------------|----------------|
| **L1 — Foundation Models** | Adversarial inputs, model theft via API (model extraction), training data backdoors, membership inference, denial-of-service via expensive inference | KQL P03-Q6 (model extraction detection); Track B/C Module-03 (rate limiting, Foundry controls); KQL P03-Q7/Q8 (membership inference + model inversion) |
| **L2 — Data Operations** | RAG pipeline poisoning, vector store tampering, training data exfiltration, in-transit data modification, context injection via retrieval | Track B/C Module-04 (Protect Data); KQL P04 (exfiltration); context gap controls (ABAC, data minimization); Purview DLP on AI interactions |
| **L3 — Agent Frameworks** | Supply chain backdoors in orchestration libraries (LangGraph, Flowise, n8n); MCP client injection; input validation flaws enabling code injection; compromised dependencies | Track B Module-07 point 3 (open source AI platform hardening, CVE-2025-3248); skills/SCHEMA.md (`content_hash`, `scan_status`); OWASP AST02/AST04 coverage |
| **L4 — Deployment & Infrastructure** | Malicious container images; orchestration attacks (Kubernetes); IaC tampering; resource hijacking; internet-exposed AI platforms | Track B Module-03 point 6 (CNAPP — Defender for Cloud Containers); Track B Module-07 point 3 (network segmentation, WAF for AI platforms) |
| **L5 — Evaluation & Observability** | Poisoned monitoring data hiding incidents; manipulated metrics; detection evasion (compressed attack chains); compromised monitoring agents receiving contaminated context | KQL P05-Q7 (LPCI detection via tool responses); KQL P05-Q8 (agentic ransomware chain — compressed time density signal); Track C Module-05 (Detect & Respond) |
| **L6 — Security & Compliance** | Bias in AI security decision-making; poisoned threat detection agents; lack of explainability in security determinations; regulatory evasion | Track B Module-06 (Regulatory Frameworks); Track B Module-02 point 5 (CAGE model, independent control plane); Purview Compliance Manager |
| **L7 — Agent Ecosystem** | Agent impersonation in marketplaces; goal manipulation via registry poisoning; malicious agents disguised as legitimate services; Sybil attacks with fake agent identities | Track B Module-07 (MCP server vendor assessment); Track B/C Module-01 (Discover — agent registry + shadow AI); KQL P01 (agent inventory + MCP server audit) |

**Cross-layer threats MAESTRO explicitly calls out** — and where this framework covers them:

| Cross-layer pattern | MAESTRO description | This framework |
|--------------------|---------------------|----------------|
| Supply chain → all layers | L3 compromise propagates downstream to L2 data and L7 ecosystem | Track C Module-06 Attack 6 (JadePuffer 7-stage chain); OWASP AST02; KQL P05-Q8 |
| Compromised monitoring (L5→L6) | The monitoring agent itself becomes the attack vector when fed contaminated context | Track B Module-02 point 5 (CAGE: control plane independent of reasoning path); KQL P05-Q7 (LPCI in tool responses reaching Security Copilot) |
| Lateral movement between layers | Privilege escalation from L4 (infra) to L3 (frameworks) to L7 (ecosystem) | Track C Module-06 (attacker perspective, lateral movement attack steps); MITRE ATLAS `AML.T0051` |

**MAESTRO 6-step methodology** applied to this framework's lab environment: (1) decompose your demo tenant into MAESTRO's 7 layers — which layer does each Copilot Studio agent, MCP server, and Foundry deployment sit in? (2) run layer-specific KQL queries (P01–P05) to surface threats per layer; (3) trace cross-layer propagation paths using the JadePuffer chain as a concrete example; (4) evaluate risk using the P-series severity scores; (5) map mitigations to the Track B/C module controls; (6) deploy Sentinel analytics rules and monitor continuously.

---

## CIS Controls v8.1 — AI Agent Coverage Map

The [CIS Controls AI Agent Companion Guide](https://www.cisecurity.org/controls/ai-agent-companion-guide) (CIS, 2026) interprets each CIS Control through the lens of autonomous agent systems: their runtimes, orchestration logic, tool interfaces, memory stores, and retrieval pipelines. The table below maps the Controls most relevant to agentic environments to this framework's content.

| CIS Control | Agent Interpretation | This Framework |
|-------------|---------------------|----------------|
| **01 — Inventory and Control of Enterprise Assets** | Agent runtimes, orchestration components, memory stores, and retrieval pipelines are enterprise assets requiring inventory and lifecycle management — including dynamically instantiated cloud workloads and serverless functions | Track B/C Module-01 (Discover); KQL P01 (agent inventory queries); Agent 365 Registry + Defender AI Inventory |
| **02 — Inventory and Control of Software Assets** | Agent software stacks are composite assets: orchestration frameworks, MCP clients/servers, SDKs, LLM clients, and tool dependencies must be versioned and tracked — a change in a SaaS model or local library can alter agent decision-making | Track B Module-07 point 3 (open source AI platform hardening); KQL P01-Q2 (shadow AI / ungoverned agent detection) |
| **03 — Data Protection** | Agents retrieve, process, and act on sensitive data autonomously. Context window content, retrieval outputs, and intermediate reasoning steps constitute data in motion that requires classification, minimization, and DLP controls | Track B Module-04 (Protect Data); KQL P04 (exfiltration detection); Purview DLP + sensitivity labels |
| **05 — Account Management** | Agent identities are accounts: they must be provisioned with scoped permissions, reviewed periodically, and decommissioned with token revocation. "Abandoned" agents with active permissions are accounts that can be taken over | Track B Module-02 point 4 (lifecycle); Track B Module-03 (Entra Agent ID + CA for agents); KQL P02 (governance gaps) |
| **06 — Access Control Management** | Least privilege for agents requires scoping at the OAuth scope level, not only the role level. PIM just-in-time limits the exposure window; Blueprint-level CA scales without per-instance configuration | Track B Module-03 (Secure Access); KQL P03 (access anomalies); Entra CA `clientApplications.includeAgentIdServicePrincipals` |
| **08 — Audit Log Management** | Agent decisions, tool calls, memory updates, and retrieval operations must be logged with enough fidelity to reconstruct the full agent-loop chain after an incident — standard event logs are insufficient without agent-context correlation | KQL Library (all 5 query files); Track C Module-05 (Detect & Respond); Purview Audit; CloudAppEvents `ExecuteToolByGateway` |
| **12 — Network Infrastructure Management** | Agents running on internet-exposed infrastructure (open source AI platforms, self-hosted MCP servers) extend the network attack surface. CVE-2025-3248 class vulnerabilities require WAF and network segmentation at the AI platform layer | Track B Module-03 point 6 (CNAPP for Azure-hosted agents); Track B Module-07 point 3 (open source AI platform hardening); Defender for Cloud Containers |
| **15 — Service Provider Management** | Every external MCP server, foundation model API, and AI-as-a-service provider is a service provider requiring structured assessment. Silent remote tool updates and prompt-logging policies are AI-specific risks not covered by standard vendor questionnaires | Track B Module-07 (20-question vendor evaluation framework, 5 domains); KQL P01-Q6 (MCP server risk scoring) |
| **16 — Application Software Security** | MCP server tool definitions, skill YAML manifests, and orchestration logic are application software that must be reviewed for injection risks, deserialization vulnerabilities, and supply chain integrity | Track B Module-07 Domain D (MCP server-specific questions); skills/SCHEMA.md (security manifest: `content_hash`, `scan_status`, `signature`) |
| **18 — Penetration Testing** | Agentic systems require adversarial testing distinct from traditional pen tests: multi-stage chain simulation, LPCI via tool responses, credential exfiltration through agent context, and autonomous ransomware chain (JadePuffer pattern) must be part of the scope | Track C Module-06 (6 attacks + red team perspective); KQL P05-Q7/Q8 (LPCI + agentic ransomware detection) |

**Implementation Groups:** The CIS Companion Guide uses the IG1/IG2/IG3 prioritization model. Map to this framework: Track A exercises (IG1 baseline understanding) → Track B Architect labs (IG2 enterprise controls) → Track C SOC engineer detection (IG3 advanced detection and response).

---

## Risk Vectors Covered

| Domain | Vectors |
|--------|---------|
| 01 | Shadow AI · Identity exposure · Data exposure · Local AI agents without endpoint connector · Third-party agents (ISV plugins, MCP servers) |
| 02 | No technical owner · Makers without controls · No lifecycle · Graph drift · Multi-agent trust boundaries · Unsafe agent autonomy (no tiered autonomy model) · Control plane collapsed into reasoning path (description laundering / rubber-stamp approval) |
| 03 | CA inherited from users · Over-permissioned agents · Uncontrolled OAuth consent · Identity laundering · Model extraction via API · Token exfiltration from non-managed-identity agent environments · Internet-exposed AI dev platforms (Langflow CVE-2025-3248 class) |
| 04 | Prompt injection · Oversharing · API exfiltration · Corpus poisoning (SharePoint) · Model supply chain poisoning · Memory/session poisoning · Membership inference (privacy without exfiltration) · Context gap (agent acting on stale, misrouted, or wrong data at machine speed) |
| 05 | Jailbreak attempts · Agent anomaly · Structural false negatives · Evasion at inference boundary · Goal hijacking (sustained objective drift) · Capability/architecture disclosure · LPCI via tool responses · Agentic ransomware chain (JadePuffer: autonomous multi-stage, adaptive, no human pause) |
| 07 | MCP server tool injection · Credential exposure via tool return values · Silent remote tool updates · Open source AI platform RCE · Model layer risks (prompt logging, training data use, no red team documentation) · Foundry model layer misconfiguration (no content filters, no prompt shields) |

---

## How to Use These Labs

**Self-paced learner:** Pick your track, start at Module 01, work through sequentially. Each module is standalone but the narrative builds. Track B and C now extend to Module 07 and 06 respectively.

**Facilitator:** Read [`/Facilitator-Kit`](./Facilitator-Kit/README.md) before running any session — environment prep checklist, per-track prerequisites, and signals that the workshop is working.

**Team event:** Run all three tracks in parallel. Tracks A and B/C can share a 30-minute opening keynote on the five domains, then split into track-specific rooms.

**Security operations:** Use the [skills library](./skills/) and [KQL Library](./KQL-Library/README.md) independently — each skill and query works standalone without the workshop context.

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

Areas where contributions are most valuable:
- Additional KQL queries for detection coverage gaps
- New skills for controls not yet covered (see [SCHEMA.md](./skills/SCHEMA.md) for the format)
- Lab exercises for regulated industries (financial services, healthcare, energy)
- ARM template improvements for faster lab environment deployment
- Translations of Track A materials

---

## License

MIT License. See [LICENSE](./LICENSE) for details.

---

## Related Projects

| Repository | What it does | How it differs from this project |
|------------|-------------|----------------------------------|
| [microsoft/Data-and-Agent-Governance-and-Security-Accelerator](https://github.com/microsoft/Data-and-Agent-Governance-and-Security-Accelerator) | Automates Purview DSPM for AI onboarding, DLP, sensitivity labels, and audit logging via `azd up` | Automation accelerator for deployment — not a learning framework. Use it after you understand what you're deploying. |
| [microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit) | Policy enforcement, zero-trust identity, execution sandboxing, and SRE for autonomous agents. Covers OWASP Agentic Top 10. | Framework-agnostic governance SDK (Python, any LLM). Complements this project's Microsoft-native focus. |
| [microsoft/agentic-ai-lab](https://github.com/microsoft/agentic-ai-lab) | Azure AI Foundry & Agents development workshop — RAG, MCP, red teaming, observability | Developer-focused lab for building agents, not securing them in enterprise environments. |
| [Azure/Azure-Sentinel Training Lab](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Training/Azure-Sentinel-Training-Lab) | Single-track Sentinel hands-on lab with pre-loaded data via ARM template | Sentinel product training for one audience. This project adds multi-track structure and an agentic security domain layer on top. |

---

## References

- [NIST AI Risk Management Framework](https://www.nist.gov/system/files/documents/2023/01/26/AI_RMF_1.0.pdf)
- [MITRE ATLAS — Adversarial Threat Landscape for AI Systems](https://atlas.mitre.org/)
- [MITRE D3FEND](https://d3fend.mitre.org/)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [CISA — Careful Adoption of Agentic AI Services](https://www.cisa.gov/resources-tools/resources/careful-adoption-agentic-ai-services)
- [Microsoft — Conditional Access for workload identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity)
- [Anthropic — Zero Trust for AI Agents](https://www.anthropic.com/resources/zero-trust-for-ai-agents) — source of the "least agency" concept and the impossible vs. tedious design test
- [OWASP Top 10 for Agentic AI Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-ai-applications-v1-0/) — agentic-specific vulnerability categories aligned to this framework's five pillars
- [Red Teaming AI — Attacking & Defending Intelligent Systems](https://www.apress.com/9798868817328) (Philip A. Dursey, 2025) — model extraction, membership inference, and AI red teaming methodology
- [AI Strategy and Security](https://link.springer.com/book/9798868817328) (Donnie W. Wendt, 2025) — securing agentic AI, supply chain, and drift analysis
- [agentskills.io — Agent skill format reference](https://agentskills.io)
- [JadePuffer: The Dawn of Agentic AI Ransomware](https://thecyberthrone.in/2026/07/06/jadepuffer-the-dawn-of-agentic-ai-ransomware/) (Sysdig / TheCyberThrone, 2026) — first publicly documented autonomous AI agent ransomware campaign; CVE-2025-3248 entry point; adaptive decision making at each stage
- [AI Agents Need a Control Plane Before They Touch Critical Systems](https://pub.towardsai.net/ai-agents-need-a-control-plane-before-they-touch-critical-systems-48397e1d254d) (Manoj Verma, 2026) — CAGE model; control plane independence from reasoning path; action classification matrix
- [Securing Agentic Identity](https://www.codon.org.uk/~mjg59/blog/p/securing-agentic-identity/) (Matthew Garrett, 2026) — placeholder token/proxy architecture; mTLS binding via SPIFFE/SVID; RFC 8705 for non-managed-identity agent environments
- [Agentic AI Security: Context Is the New Attack Surface](https://www.kiteworks.com/cybersecurity-risk-management/agentic-ai-context-attack-surface/) (Kiteworks, 2026) — context gap as operational failure mode; ABAC for agents; data minimization at data-to-agent boundary
- [Gartner — AI Agent Security Architecture: The Structure](https://www.gartner.com/document/8101397) (Gartner, 2026) — layered architecture: IAM, Model, Infrastructure, Data, Application + WIM/WAM/AMP/CNAPP/DSPM/AppSec + native agent control plane + AI security platform
- [CIS Controls AI Agent Companion Guide](https://www.cisecurity.org/controls/ai-agent-companion-guide) (CIS, 2026; principal author: Jonathan Sander, Astrix Security) — maps CIS Controls v8.1 to agentic systems; introduces agent-specific asset taxonomy, kill switch guidance, and implementation group (IG1/IG2/IG3) prioritization for agent security programs
- [ECB/SSM Supervisory Letter SSM-2026-0301: Addressing AI-enabled cybersecurity threats](https://www.bankingsupervision.europa.eu/press/letterstobanks/shared/pdf/2026/ssm.2026_letter_on_AI_enabled_cybersecurity_threats.en.pdf) (Claudia Buch, ECB, 7 July 2026) — requires significant institutions to submit a DORA-grounded action plan to their JST by 31 October 2026; six focus areas (attack surface, patch management, detection, governance, zero-trust, resilience) map directly to Track B Modules 01–07; Track B Gap Assessment is the technical foundation for JST submission
- [ESRB Warning on systemic cyber risks stemming from frontier AI models](https://www.esrb.europa.eu/pub/pdf/warnings/esrb.warning260625_on_systemic_cyber_risks_stemming_from_frontier_ai_models~ef424708cf.en.pdf) (European Systemic Risk Board, 7 July 2026) — system-level warning on frontier AI accelerating vulnerability discovery and exploitation at scale; published same day as ECB/SSM letter
- [MAESTRO: Agentic AI Threat Modeling Framework](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro) (Cloud Security Alliance, 2025) — 7-layer threat model (Foundation Models → Data Operations → Agent Frameworks → Deployment → Observability → Security → Ecosystem); 6-step analysis methodology; cross-layer lateral movement and supply chain propagation patterns; purpose-built for agentic systems as the CSA alternative to STRIDE/PASTA
