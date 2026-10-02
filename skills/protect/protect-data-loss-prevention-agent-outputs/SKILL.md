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
  input prompts; this skill protects generated outputs/files

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
Purview Compliance Portal → Data loss prevention → Policies → Create policy
→ Custom → Custom policy
```

**Locations:**
- SharePoint sites: select only the sites where agents operate
- OneDrive accounts: all, or a group-based selection
- Exchange email: include if agents have access to Mail.Send

**Rules:**

**Rule 1 — Block external sharing of AI content with sensitive data:**
```
Condition: Content contains sensitivity label [Confidential / AI-Generated]
AND
Condition: Content is shared with [people outside the organization]
Action: Block access + Notify user + Generate alert
```

**Rule 2 — Restrict downloading AI files on unmanaged devices:**
```
Condition: Content contains sensitivity label [Confidential / AI-Generated]
AND
Condition: Device is not managed (Intune)
Action: Block download + Allow view only
```

**Rule 3 — Alert on high-volume access to AI files in a short window:**
```
Condition: Content contains sensitivity label [AI-Generated]
AND
Condition: Activity count > 50 in 30 minutes (same user)
Action: Generate alert + Restrict access
```

### Step 3 — Simulation mode

Enable **Test mode** for 7 days.
Review:

```
DLP → Reports → DLP policy matches
→ Filter by the newly created policy
```

Tune thresholds if Rule 3 generates false positives.

### Step 4 — Configure endpoint DLP (if applicable)

To control what happens when a user downloads an AI-generated file to their device:

```
DLP → Endpoint DLP settings → Browser and app restrictions
→ Add unallowed apps: non-corporate applications
→ Clipboard restriction: restrict copy-paste of AI-Generated content
```

Requires devices onboarded to MDE with Endpoint DLP enabled.

### Step 5 — Activate and monitor

```
DLP policy → Turn it on right away
```

Monitor during the first week with Sentinel queries.

```kql
// See queries/sentinel-dlp-outputs.kql
```

## Verification

- [ ] Policy covers every identified agent output location
- [ ] Test mode returns the expected matches (not only files without sensitive data)
- [ ] The external-sharing rule blocks correctly in test
- [ ] Policy in active enforcement
- [ ] Compliance alerts configured for the security team
- [ ] Endpoint DLP active if agents deposit content on local devices

## Implementation notes

- Endpoint DLP requires devices onboarded to Microsoft Defender for Endpoint (MDE) — verify onboarding status before enabling this protection vector
- The high-volume rule can generate false positives for users running broad searches — tune the threshold
- To validate the policy: create a file with synthetic data (for example a fictitious credit card number) in SharePoint and verify enforcement
