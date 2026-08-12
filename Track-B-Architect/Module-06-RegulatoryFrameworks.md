# Module 06 — Regulatory Frameworks for AI Security | Track B

**Module duration:** 90 minutes  
**Format:** Presentation + structured gap assessment exercise  
**Audience:** Security architects, compliance leads, risk managers

---

## Learning Objective

By the end of this module, participants will be able to map Microsoft AI agent deployments against four regulatory frameworks (EU AI Act, DORA, NIST AI RMF, ISO 42001), identify compliance obligations that apply to their organization's agent deployments, and translate those obligations into concrete technical controls already available in the Microsoft security stack. Participants in regulated financial institutions will additionally be able to scope the action plan required by the ECB/SSM supervisory letter of 7 July 2026 (SSM-2026-0301).

---

## Module Agenda

| Time | Activity | Type |
|------|----------|------|
| 20 min | Four frameworks, one Microsoft stack: EU AI Act + DORA + NIST AI RMF + ISO 42001 | Presentation |
| 15 min | Mapping Microsoft controls to regulatory obligations | Presentation |
| 45 min | Gap assessment: classify your agent deployments against each framework | Exercise |
| 10 min | Prioritization and remediation roadmap draft | Discussion |

---

## Core Content

1. **EU AI Act — risk classification determines your obligations:** The Act classifies AI systems into four tiers: *Unacceptable risk* (prohibited — biometric surveillance, social scoring), *High risk* (Annex III — HR, law enforcement, critical infrastructure, education), *Limited risk* (chatbots, emotion recognition — transparency obligations only), and *Minimal risk* (spam filters, AI in games). Most Microsoft 365 Copilot agent deployments fall into *Limited risk* (transparency obligations) unless they are used in Annex III contexts. Consequences: up to €30M or 6% of global annual turnover for high-risk non-compliance.

2. **NIST AI RMF — four functions, continuous cycle:** The AI Risk Management Framework structures AI risk across GOVERN (policies, roles, culture), MAP (context and risk identification), MEASURE (quantification and monitoring), and MANAGE (treatment and response). Unlike the EU AI Act (compliance-based), NIST AI RMF is a voluntary framework focused on operationalization. For Microsoft environments: GOVERN maps to Track B Module 02 (agent governance), MAP maps to Track B Module 01 (agent discovery), MEASURE maps to Track C KQL Library (detection metrics), MANAGE maps to Track C Module 05 (incident response).

3. **ISO 42001 — AI Management System Standard (2023):** The first international standard for AI management systems. Structured like ISO 27001 but focused on AI risk. Key clauses: Clause 4 (organizational context — AI system inventory), Clause 6 (planning — AI risk assessment and treatment), Clause 8 (operation — AI impact assessment), Clause 9 (performance evaluation — monitoring and measurement), Clause 10 (improvement). Certification is possible; many enterprise customers will require it from AI service providers by 2027.

4. **DORA — Digital Operational Resilience Act (Regulation EU 2022/2554):** Mandatory for all EU financial entities (banks, payment institutions, investment firms, insurance). DORA establishes binding requirements for ICT risk management, incident reporting, resilience testing, and third-party ICT provider oversight. AI-enabled threats do not introduce new DORA obligations but dramatically raise the stakes on existing ones: the ECB/SSM supervisory letter of **7 July 2026** (SSM-2026-0301, Claudia Buch) explicitly invokes DORA as the binding framework for its action plan requirement. Banks must submit a concrete AI-enabled threat response plan to their Joint Supervisory Team (JST) by **31 October 2026**. Key DORA articles for agent deployments: Art. 5 (ICT risk management governance — management body accountability), Art. 8 (ICT asset identification and classification — includes agent runtimes and MCP servers), Art. 9 (protection of ICT systems — least privilege, zero-trust for service accounts/APIs), Art. 10 (detection — monitoring of anomalous activities), Art. 11 (ICT response and recovery), Art. 28-30 (third-party ICT provider risk management — applies to every external model API and MCP server). **The Gap Assessment produced in Track B Modules 01–07 is the technical foundation for the ECB-required action plan.**

