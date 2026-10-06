---
name: govern-dlp-policy-copilot-prompts
version: "1.0"
pillar: govern
subdomain: ms-purview-ai
description: >-
  Configures Microsoft Purview DLP for Microsoft 365 Copilot interactions: blocks prompts
  that contain sensitive information types, keeps files and emails with chosen sensitivity
  labels out of Copilot responses, and states what Learn documents for Copilot Studio agents.
tags: [govern, purview, dlp, copilot-studio, data-protection, prompt-security]
atlas_techniques: [AML.T0057, AML.T0086]
d3fend_techniques: [D3-CF, D3-FCR]
nist_ai_rmf: [MEASURE-2.10, MANAGE-1.3]
nist_csf: [PR.DS-01, PR.DS-10]
ms_license: [Microsoft Purview, M365 E5 (restriction of files and emails by label)]
ms_roles: [Compliance Administrator, DLP Compliance Management]
effort_hours: 6
---

## When to use

- Users with access to customer (PII), financial, or strategic data who work with Microsoft 365 Copilot
- Before enabling Copilot and agents in production environments with real data
- Compliance requirement (data regulations in financial/healthcare sectors)

## Known constraint

DLP policies for Copilot are created in the Microsoft Purview portal. Configuration through the portal is the reliable path for these policies.

## What DLP can do for Copilot (Microsoft Learn)

The policy location is **Microsoft 365 Copilot and Copilot Chat**. It supports these conditions and actions:

| Condition | Action | Effect |
|---|---|---|
| Content contains > Sensitivity labels | Prevent Copilot from processing content | Copilot does not use the file or email in the response; the item can still appear in the citations |
| Content contains > Sensitive information types | Prevent Copilot from processing content > Processing prompts (preview) | Copilot does not answer a prompt that contains the chosen types, and does not use it for searches |
| Content contains > Sensitive information types | Prevent Copilot from processing content > Performing Web Searches | The prompt is not sent to an external web search provider; Copilot answers from internal sources |
| Email is received from > External users (preview) | Prevent Copilot from processing content | External email is left out of grounding, summarization and citation |

Limits that change the design:
- A rule cannot combine the sensitive information type and the sensitivity label conditions: create one rule per condition
- DLP evaluates prompts and the items Copilot would use. It does not evaluate Copilot's response text, so a rule that "alerts on responses with confidential data" does not exist
- For files, the policy is evaluated when the file opens in Word, Excel or PowerPoint; calendar invites are not supported; emails are covered from January 1, 2025
- The restriction of files and emails by label needs a Microsoft 365 E5-class license; DLP for prompts is available to all Copilot users (Purview service description)
- For agents built in Copilot Studio, Learn documents one capability: when the knowledge source is SharePoint, a DLP policy scoped to the Microsoft 365 Copilot location can
  stop them from processing content with a chosen sensitivity label. Learn does not document blocking sensitive information types in prompts for Copilot Studio agents

## Prerequisites

- Microsoft Purview with DLP for Microsoft 365 Copilot available to the tenant
- Sensitivity labels configured in the tenant (for the label rule)
- DLP Compliance Management permissions
- Access to the Microsoft Purview portal (`purview.microsoft.com`)

## Workflow

### Step 1 — Choose the sensitive information types and labels

Review the built-in and custom sensitive information types for your sector and country. Learn's examples are credit card numbers, passport numbers and Social Security numbers.
Decide which sensitivity labels (for example Highly Confidential) Copilot must not process.

### Step 2 — Create the DLP policy for Copilot

```
Microsoft Purview portal → Data loss prevention → Policies → + Create policy
→ Custom → Custom policy
→ Locations: Microsoft 365 Copilot and Copilot Chat = On
```

**Rule 1 — Block sensitive prompts:**
- Condition: Content contains > Sensitive information types [chosen types]
- Action: Prevent Copilot from processing content > Processing prompts

**Rule 2 — Keep sensitive data out of web search (separate rule):**
- Condition: Content contains > Sensitive information types [chosen types]
- Action: Prevent Copilot from processing content > Performing Web Searches

**Rule 3 — Exclude labeled files and emails (separate rule):**
- Condition: Content contains > Sensitivity labels [Highly Confidential and any others you chose]
- Action: Prevent Copilot from processing content

Microsoft also creates a default policy, **Default DLP policy - Protect sensitive M365 Copilot interactions**, in simulation mode: it only logs matches until you change its mode.

### Step 3 — Simulation mode first

Run the policy in **simulation mode** for 7 days and review the matches in the Microsoft Purview portal (DSPM for AI activity explorer, **AI activities** tab, **DLP rule match** events).
Tune the types and labels to remove false positives.

### Step 4 — Activate enforcement

Switch the policy to **Turn the policy on immediately**. Turn on **Incident reports** and add the security team as recipients (Microsoft's recommendation).

### Step 5 — Add visibility with DSPM for AI

```
Microsoft Purview portal → DSPM for AI (classic) → Recommendations
→ Detect risky interactions in AI apps  (Insider Risk Management policy)
→ Detect unethical behavior in AI apps  (Communication Compliance policy)
```

See `protect-purview-ai-hub-monitoring`.

### Step 6 — Monitor in Sentinel

```kql
// See queries/sentinel-dlp-agents.kql
```

## Verification

- [ ] Sensitive information types and labels chosen
- [ ] Policy in simulation mode returns matches in the activity explorer
- [ ] False positives reviewed and tuned
- [ ] Policy in active enforcement
- [ ] Incident reports go to the security team
- [ ] DSPM for AI recommendations actioned

## Implementation notes

- DLP rule matches for Exchange, SharePoint and OneDrive reach Sentinel through the Microsoft 365 connector (`OfficeActivity`, operations `DLPRuleMatch` and `DlpRuleMatch`), and Purview DLP alerts through
  `SecurityAlert`. The matches that happen during Copilot interactions are in the DSPM for AI activity explorer, and the Copilot audit record lists the resources a policy restricted in `AccessedResources[].PolicyDetails`
- On the validation workspace Queries 1 to 3 returned rows (DLP matches in Exchange, SharePoint and OneDrive, and DLP alerts grouped by policy), and Query 4 returned none: the `PolicyDetails` key exists and is empty
- To validate the policy without real data: use synthetic credit-card-formatted data in a test prompt and confirm Copilot does not answer
- Removed in this version, because Microsoft Learn (Oct 2026) does not support them: the `MicrosoftDataLossPrevention` table (it does not exist in the validation workspace), a "Microsoft Copilot (preview)"
  location, a rule that alerts on the response text, and the Purview AI Hub settings page
