# Module 06 — Regulatory Frameworks for AI Security | Track B

**Module duration:** 90 minutes  
**Format:** Presentation + structured gap assessment exercise  
**Audience:** Security architects, compliance leads, risk managers

---

## Learning Objective

By the end of this module, participants will be able to map Microsoft AI agent deployments against the three major regulatory frameworks (EU AI Act, NIST AI RMF, ISO 42001), identify compliance obligations that apply to their organization's agent deployments, and translate those obligations into concrete technical controls already available in the Microsoft security stack.

---

## Module Agenda

| Time | Activity | Type |
|------|----------|------|
| 20 min | Three frameworks, one Microsoft stack: EU AI Act + NIST AI RMF + ISO 42001 | Presentation |
| 15 min | Mapping Microsoft controls to regulatory obligations | Presentation |
| 45 min | Gap assessment: classify your agent deployments against each framework | Exercise |
| 10 min | Prioritization and remediation roadmap draft | Discussion |

---

## Core Content

1. **EU AI Act — risk classification determines your obligations:** The Act classifies AI systems into four tiers: *Unacceptable risk* (prohibited — biometric surveillance, social scoring), *High risk* (Annex III — HR, law enforcement, critical infrastructure, education), *Limited risk* (chatbots, emotion recognition — transparency obligations only), and *Minimal risk* (spam filters, AI in games). Most Microsoft 365 Copilot agent deployments fall into *Limited risk* (transparency obligations) unless they are used in Annex III contexts. Consequences: up to €30M or 6% of global annual turnover for high-risk non-compliance.

2. **NIST AI RMF — four functions, continuous cycle:** The AI Risk Management Framework structures AI risk across GOVERN (policies, roles, culture), MAP (context and risk identification), MEASURE (quantification and monitoring), and MANAGE (treatment and response). Unlike the EU AI Act (compliance-based), NIST AI RMF is a voluntary framework focused on operationalization. For Microsoft environments: GOVERN maps to Track B Module 02 (agent governance), MAP maps to Track B Module 01 (agent discovery), MEASURE maps to Track C KQL Library (detection metrics), MANAGE maps to Track C Module 05 (incident response).

3. **ISO 42001 — AI Management System Standard (2023):** The first international standard for AI management systems. Structured like ISO 27001 but focused on AI risk. Key clauses: Clause 4 (organizational context — AI system inventory), Clause 6 (planning — AI risk assessment and treatment), Clause 8 (operation — AI impact assessment), Clause 9 (performance evaluation — monitoring and measurement), Clause 10 (improvement). Certification is possible; many enterprise customers will require it from AI service providers by 2027.

4. **How the frameworks overlap and where they diverge:**

   | Obligation | EU AI Act | NIST AI RMF | ISO 42001 |
   |-----------|-----------|-------------|-----------|
   | AI inventory | Article 9 | MAP-1.1 | Clause 4.3 |
   | Risk assessment | Article 9 | MAP-2.1 / MEASURE-2.5 | Clause 6.1 |
   | Human oversight | Article 14 | GOVERN-6.1 | Clause 8.4 |
   | Transparency to users | Article 13 | MAP-1.6 | Clause 8.3 |
   | Incident logging | Article 12 | MANAGE-2.4 | Clause 9.1 |
   | Third-party risk | Article 25 | GOVERN-5.1 | Clause 8.6 |

5. **Microsoft controls that satisfy regulatory obligations directly:**

   | Obligation | Microsoft Control | Where configured |
   |-----------|-----------------|------------------|
   | AI inventory (all frameworks) | Defender AI Agent Inventory + Agent 365 Registry | Defender XDR → AI Agents |
   | Compliance assessment (EU AI Act, ISO 42001, NIST AI RMF) | **Microsoft Purview Compliance Manager** — premium templates for all 3 frameworks | Purview compliance portal → Compliance Manager |
   | Human oversight (EU Act Art. 14, NIST GOVERN-6.1) | Copilot Studio approval flow + Tiered Autonomy | Module 02 of this track |
   | Transparency to users (EU Act Art. 13) | Copilot Studio — agent identity disclosure | Agent Builder settings |
   | Incident logging (EU Act Art. 12, ISO 9.1) | Microsoft Purview Audit (immutable) | Purview compliance portal |
   | Risk assessment documentation (ISO 6.1) | Gap Assessment Template (this repo) | Track B Templates |
   | Third-party risk (EU Act Art. 25) | Power Platform DLP + MCP server audit (AgentsInfo.McpServers) | Module 07 of this track |

   > **Key tool:** Microsoft Purview Compliance Manager has official premium templates for EU AI Act, ISO/IEC 42001:2023, and NIST AI RMF 1.0, applicable to M365 Copilot, Copilot Studio, Security Copilot, Azure AI Foundry, and ChatGPT Enterprise interactions. Use it as the starting point for any formal compliance assessment against these three frameworks.

---

## EU AI Act — What Applies to Microsoft Agent Deployments

### Risk classification decision tree

