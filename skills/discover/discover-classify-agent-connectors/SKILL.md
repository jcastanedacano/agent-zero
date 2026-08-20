---
name: discover-classify-agent-connectors
version: "1.0"
pillar: discover
subdomain: ms-copilot-studio
description: >-
  Classifies the active connectors on Copilot Studio and Power Platform agents
  by risk level according to the type of data accessible, producing an exposure
  matrix as input for govern and protect controls.
tags: [discover, copilot-studio, connectors, data-classification, power-platform]
atlas_techniques: [AML.T0057, AML.T0048]
d3fend_techniques: [D3-AM, D3-NTA]
nist_ai_rmf: [MAP-2.2, MAP-5.1]
nist_csf: [ID.AM-05, ID.RA-01]
ms_license: [Power Platform, M365 E3]
ms_roles: [Power Platform Administrator]
effort_hours: 2
---

## When to use

- After `discover-inventory-agents-copilot-studio`
- As input for `govern-dlp-policy-copilot-prompts` and `protect-purview-ai-hub`
- When a per-agent data exposure matrix is required

## Prerequisites

- Power Platform Admin Center access
- The agent list from Step 1 (previous skill)
- Tenant data type catalog (Purview, if available)

## Workflow

### Step 1 — Export connectors per agent from PP Admin

```
Power Platform Admin Center → Analytics → Power Automate → Connectors
```

Or via the Power Platform Management connector in Power Automate:

```
List connectors → filter by environment → export to CSV
```

### Step 2 — Classify connectors by data category

| Connector | Category | Base risk |
|---|---|---|
| SharePoint | Corporate documents | High |
| Exchange / Outlook | Corporate email | High |
| Dataverse | Business data | High |
| Teams | Communications | Medium |
| Azure Blob Storage | Depends on content | Medium-High |
| Bing Search | Public data | Low |
| Generic HTTP | Unknown | High (unvalidated) |
| ServiceNow / Jira | IT tickets | Medium |
| SAP / Dynamics | ERP / CRM | High |

### Step 3 — Cross-reference connector × agent × owner

Build a table:

| Agent | Connector | Category | Owner | Approved? | Risk |
|---|---|---|---|---|---|
| {name} | SharePoint | Documents | {email} | Yes/No | High |

### Step 4 — Prioritize for remediation

Priority order:
1. Unapproved agents + High-risk connectors
2. Approved agents + connectors not documented in the original scope
3. Generic HTTP connectors with no destination validation

## Verification

- [ ] Connector × agent matrix completed
- [ ] Risk assigned to every combination
- [ ] Generic HTTP connectors with a documented destination URL (undocumented = High risk)
- [ ] Input ready for the govern/protect skill

## Implementation notes

- In tenants with few demo agents, the connector table may hold limited data — use real production data or synthetic data imported via CSV
- Purview AI Hub (if enabled in the tenant) can provide automatic classification of the data accessed by connectors — it complements this inventory
- Prioritize classifying external connectors (generic HTTP, webhooks) over internal Microsoft connectors that already have native DLP coverage
