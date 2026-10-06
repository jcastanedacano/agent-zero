---
name: protect-data-loss-prevention-agent-outputs
version: "1.0"
pillar: protect
subdomain: ms-purview-ai
description: >-
  Configures DLP policies in Purview specifically for AI agent outputs in
  SharePoint, OneDrive, and Exchange, blocking sharing of agent-generated
  content containing sensitive data toward unauthorized destinations.
tags: [protect, purview, dlp, sharepoint, onedrive, exchange, agent-outputs, exfiltration]
atlas_techniques: [AML.T0086, AML.T0057]
d3fend_techniques: [D3-DLP, D3-EAC]
nist_ai_rmf: [MANAGE-2.2, GOVERN-6.1]
nist_csf: [PR.DS-05, DE.CM-01]
ms_license: [Microsoft Purview E3, M365 E3]
ms_roles: [Compliance Administrator, DLP Compliance Management]
effort_hours: 5
---

## When to use

- Agents that deposit outputs in SharePoint or OneDrive
- Agents that send outputs via email (Exchange)
- When sensitivity labels are configured (see the previous skill) and you need
  to block actions on labeled content
- Key difference from `govern-dlp-policy-copilot-prompts`: that skill protects
  what Copilot receives and processes; this skill protects generated outputs/files

## Risk scenarios covered

1. An agent generates a report with customer data and a user shares it externally
2. An agent exports CRM data to a CSV in OneDrive and a user downloads it without restriction
3. An agent drafts an email with confidential information and sends it to an external recipient

## Workflow

### Step 1 — Identify agent output locations

From the Pillar 1 risk register and the `discover-classify-agent-connectors` skill:
- Which SharePoint sites do agents use as an output destination?
- Which OneDrive folders?
- Do agents have access to send email via Exchange?

Build the list of target locations for the policy.

### Step 2 — Create a DLP policy for outputs in SharePoint/OneDrive

```
Microsoft Purview portal → Data loss prevention → Policies → + Create policy
→ Enterprise applications & devices → Custom → Custom policy
```

**Locations:**
- SharePoint sites: select only the sites where agents operate
- OneDrive accounts: all, or a group-based selection
- Exchange email: create it as its own policy (Learn's best practice is to keep email in a separate DLP policy), and include it if agents have Mail.Send

**Rules:**

**Rule 1 — Block external sharing of AI content with sensitive data:**
```
Condition: Content is shared from Microsoft 365 > with people outside my organization
AND
Condition: Content contains > Sensitivity labels [Confidential / AI-Generated]
Action: Restrict access or encrypt the content in Microsoft 365 locations
        > Block only people outside your organization
        + Notify users with a policy tip + Generate an alert
```

**Rule 2 — Downloads on unmanaged devices (not a DLP rule):**
The DLP pages reviewed list no condition for the management state of the device in the SharePoint and OneDrive locations. Restrict download on unmanaged devices with Conditional
Access (see `secure-ca-policy-agents`) and use Endpoint DLP (Step 4) for managed devices.

**Rule 3 — High-volume access (not a DLP rule):**
DLP has no condition for "activity count in a time window". Detect it in Sentinel with Query 3 of `queries/sentinel-dlp-outputs.kql` and with
`detect-data-exfiltration-agent` (Query 1).

### Step 3 — Simulation mode

Create the policy with **Run the policy in simulation mode** for 7 days.
Review:

```
Microsoft Purview portal → Data loss prevention → Activity explorer / Alerts
→ Filter by the newly created policy
```

Tune the rules if Rule 1 generates false positives. Learn notes that when a file already contains the sensitive content before it is uploaded, external sharing is blocked
proactively and no alert or incident report is sent (the event shows in the audit log and Activity explorer).

### Step 4 — Configure endpoint DLP (if applicable)

To control what happens when a user copies an AI-generated file off their device, create a DLP policy with **Devices** as the location:

```
DLP policy → Locations: Devices
→ Condition: Content contains > Sensitivity labels [Confidential / AI-Generated]
→ Actions: block copy to USB, print, copy to clipboard, upload from the browser
```

Requires Windows devices onboarded to Microsoft Purview.

### Step 5 — Activate and monitor

```
DLP policy → Turn the policy on immediately
```

Monitor during the first week with Sentinel queries.

```kql
// See queries/sentinel-dlp-outputs.kql
```

## Verification

- [ ] Policy covers every identified agent output location
- [ ] Simulation mode returns the expected matches (not only files without sensitive data)
- [ ] The external-sharing rule blocks correctly in test
- [ ] Policy in active enforcement
- [ ] Compliance alerts configured for the security team
- [ ] Endpoint DLP active if agents deposit content on local devices

## Implementation notes

- Queries 1 to 5 read `OfficeActivity` (Microsoft 365 connector): DLP matches are the operations `DLPRuleMatch` and `DlpRuleMatch`, the label of a file is `SensitivityLabelId`, and the recipients of a mail are in `Item.Recipients`.
  They compile and returned rows on the validation workspace; Query 3 and Query 4 of the label list need your label GUIDs
- A DLP event carries the user and the record type, not the policy name; the policy name is in the Purview DLP alerts (`SecurityAlert`)
- The external-sharing events (`AnonymousLinkCreated`, `SharingInvitationCreated`) do not carry the label: join the file with Query 3 or with the label inventory
- To validate the policy: create a file with synthetic data (for example a fictitious credit card number) in SharePoint and verify enforcement
- Removed in this version, because Microsoft Learn (Oct 2026) does not support them: the `MicrosoftDataLossPrevention` and `PurviewAuditLog` tables (they do not exist in the validation workspace),
  a SharePoint DLP condition on an unmanaged device, a DLP condition on activity count, and an Endpoint DLP "clipboard restriction" settings page (copy to clipboard is an action in the policy rule)
