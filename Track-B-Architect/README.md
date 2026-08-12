# Track B — Security Architect / Consultant

**Audience:** Security architects, security consultants, identity engineers, technical IT leaders  
**Duration:** 8 hours (full day)  
**Format:** Hands-on labs in M365 E5 demo tenant with real Microsoft controls  
**Output:** Completed Gap Assessment + 90-day implementation roadmap

---

## Prerequisites

- Active M365 E5 demo or CDX tenant (see [Prerequisites.md](../Facilitator-Kit/Prerequisites.md))
- **Agent 365 / Microsoft 365 Copilot license** — required for the `AgentsInfo` table and agent registry (Modules 01–02). Included in the M365 Copilot SKU. Assign in M365 admin center and allow 2–4 hours for propagation before lab day.
- Azure subscription with Contributor access for ARM template deployment
- Roles in demo tenant: Global Reader + Security Admin + Sentinel Contributor
- Familiarity with Microsoft Entra ID, Microsoft Sentinel, and Purview (architect level)
- Recommended: complete Track A or read the framework executive summary beforehand

---

## Module Index

| Module | Domain | Lab | Duration |
|--------|--------|-----|----------|
| [01 — Discover & Prioritize](./Module-01-Discover.md) | Agent inventory architecture | Defender AI Inventory + inventory KQL | 90 min |
| [02 — Govern & Control](./Module-02-Govern.md) | Governance model and lifecycle | Entra Agent ID + Copilot Studio + DLP | 90 min |
| [03 — Secure Access](./Module-03-SecureAccess.md) | CA policy for agent identities | CA policy + What If + OAuth audit KQL | 90 min |
| [04 — Protect Data](./Module-04-ProtectData.md) | Data protection and AI DLP | Purview DLP + SharePoint Advanced Management | 90 min |
| [05 — Detect & Respond](./Module-05-DetectRespond.md) | Detection and response architecture | Sentinel rules + Logic App playbook | 90 min |
| [06 — Regulatory Frameworks](./Module-06-RegulatoryFrameworks.md) | EU AI Act + NIST AI RMF + ISO 42001 | Agent classification + compliance gap assessment | 90 min |
| [07 — Vendor & Third-Party AI Risk](./Module-07-VendorRisk.md) | Supply chain and MCP server risk | Vendor evaluation (22-question checklist) + MCP audit KQL | 90 min |

Total lab time: ~10.5 hours. Reserve 30 minutes for Gap Assessment consolidation and roadmap at close.

---

## Participant Output — Gap Assessment

Each module contributes one section of the Gap Assessment Template. By end of day:

```
Gap Assessment — [Organization Name]
├── Domain 1 — Agent inventory with documented blind spots
├── Domain 2 — Governance model configured with gaps and owners assigned
├── Domain 3 — Valid CA policy for agents + What If evidence
├── Domain 4 — DLP policy for AI interactions + site inventory
├── Domain 5 — Active analytics rules + enforcement Logic App
├── Domain 6 — Regulatory framework compliance status (EU AI Act / NIST AI RMF / ISO 42001)
└── Domain 7 — Third-party AI vendor assessment scores + MCP server audit
    └── Consolidated 90-day roadmap with prioritization by domain
```

Use the [Gap Assessment Template](./Templates/Gap-Assessment-Template.md) to document findings during each module.

---

## Lab Environment Deployment

Deploy the Sentinel workspace with demo data before the session starts:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fjcastanedacano%2Fagent-zero%2Fmain%2FARM-Templates%2Fazuredeploy.json)

→ See [ARM Templates README](../ARM-Templates/README.md) for parameter details and estimated cost.

---

## KQL Library

All queries used in these labs are available in [`/KQL-Library`](../KQL-Library/) for reference, adaptation, and production deployment.
