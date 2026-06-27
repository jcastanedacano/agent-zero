# Microsoft Agentic Security Labs

**Practical security workshops for AI agents on the Microsoft stack.**

> Hands-on labs, instructional design, KQL queries, and facilitator resources for securing agentic AI systems using Microsoft 365, Defender, Sentinel, Purview, and Entra.

---

## What This Is

A community lab framework covering the five security domains that matter when AI agents operate in your Microsoft environment:

| # | Domain | Core Question |
|---|--------|---------------|
| 01 | **Discover & Prioritize** | What agents are running, and does anyone know? |
| 02 | **Govern & Control** | Who owns each agent, and what's the lifecycle? |
| 03 | **Secure Access** | Do agents have only the access they need? |
| 04 | **Protect Data** | Can agents exfiltrate data through prompts or connectors? |
| 05 | **Detect & Respond** | Is your SOC ready for agentic incidents? |

---

## Who This Is For

The labs are organized into three tracks. Pick the one that fits your role:

| Track | Audience | Format | Duration |
|-------|----------|--------|----------|
| **A** | CISO / CTO / Director | Decision exercises, risk scenarios, roleplay | 4 hours |
| **B** | Security Architect / Consultant | Hands-on labs in M365 E5 demo tenant | 8 hours |
| **C** | SOC Analyst / Engineer | KQL, Sentinel rules, Purview, Entra CA | 8 hours |

Each track produces a tangible output:
- **Track A** → Risk Posture Map for your organization
- **Track B** → Gap Assessment + 90-day roadmap
- **Track C** → Agentic incident response playbook

---

## Repository Structure

```
microsoft-agentic-security-labs/
├── README.md
├── Track-A-Executive/
│   ├── README.md
│   ├── Module-01-Discover.md
│   ├── Module-02-Govern.md
│   ├── Module-03-SecureAccess.md
│   ├── Module-04-ProtectData.md
│   ├── Module-05-DetectRespond.md
│   └── Printables/
│       ├── Exercise-P01-Exposure-Map.md
│       ├── Exercise-P02-Approval-Scenarios.md
│       ├── Exercise-P03-Access-Decision.md
│       ├── Exercise-P04-Data-Exposure-Scorecard.md
│       └── Exercise-P05-SOC-Maturity-Card.md
├── Track-B-Architect/
│   ├── README.md
│   ├── Module-01-Discover.md
│   ├── Module-02-Govern.md
│   ├── Module-03-SecureAccess.md
│   ├── Module-04-ProtectData.md
│   ├── Module-05-DetectRespond.md
│   └── Templates/
│       └── Gap-Assessment-Template.md
├── Track-C-SOC-Engineer/
│   ├── README.md
│   ├── Module-01-Discover.md
│   ├── Module-02-Govern.md
│   ├── Module-03-SecureAccess.md
│   ├── Module-04-ProtectData.md
│   ├── Module-05-DetectRespond.md
│   └── Templates/
│       └── Incident-Response-Playbook-Template.md
├── KQL-Library/
│   ├── README.md
│   ├── P01-Agent-Discovery.kql
│   ├── P02-Governance-Gaps.kql
│   ├── P03-Access-Anomalies.kql
│   ├── P04-Exfiltration-Detection.kql
│   └── P05-Jailbreak-Detection.kql
├── ARM-Templates/
│   ├── README.md
│   └── azuredeploy.json
└── Facilitator-Kit/
    ├── README.md
    ├── Prerequisites.md
    ├── Lab-Environment-Checklist.md
    └── Impact-Indicators.md
```

---

## Prerequisites

### Track A — No technical environment required
- A role with security or technology oversight responsibility
- Familiarity with your organization's current AI tooling (helpful, not required)

### Track B — M365 E5 demo tenant
- Microsoft 365 E5 trial or CDX demo tenant
- Roles: Global Reader + Security Reader
- Access to: Purview compliance portal, Defender XDR portal, Entra admin center, Copilot Studio admin, Power Platform admin

### Track C — M365 E5 + Sentinel workspace
- Microsoft 365 E5 trial or CDX demo tenant
- Azure subscription with Sentinel workspace deployed
- Roles: Security Admin (scoped to demo tenant) + Sentinel Contributor
- Access to: All Track B portals + Microsoft Sentinel + Logic Apps

> **Deploy the lab environment** using the ARM template in [`/ARM-Templates`](./ARM-Templates/README.md) to provision a pre-configured Sentinel workspace with demo data for Track B and C labs.

