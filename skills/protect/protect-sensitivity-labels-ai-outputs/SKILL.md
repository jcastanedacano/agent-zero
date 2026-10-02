---
name: protect-sensitivity-labels-ai-outputs
version: "1.0"
pillar: protect
subdomain: ms-purview-ai
description: >-
  Configures auto-labeling in Purview so that documents and files generated
  or processed by AI agents inherit appropriate sensitivity labels, ensuring
  agent outputs containing sensitive data are automatically classified and
  protected with encryption and access restrictions.
tags: [protect, purview, sensitivity-labels, auto-labeling, classification, ai-outputs]
atlas_techniques: [AML.T0086, AML.T0057]
d3fend_techniques: [D3-DLP, D3-EAC]
nist_ai_rmf: [MANAGE-2.2, GOVERN-6.1]
nist_csf: [PR.DS-01, PR.DS-02]
ms_license: [Microsoft Purview E3, Azure Information Protection P2]
ms_roles: [Compliance Administrator, Information Protection Administrator]
effort_hours: 6
---

## When to use

- Agents that generate documents, reports, or files as output
- Agents with access to already-classified data that could copy or transform content
- When agent outputs need to inherit the classification of the source data

## Implementation constraint

Creating sensitivity labels and auto-labeling policies has limited support
via ARM/API. Configuring through the **Microsoft Purview Compliance Portal**
is the reliable path for initial configuration.
Activation and minor adjustments can be done via Graph API
(`/beta/informationProtection/policy/labels`).

## Recommended label hierarchy for AI outputs

```
Public
  └── Internal Use Only
        └── Confidential
              ├── Confidential \ AI-Generated        ← agent outputs
              └── Confidential \ Customer Data
                    └── Highly Confidential
                          └── Highly Confidential \ AI-Generated
```

The `AI-Generated` sub-label identifies which content was produced or
processed by an agent, independent of the sensitivity level.

## Workflow

### Step 1 — Audit existing sensitivity labels in the tenant

```
Purview Compliance Portal → Information protection → Labels
```

If no label structure exists: create the base hierarchy before continuing.
If one already exists: assess whether it needs sub-labels for AI-generated content.

### Step 2 — Create the AI-Generated sub-label

```
Information protection → Labels → [Confidential] → Add sub-label
```

Sub-label configuration:
- **Name**: `AI-Generated`
- **Display name**: `Confidential / AI-Generated`
- **Description**: "Content generated or processed by an AI agent"
- **Encryption**: inherit from the parent label or configure specifically
- **Content marking**: add the watermark "AI Generated - Review before sharing"
- **Auto-labeling**: No (configured in a separate policy)

### Step 3 — Create the auto-labeling policy for agent outputs

```
Information protection → Auto-labeling policies → Create policy
```

Configuration:
- **Name**: `AutoLabel-AI-Agent-Outputs`
- **Locations**: SharePoint sites where agents deposit outputs,
  OneDrive of users who use agents, Exchange if applicable
- **Rules**:
  - Content contains sensitive info types: [tenant-relevant types]
  - OR content was created/modified by: [known agent service principals]
- **Label to apply**: `Confidential / AI-Generated`
- **Mode**: Simulation first (7 days), then enforcement

### Step 4 — Configure label inheritance in Copilot Studio

For agents that access already-classified documents:

```
Purview → Information protection → Settings → Inheritance
→ Enable label inheritance from email attachments and documents
```

When an agent extracts content from a `Confidential` document,
the output must inherit at least that classification level.

### Step 5 — Validate in simulation mode

```
Auto-labeling policies → [PolicyName] → Simulation results
```

Review which files would be labeled. Tune rules to eliminate
false positives before activating enforcement.

### Step 6 — Activate and monitor

```
Auto-labeling policies → [PolicyName] → Turn on policy
```

Monitor in Sentinel with `MicrosoftDataLossPrevention`
and `PurviewAuditLog` queries.

```kql
// See queries/sentinel-label-coverage.kql
```

## Verification

- [ ] `AI-Generated` sub-label created under `Confidential`
- [ ] Auto-labeling policy in simulation mode returns the expected matches
- [ ] False positives reviewed and rules tuned
- [ ] Policy in active enforcement
- [ ] Agent output documents show the applied label
- [ ] Watermark visible on labeled documents

## Implementation notes

- Graph API beta endpoint for labels: `/beta/informationProtection/policy/labels` — verify availability and stability before using it in production scripts
- Auto-labeling can take up to 24 hours to process existing files in SharePoint — do not assume immediate coverage on activation
- To validate auto-labeling: create a test document with synthetic credit-card-type data and confirm the label is applied
- Prioritize manual labeling of SharePoint sites used as agent knowledge sources before enabling retrieval
