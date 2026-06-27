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
| Azure subscription | Contributor access to an Azure subscription for ARM template deployment |
| Entra roles | Global Reader + Security Reader |
| Tools | Browser access to: Azure Portal, Microsoft Entra admin center, Microsoft Purview compliance portal |

**Provisioning lead time:** 48 hours minimum for CDX tenant activation.

---

## Track C — SOC Engineer Workshop

**Format:** Hands-on technical labs (KQL, Sentinel, Purview, Entra CA)

| Requirement | Detail |
|-------------|--------|
| Device | Laptop with browser |
| M365 tenant | M365 E5 demo tenant (CDX tenant strongly recommended) |
| Azure subscription | Contributor access — Sentinel workspace will be deployed via ARM template |
| Microsoft Sentinel | Workspace deployed and connected to M365 tenant before lab day |
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
AIAgentsInfo | take 5
CloudAppEvents | take 5
OfficeActivity | take 5
MicrosoftPurviewInformationProtection | take 5
```

If `AIAgentsInfo` is empty, deploy the ARM template — it includes pre-loaded demo data simulating agentic activity.

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