```
Is the agent used for biometric surveillance, social scoring,
or subliminal manipulation?
  └─ YES → PROHIBITED. Do not deploy.
  └─ NO ↓

Is the agent used in any of these domains?
  • Critical infrastructure (energy, water, transport)
  • Educational institution admission or grading
  • Employment decisions (CV screening, performance evaluation)
  • Essential public services (credit scoring, benefits)
  • Law enforcement, border control, justice
  • Democratic processes (political targeting)
  └─ YES → HIGH RISK (Annex III). Full compliance obligations.
  └─ NO ↓

Does the agent interact with humans and could users mistake it
for a human?
  └─ YES → LIMITED RISK. Transparency disclosure required.
  └─ NO → MINIMAL RISK. No specific AI Act obligations.
```

### High-risk obligations (if Annex III applies)

| Article | Obligation | Microsoft control |
|---------|-----------|------------------|
| Art. 9 | Risk management system documentation | Gap Assessment Template + ISO 42001 process |
| Art. 10 | Data governance — training data quality | Azure AI Foundry data lineage |
| Art. 11 | Technical documentation | Agent 365 Registry + architecture docs |
| Art. 12 | Record keeping (logs, audit trail) | Purview Audit (immutable, 1–10 years) |
| Art. 13 | Transparency — users must know they interact with AI | Copilot Studio disclosure settings |
| Art. 14 | Human oversight — must be able to override | Tiered Autonomy + Logic App revocation |
| Art. 17 | Quality management system | ISO 42001 management system |

---

## NIST AI RMF — Mapping to This Repository

| RMF Function | Core Activity | Repo Coverage |
|-------------|--------------|---------------|
| **GOVERN** | Policies, roles, accountability | Track B Module 02 — governance model |
| **MAP** | Identify AI context, use cases, risks | Track B Module 01 — agent discovery |
| **MEASURE** | Quantify and monitor risk | Track C KQL Library — detection metrics |
| **MANAGE** | Treat risk, respond to incidents | Track C Module 05 — detect & respond |

**Specific NIST AI RMF subcategories covered by this repo:**

- `GOVERN-1.1` — Policies for AI risk management established ← Module 02 governance model
- `GOVERN-6.1` — Human oversight and override capability ← Tiered Autonomy + Module 05 Logic App
- `MAP-1.1` — AI system inventory maintained ← Module 01 AgentsInfo KQL
- `MAP-2.1` — Potential impacts and risks identified ← Gap Assessment Template Domain risk scores
- `MEASURE-2.5` — AI system performance monitored ← P05 analytics rules + behavioral baselines
- `MANAGE-2.4` — AI incidents documented and reviewed ← Module 05 playbook + Purview Audit

**Gaps not yet covered by this repo:**
- `MAP-1.6` — AI impact assessments for high-risk deployments (AIIA)
- `GOVERN-5.1` — Third-party AI risk documented (→ Module 07 of this track)
- `MEASURE-2.2` — Bias and fairness measurement (outside scope of security focus)

---

## ISO 42001 — Implementation Checklist

Use this checklist as a pre-audit readiness assessment. Each item maps to a clause and a repo artifact.

| Clause | Requirement | Repo Artifact | Status |
|--------|-------------|---------------|--------|
| 4.3 | AI system inventory scope defined | Module 01 — agent discovery | ☐ |
| 6.1 | AI risk assessment process documented | Gap Assessment Template | ☐ |
| 6.2 | AI objectives with measurable targets | Domain risk scores in Gap Assessment | ☐ |
| 8.3 | AI impact assessment for significant changes | Gap Assessment — Domain 01 | ☐ |
| 8.4 | Measures to address AI risks | Track C Module 03-04 controls | ☐ |
| 8.6 | Third-party AI system controls | Module 07 — Vendor Risk (this track) | ☐ |
| 9.1 | Monitoring, measurement, and evaluation | Track C KQL Library + analytics rules | ☐ |
| 9.2 | Internal audit of AI management system | Gap Assessment — annual re-run | ☐ |
| 10.1 | Nonconformity and corrective action | Incident Response Playbook (Track C) | ☐ |

---

## Lab Exercise — Classify Your Agent Deployments

For each agent in your Agent 365 Registry (use P01-Q1 output from Module 01):

**Step 1 — EU AI Act classification:**
```
Agent name: ________________
Use case: ________________
Risk tier: ☐ Prohibited ☐ High risk ☐ Limited risk ☐ Minimal risk
Annex III domain (if high risk): ________________
Compliance gap: ________________
```

**Step 2 — NIST AI RMF coverage:**
```
GOVERN gap: ________________
MAP gap: ________________
MEASURE gap: ________________
MANAGE gap: ________________
```

**Step 3 — ISO 42001 readiness (0-10 scale per clause):**

| Clause | Score | Gap |
|--------|-------|-----|
| 4.3 Inventory | /10 | |
| 6.1 Risk assessment | /10 | |
| 8.4 Risk controls | /10 | |
| 9.1 Monitoring | /10 | |

---

## Closing Questions

- If your organization deploys a Copilot Studio agent used for employee performance evaluation, what EU AI Act tier applies and what are the three most urgent compliance obligations?
- Which NIST AI RMF function is most mature in your current deployment? Which is the largest gap?
- An auditor asks for evidence that your AI systems have human override capability. What Microsoft artifacts would you produce?

---

## Connection to Module 07

Regulatory frameworks require third-party AI risk management (EU AI Act Art. 25, NIST GOVERN-5.1, ISO 42001 Clause 8.6). The next module covers how to evaluate vendors and MCP server providers before connecting them to your agent environment.

→ [Module 07 — Vendor & Third-Party AI Risk](./Module-07-VendorRisk.md)
