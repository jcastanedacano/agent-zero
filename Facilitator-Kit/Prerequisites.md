# Prerequisites

Technical and access requirements per track. Validate these **before** distributing workshop invitations — provisioning gaps discovered on lab day cannot be resolved in time.

---

## Track A — Executive Briefing

**Format:** Presentation + discussion (no hands-on lab)

| Requirement | Detail |
|-------------|--------|
| Device | Any device with a modern browser |
| M365 account | Read-only access to a demo or production M365 tenant (optional — for live demos) |
| Role | None required for participants |

**Facilitator only:**
- M365 E5 demo tenant with at least one Copilot Studio agent deployed
- Screen sharing capability for live demos

---

## Track B — Architect Workshop

**Format:** Design sessions + architecture review

| Requirement | Detail |
|-------------|--------|
| Device | Laptop with browser (no local tooling required) |
| M365 tenant | M365 E5 demo or trial tenant (CDX tenant recommended) |
| **Microsoft Agent 365** | Defender's AI agent inventory (`AgentsInfo`) needs the tenant onboarded to Agent 365, plus the Microsoft 365 connector in Defender with the components *Microsoft Entra ID Management events* and *Microsoft 365 activities* (investigation and hunting). Agent 365 is included with Microsoft 365 E7 and is an add-on for E5, A5 and Business Premium; registry inventory and basic governance actions come with Microsoft 365 Enterprise plans, while policy templates, observability, tool access control and access packages need E7 or Agent 365. In CDX tenants, check **M365 admin center → Billing → Licenses**. Without onboarding, `AgentsInfo` can return 0 rows. |
| Azure subscription | Contributor access to an Azure subscription for ARM template deployment |
| Entra roles | Global Reader + Security Reader |
| Tools | Browser access to: Azure Portal, Microsoft Entra admin center, Microsoft Purview compliance portal, Copilot Studio admin center |

**Provisioning lead time:** 48 hours minimum for CDX tenant activation. If adding Agent 365 to an existing CDX tenant, allow an additional 2–4 hours for license propagation before lab day.

---

## Track C — SOC Engineer Workshop

**Format:** Hands-on technical labs (KQL, Sentinel, Purview, Entra CA)

| Requirement | Detail |
|-------------|--------|
| Device | Laptop with browser |
| M365 tenant | M365 E5 demo tenant (CDX tenant strongly recommended) |
| Azure subscription | Contributor access — Sentinel workspace will be deployed via ARM template |
| Microsoft Sentinel | Workspace deployed and connected to M365 tenant before lab day |
| **Microsoft Agent 365** | Needed for the `AgentsInfo` table and the agent registry (Modules 01–02): onboard the tenant to Agent 365 and connect the Microsoft 365 connector in Defender (*Microsoft Entra ID Management events* and *Microsoft 365 activities*). Included with Microsoft 365 E7, add-on for E5, A5 and Business Premium. Verify before lab day. |
| Roles — Entra | Security Admin (scoped to demo tenant) |
| Roles — Sentinel | Sentinel Contributor |
| Roles — Defender | Security Reader minimum; Security Operator to act on findings |
| Roles — Purview | Compliance Administrator |
| KQL familiarity | Can write basic KQL: `where`, `project`, `summarize`, `join` — see [KQL quickstart](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/tutorials/learn-common-operators) |
| Experience | Basic familiarity with Microsoft Sentinel analytics rules and Logic Apps |

### Track C — Minimum viable data in tables

The following tables must return results before labs start. Run these validation queries in Sentinel Logs:

```kql
// Must return > 0 rows
AgentsInfo | take 5                          // Requires Agent 365 (M365 Copilot) license
CloudAppEvents | take 5
OfficeActivity | take 5
MicrosoftPurviewInformationProtection | take 5
EntraIdSpnSignInEvents | take 5              // Replaces AADSpnSignInEventsBeta (deprecated Dec 2025)
```

If `AgentsInfo` is empty, check two things: (1) verify the tenant is onboarded to Microsoft Agent 365 and that the Microsoft 365 connector in Defender shows Connected (Settings → Security for AI → Get started); (2) allow 2–4 hours after onboarding for the table to become queryable (lab guidance, not re-verified in Oct 2026). If `CloudAppEvents` is empty, deploy the ARM template — it includes pre-loaded demo data simulating agentic activity.

> **Note:** `AIAgentsInfo` was deprecated on **July 1, 2026** and has been replaced by `AgentsInfo`. If you have saved queries referencing the old table name, migrate them before running the lab.

→ [Deploy lab environment](../ARM-Templates/README.md)

---

## Common — All Tracks

| Requirement | Detail |
|-------------|--------|
| Network | No VPN blocking Azure Portal, Defender XDR, Purview, or Entra admin center |
| MFA | All participant accounts must have MFA configured (conditional access will block unconfigured accounts during lab) |
| Browser | Microsoft Edge or Chrome (recommended); Safari supported but some Purview admin pages render inconsistently |

---

## What If You Don't Have an E5 Tenant?

- **CDX (Customer Digital Experiences):** Request a demo tenant at [cdx.transform.microsoft.com](https://cdx.transform.microsoft.com). Activation takes 24–48 hours. Recommended for facilitators.
- **M365 Developer Program:** Free 90-day E5 sandbox at [developer.microsoft.com/microsoft-365/dev-program](https://developer.microsoft.com/microsoft-365/dev-program). No Copilot licenses included by default.
- **Azure trial:** [azure.microsoft.com/free](https://azure.microsoft.com/free) covers the Sentinel workspace deployment. ARM template cost for 1 lab day: < $5 USD.
