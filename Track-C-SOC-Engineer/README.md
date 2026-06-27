# Track C — SOC Analyst / Engineer

**Audience:** SOC analysts, security engineers, detection engineers, incident responders  
**Duration:** 8 hours (full day)  
**Format:** Hands-on technical labs — KQL, Sentinel analytics rules, Purview policies, Entra CA  
**Output:** Agentic incident response playbook (documented, ready to operationalize)

---

## Prerequisites

- Microsoft 365 E5 demo or trial tenant
- Azure subscription with Microsoft Sentinel workspace deployed
- Roles: Security Admin (scoped to demo tenant) + Sentinel Contributor
- Familiarity with KQL basics (can write simple queries, understand filter/summarize/join)
- Experience with Microsoft Sentinel analytics rules and Logic Apps (basic)

> Deploy the lab environment using the [ARM template](../ARM-Templates/README.md) before the session.

---

## Module Index

| Module | Domain | Core Lab | Duration |
|--------|--------|----------|----------|
| [01 — Discover & Prioritize](./Module-01-Discover.md) | Agent inventory and visibility | KQL queries on AIAgentsInfo + OfficeActivity | 90 min |
| [02 — Govern & Control](./Module-02-Govern.md) | Governance gaps and identity orphans | Entra Agent ID + DLP policy + governance KQL | 90 min |
| [03 — Secure Access](./Module-03-SecureAccess.md) | CA policy for agents + OAuth audit | Entra CA for Agents + What If validation | 90 min |
| [04 — Protect Data](./Module-04-ProtectData.md) | DLP for AI interactions + exfiltration detection | Purview DLP + CloudAppEvents KQL | 90 min |
| [05 — Detect & Respond](./Module-05-DetectRespond.md) | Jailbreak detection + response playbook | Sentinel analytics rules + Logic App enforcement | 90 min |

Total lab time: ~7.5 hours. Reserve 30 minutes for setup validation and playbook consolidation.

---

## What You Build

Each module produces a component of the final deliverable. By end of day:

```
Agentic Incident Response Playbook
├── Section 1 — Agent inventory queries (P01)
├── Section 2 — Governance gap detection queries (P02)
├── Section 3 — CA policy documentation + access anomaly queries (P03)
├── Section 4 — DLP configuration + exfiltration detection queries (P04)
└── Section 5 — Jailbreak analytics rules + Logic App enforcement flow (P05)
```

Use the [Playbook Template](./Templates/Incident-Response-Playbook-Template.md) to consolidate outputs across modules.

---

## KQL Library

All queries used in these labs are available in the [`/KQL-Library`](../KQL-Library/) folder for reference, adaptation, and production deployment.