5. **How the frameworks overlap and where they diverge:**

   | Obligation | EU AI Act | DORA | NIST AI RMF | ISO 42001 |
   |-----------|-----------|------|-------------|-----------|
   | AI / ICT inventory | Article 9 | Art. 8 | MAP-1.1 | Clause 4.3 |
   | Risk assessment | Article 9 | Art. 6 | MAP-2.1 / MEASURE-2.5 | Clause 6.1 |
   | Human oversight | Article 14 | Art. 5 (governance) | GOVERN-6.1 | Clause 8.4 |
   | Transparency to users | Article 13 | — | MAP-1.6 | Clause 8.3 |
   | Incident logging | Article 12 | Art. 10 / Art. 19 | MANAGE-2.4 | Clause 9.1 |
   | Third-party risk | Article 25 | Art. 28-30 | GOVERN-5.1 | Clause 8.6 |
   | Resilience testing | — | Art. 24-25 (TLPT) | MANAGE-4.1 | Clause 9.2 |

6. **Microsoft controls that satisfy regulatory obligations directly:**

   | Obligation | Microsoft Control | Where configured |
   |-----------|-----------------|------------------|
   | AI / ICT inventory (all frameworks) | Defender AI Agent Inventory + Agent 365 Registry | Defender XDR → AI Agents |
   | Compliance assessment (EU AI Act, ISO 42001, NIST AI RMF) | **Microsoft Purview Compliance Manager** — premium templates for all 3 frameworks | Purview compliance portal → Compliance Manager |
   | Human oversight (EU Act Art. 14, DORA Art. 5, NIST GOVERN-6.1) | Copilot Studio approval flow + Tiered Autonomy | Module 02 of this track |
   | Transparency to users (EU Act Art. 13) | Copilot Studio — agent identity disclosure | Agent Builder settings |
   | Incident logging (EU Act Art. 12, DORA Art. 10/19, ISO 9.1) | Microsoft Purview Audit (immutable) | Purview compliance portal |
   | Risk assessment documentation (ISO 6.1, DORA Art. 6) | Gap Assessment Template (this repo) — doubles as ECB action plan foundation | Track B Templates |
   | Third-party risk (EU Act Art. 25, DORA Art. 28-30) | Power Platform DLP + MCP server audit (AgentsInfo.McpServers) | Module 07 of this track |
   | Detection of anomalous ICT activity (DORA Art. 10) | KQL P01–P05 + Sentinel analytics rules + Defender XDR | Track C KQL Library + Module 05 |
   | Resilience testing (DORA Art. 24-25 TLPT) | Track C Module 06 red team exercises (JadePuffer chain simulation) | Track C Module 06 |

   > **Key tool:** Microsoft Purview Compliance Manager has official premium templates for EU AI Act, ISO/IEC 42001:2023, and NIST AI RMF 1.0, applicable to M365 Copilot, Copilot Studio, Security Copilot, Azure AI Foundry, and ChatGPT Enterprise interactions. Use it as the starting point for any formal compliance assessment against these three frameworks.

---

## ECB/SSM Supervisory Letter — Action Plan Requirement for Financial Institutions

> **Applies to:** Significant institutions supervised by the ECB under the Single Supervisory Mechanism (SSM). Similar requirements are emerging from national supervisors across the EU, UK (PRA/FCA), and international equivalents (FSOC, APRA).

On **7 July 2026**, ECB Chair Claudia Buch issued supervisory letter **SSM-2026-0301** to the CEO of every significant institution, requiring:

1. A comprehensive **action plan** addressing AI-enabled cybersecurity threats, submitted to the Joint Supervisory Team (JST) by **31 October 2026**
2. The action plan must cover six focus areas (Annex 1 of the letter):
   - **Attack surface protection**: ICT asset inventory including third-party software and open-source components; minimisation of internet-facing exposure — maps to **Module 01** (Discover) and **Module 07** (Vendor Risk)
   - **Vulnerability and patch management at scale**: AI-accelerated vulnerability discovery compresses the exploitation window; AI-assisted scanning tools require governance before deployment — maps to **Module 07** point 4 (open source AI platform hardening, CVE-2025-3248)
   - **Monitoring, detection, and AI-enabled defensive capabilities**: strengthened log monitoring, network traffic analysis, and AI-native detection tools — maps to **Module 05** (Detect & Respond) and **KQL Library P01–P05**
   - **Governance, supply chain assurance, and awareness**: management body accountability; third-party ICT provider preparedness — maps to **Module 02** (Govern) and **Module 07** (Vendor Risk)
   - **Defence-in-depth and zero-trust**: zero-trust for users, devices, applications, APIs, and **service accounts** — maps to **Module 03** (Secure Access, CA for agents as service accounts)
   - **Operational resilience**: ransomware and high-speed attack scenario exercises — maps to **Track C Module 06** (JadePuffer chain simulation) and **KQL P05-Q8**

