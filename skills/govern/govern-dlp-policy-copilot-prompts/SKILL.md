---
name: govern-dlp-policy-copilot-prompts
version: "1.0"
pillar: govern
subdomain: ms-purview-ai
description: >-
  Configures DLP policies in Microsoft Purview to detect and block sensitive
  data transmission in Copilot Studio agent prompts and responses, covering
  PII, financial data, and corporate secrets.
tags: [govern, purview, dlp, copilot-studio, data-protection, prompt-security]
atlas_techniques: [AML.T0057, AML.T0048]
d3fend_techniques: [D3-DLP, D3-PA]
nist_ai_rmf: [MANAGE-2.2, GOVERN-6.1]
nist_csf: [PR.DS-01, PR.DS-05]
ms_license: [Microsoft Purview E3, M365 E3]
ms_roles: [Compliance Administrator, DLP Compliance Management]
effort_hours: 6
---

## When to use

- Agents with access to customer (PII), financial, or strategic data
- Before enabling agents in production environments with real data
- Compliance requirement (data regulations in financial/healthcare sectors)

## Known constraint

Purview auto-labeling policy creation is not available via the Lokka-Microsoft
MCP or direct ARM for every capability. Configuration via the Compliance
Portal (UI) is the reliable path for complex policies.

## Prerequisites

- Microsoft Purview E3 or higher
- Sensitivity labels configured in the tenant
- Compliance Administrator role
- Access to the Microsoft Purview Compliance Portal (`compliance.microsoft.com`)

## Workflow

### Step 1 — Verify the relevant sensitive information types

```
Purview Compliance Portal → Data classification → Sensitive info types
```

Priority types for AI agents:
- **Credit Card Number** — financial transactions
- **National ID** — user PII
- **SWIFT Code** — banking data
- **Generic Password** / **API Key** — secrets that could be exfiltrated via prompt
- Custom types: create if the sector requires it

### Step 2 — Create the DLP policy for Copilot

```
Purview Compliance Portal → Data loss prevention → Policies → Create policy
→ Custom policy
→ Locations: Microsoft Copilot (preview if available), Teams, SharePoint
```

**Rule 1 — Block PII in outbound prompts:**
- Condition: content contains [Credit Card Number, National ID, SWIFT Code]
- Action: Block + notify user + generate alert
- User notification: This prompt contains sensitive information and cannot be sent to the agent

**Rule 2 — Alert on responses with confidential data:**
- Condition: content contains sensitivity label [Confidential, Highly Confidential]
- Action: Alert compliance team + audit log

### Step 3 — Simulation mode first

Enable the policy in **Test mode** (no enforcement) for 7 days.
Review DLP reports to identify false positives before enforcement.

```
Purview → Data loss prevention → Reports → DLP policy matches
```

### Step 4 — Activate enforcement

Switch to **Turn it on right away** after validating in test mode.
Configure alerts for the compliance team.

### Step 5 — Configure Purview AI Hub (if available)

```
Purview → AI Hub → Settings
```

AI Hub provides visibility specific to AI agent interactions.
Enable prompt auditing for correlation with Sentinel.

## Verification

- [ ] Sensitive information types configured
- [ ] Policy in test mode returns matches in DLP reports
- [ ] False positives reviewed and tuned
- [ ] Policy in active enforcement
- [ ] Compliance alerts configured
- [ ] AI Hub enabled (if licensed)

## Implementation notes

- The Purview connector in Sentinel must be active for DLP events to be visible in KQL queries
- Creating auto-labeling policies via API has preview limitations — use the Compliance Portal for initial configuration
- To validate the DLP policy without real data: use synthetic credit-card-formatted data in a test prompt and confirm the policy fires