---

## How to Use These Labs

### As a self-paced learner
Pick your track, start at Module 01, and work through to Module 05. Each module is standalone — you can do them in any order, but the narrative builds sequentially.

### As a facilitator
Read the [`/Facilitator-Kit`](./Facilitator-Kit/README.md) before running any session. It includes environment prep checklist, per-track prerequisites, and signals that the workshop is working.

### As a team
Run all three tracks in parallel on the same day. Tracks A and B/C can share an opening keynote (30 min) covering the five domains, then split into track-specific rooms.

---

## KQL Library

The [`/KQL-Library`](./KQL-Library/README.md) folder contains production-ready queries organized by security domain. Each query includes:
- Target table(s)
- Required permissions
- Expected output description
- Adaptation notes for production environments

Queries are designed for Microsoft Sentinel and Defender Advanced Hunting. Most run against standard M365 E5 tables without additional ingestion requirements.

---

## Microsoft Controls Coverage

| Domain | Primary Controls |
|--------|-----------------|
| Discover & Prioritize | Purview DSPM for AI, Defender AI Agent Inventory, Agent 365, SharePoint Advanced Management |
| Govern & Control | Entra Agent ID, Copilot Studio governance, Foundry RBAC, Power Platform DLP |
| Secure Access | Entra CA for Agents, Entra ID Protection, PIM just-in-time, Defender for Cloud Apps |
| Protect Data | Purview DLP, Insider Risk Management, Sensitivity labels, SharePoint Advanced Management |
| Detect & Respond | Defender XDR, Microsoft Sentinel, Security Copilot, Purview Audit, Agent 365 |

---

## Risk Vectors Covered

| Domain | Vectors |
|--------|---------|
| 01 | Shadow AI, Identity exposure, Data exposure, Local AI agents |
| 02 | No technical owner, Makers without controls, No lifecycle, Graph drift |
| 03 | CA inherited from users, Over-permissioned agents, Uncontrolled OAuth consent, Identity laundering |
| 04 | Prompt injection, Oversharing, API exfiltration, Poisoned corpus |
| 05 | Jailbreak attempts, Agent anomaly, Structural false negatives |

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

Areas where contributions are most valuable:
- Additional KQL queries for detection coverage
- Lab exercises for specific regulated industries (financial services, healthcare, energy)
- ARM template improvements for faster lab environment deployment
- Translations of Track A materials

---

## License

MIT License. See [LICENSE](./LICENSE) for details.

---

## Related Projects

These Microsoft-published repos address adjacent problems. Understanding how they differ from this project helps you choose the right tool:

| Repository | What it does | How it differs from this project |
|------------|-------------|----------------------------------|
| [microsoft/Data-and-Agent-Governance-and-Security-Accelerator](https://github.com/microsoft/Data-and-Agent-Governance-and-Security-Accelerator) | Automates Purview DSPM for AI onboarding, DLP, sensitivity labels, and audit logging via a spec file (`spec.local.json`) and `azd up` | Automation accelerator for deployment — not a learning framework. Use it after you understand what you're deploying. |
| [microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit) | Policy enforcement, zero-trust identity, execution sandboxing, and SRE for autonomous agents. Covers OWASP Agentic Top 10. | Framework-agnostic governance SDK (Python, any LLM). Complements this project's Microsoft-native focus. |
| [microsoft/agentic-ai-lab](https://github.com/microsoft/agentic-ai-lab) | Azure AI Foundry & Agents development workshop — RAG, MCP, red teaming, observability | Developer-focused lab for building agents, not securing them in enterprise environments. |
| [Azure/Azure-Sentinel Training Lab](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Training/Azure-Sentinel-Training-Lab) | Single-track Sentinel hands-on lab with pre-loaded data via ARM template | Sentinel product training for one audience. This project adds multi-track structure and an agentic security domain layer on top. |

---

## References

- [NIST AI Risk Management Framework](https://www.nist.gov/system/files/documents/2023/01/26/AI_RMF_1.0.pdf)
- [MITRE ATLAS](https://atlas.mitre.org/)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [CSA AI Safety & Security](https://cloudsecurityalliance.org/research/topics/artificial-intelligence)
- [CISA Careful Adoption of Agentic AI Services](https://www.cisa.gov/resources-tools/resources/careful-adoption-agentic-ai-services)