**The Gap Assessment Template produced across Track B Modules 01–07 is the technical foundation for the ECB-required action plan.** Completing this track gives a bank a structured, evidence-based document ready for JST submission, with KQL-validated findings, control gaps, owners, and a 90-day remediation roadmap.

The letter also references the **ESRB warning on systemic cyber risks stemming from frontier AI models** (published the same day) and notes that **post-quantum cryptography** will be addressed in a separate ECB letter.

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

## OWASP AI Exchange — GUARD Model Mapping

The OWASP AI Exchange (owaspai.org) is the most comprehensive open-source technical reference for AI security, feeding directly into ISO/IEC 27090, ISO/IEC 27091, and the EU AI Act. Its **GUARD operational model** (Govern, Understand, Adapt, Reduce, Demonstrate) is a practitioner framework complementary to NIST AI RMF — where NIST describes what to do, GUARD describes how an organization operationalizes it. The table below maps GUARD to Agent Zero controls and to NIST AI RMF functions.

| GUARD Step | What it means | Agent Zero implementation | NIST AI RMF mapping |
|-----------|--------------|--------------------------|---------------------|
| **Govern** | Establish AI program oversight, policies, roles, compliance checking, security education | Track B Module 02 (governance model, Entra Agent ID ownership, lifecycle policy) + Track A all modules (executive decision framework) | GOVERN-1.1, GOVERN-6.1 |
| **Understand** | Threat model per use case, identify applicable threats via decision tree, distinguish organizational vs. supplier responsibilities | Track B Module 01 (agent discovery) + Gap Assessment Template (Domain risk scores) + MAESTRO 7-layer analysis | MAP-1.1, MAP-2.1 |
| **Adapt** | Extend existing security programs to include AI-specific threats, integrate AI security testing, enhance supply chain management | Track B Modules 03-07 (CA for agents, DLP, detection, vendor risk) extending existing IAM/DLP/SOC programs | MAP-1.6, GOVERN-5.1 |
| **Reduce** | Minimize sensitive data exposure, limit unwanted model behavior impact, manage privileges, apply human oversight | Purview DLP + SharePoint AM (data) + Tiered Autonomy + Logic App revocation (behavior) + APIM allow-list (channels) | MANAGE-2.4, MANAGE-4.1 |
| **Demonstrate** | Provide transparency through testing, document risk assessments, show compliance evidence, communicate control effectiveness | Gap Assessment Template (evidence base) + KQL P01-P05 (measurable detection coverage) + Purview Compliance Manager templates | MEASURE-2.5, MANAGE-2.4 |

**Key OWASP AI Exchange concepts adopted in this repo:**

- **Lethal Trifecta** (Track A Module 04): three conditions that must coexist for agent-mediated exfiltration — attacker-controlled input + access to sensitive data + outbound channel. Removing any one leg collapses the risk.
- **Decision tree for threat applicability**: the OWASP AI Exchange provides 6 questions to determine which threat categories apply to a given agent deployment (Is the model GenAI with untrusted input? Does the system insert augmentation data? Does the model trigger actions?). Use this as a complement to the EU AI Act risk classification tree in this module.
- **Agentic AI "four key properties"** (Action, Autonomy, Complexity, Multi-system): maps directly to why MAESTRO and Agent Zero cover 7 domains rather than a single control domain.

Reference: OWASP AI Exchange, owaspai.org — CC0 1.0 (no copyright restrictions).

---

## Sistemas autonomos y el vacio regulatorio: lo que ningun marco cubre todavia

Los cuatro marcos de este modulo (EU AI Act, DORA, NIST AI RMF, ISO 42001) fueron calibrados para sistemas de IA operados por humanos y para tiempos de decision humanos. Siguen siendo aplicables a agentes autonomos, pero tres vacios concretos aparecen cuando el sistema actua sin supervision continua. Cada uno es un elemento accionable para el programa de cumplimiento, no una discusion teorica.

**1. La taxonomia de incidentes no distingue quien decidio.** DORA Art. 19, NIS2 y EU AI Act Art. 73 exigen reportar incidentes significativos, pero ninguno define un campo para el grado de autonomia con el que se produjo el hecho. Sin ese campo, un incidente en el que un agente ejecuto una accion fuera de su alcance queda registrado igual que un error de configuracion humano, y la organizacion pierde la unica metrica que permite saber si su modelo de autonomia esta bien calibrado. Paso practico: extender la taxonomia interna de incidentes con un campo de tres valores.

| Valor | Definicion | Que dispara |
|-------|-----------|-------------|
| Dirigido por humano | Una persona instruyo explicitamente la accion | Respuesta a incidentes estandar |
| Iniciado por el agente dentro de alcance | El agente decidio de forma autonoma, dentro de su tier de autonomia y sus permisos aprobados | Respuesta a incidentes + revision del diseno del tier |
| Iniciado por el agente fuera de alcance | El agente actuo mas alla de lo autorizado, por injection, drift o error de scope | Respuesta a incidentes + revision de gobierno + evaluacion de kill switch |

El tercer valor es el unico que debe escalar a revision de gobierno y no solo a respuesta a incidentes. Si su taxonomia actual no lo distingue, esos casos se estan cerrando como fallos de configuracion.

**2. La responsabilidad transfronteriza sigue a la organizacion, no al agente.** Un agente que actua sobre sistemas en otra jurisdiccion genera obligaciones para la organizacion que lo desplego, con independencia de si la accion fue intencionada o de si el operador estaba presente. En derecho internacional esto se articula como un deber de diligencia debida: quien opera desde su jurisdiccion responde por el dano transfronterizo previsible. La lectura operativa para un arquitecto: el alcance geografico de las herramientas de un agente es una decision de cumplimiento, no solo tecnica. Documente en el registro de gobierno (Modulo 02) que jurisdicciones puede alcanzar cada agente a traves de sus conectores y servidores MCP, y trate cualquier ampliacion de ese alcance como un cambio que requiere revision legal y no solo aprobacion tecnica.

**3. Las herramientas defensivas autonomas tienen el mismo perfil que las ofensivas.** Un agente de pentesting o red teaming autonomo es, tecnicamente, indistinguible de un atacante autonomo: enumera, explota y se mueve lateralmente, con credenciales y acceso extendido a la red. El precedente que la literatura de politica publica cita de forma explicita es Cobalt Strike, una herramienta legitima de pentesting cuyas versiones pirateadas se convirtieron en instrumento estandar del crimen organizado, obligando a su creador a gestionar el acceso de forma activa y a coordinar con fuerzas del orden. Requisitos antes de desplegar cualquier agente de seguridad ofensiva, propio o de un proveedor: autorizacion escrita con alcance explicito (rangos de red, sistemas incluidos y excluidos, ventana temporal), un kill switch probado con RTO medido (Modulo 02, punto 9), y registro de todas las acciones con la misma retencion que se aplica a un incidente. Track C Modulo 06 aplica esta regla en sus ejercicios de red team.

**Assurance case: el formato que la regulacion pedira despues.** Las industrias criticas (aeroespacial, nuclear) exigen desde hace decadas un *assurance case*: un argumento estructurado, respaldado por evidencia, que sostiene la afirmacion de que un sistema es suficientemente seguro para operar. La direccion en la que se mueve la politica publica de IA es a exigir lo mismo para sistemas autonomos de alto riesgo, incluida la autorizacion previa al despliegue condicionada a esa documentacion. El Gap Assessment de este track ya tiene la estructura de un assurance case incompleto: contiene la afirmacion (este agente puede operar), la evidencia (hallazgos KQL, configuracion validada, controles verificados) y los gaps (lo que falta). Lo que le falta para serlo formalmente es el argumento explicito que conecta la evidencia con la afirmacion. Al cerrar el Gap Assessment, escriba un parrafo por dominio que responda una sola pregunta: por que esta evidencia es suficiente para sostener que este riesgo esta controlado. Ese parrafo es exactamente lo que un auditor o un supervisor pedira, y es lo que hoy falta en la mayoria de los expedientes de cumplimiento de IA.

Referencia: informe HACCA (2026), Seccion 6 (Guardrails for HACCA Development and Deployment) y Seccion 7 (Key Recommendations).

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

**Step 0 — DORA scoping (financial institutions only):**
```
Is your organization a significant institution supervised by ECB/SSM?  ☐ Yes  ☐ No
ECB action plan deadline: 31 October 2026
JST contact: ________________
Gap Assessment sections that map to action plan focus areas:
  Attack surface (Module 01 + 07):     ☐ complete  ☐ gap
  Detection (Module 05 + KQL P01-P05): ☐ complete  ☐ gap
  Governance + supply chain (Module 02 + 07): ☐ complete  ☐ gap
  Zero-trust / service accounts (Module 03): ☐ complete  ☐ gap
  Resilience exercises (Track C Module 06):  ☐ complete  ☐ gap
```

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
