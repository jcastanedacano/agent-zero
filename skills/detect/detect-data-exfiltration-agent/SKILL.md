---
name: detect-data-exfiltration-agent
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Detects data exfiltration patterns through AI agents, including bulk file
  downloads via an agent, sensitive data transfer to external connectors,
  and use of agents as a proxy to extract corporate information toward
  unauthorized destinations.
tags: [detect, sentinel, exfiltration, data-loss, sharepoint, exchange, aisoc]
atlas_techniques: [AML.T0086, AML.T0057]
d3fend_techniques: [D3-NTA, D3-DLP, D3-EAC]
nist_ai_rmf: [MEASURE-2.6, MANAGE-3.2]
nist_csf: [DE.CM-01, DE.AE-03, RS.AN-03]
ms_license: [Microsoft Sentinel, Microsoft Purview E3]
ms_roles: [Microsoft Sentinel Contributor, Security Reader]
effort_hours: 5
---

## When to use

- Agents with access to SharePoint, Exchange, or production databases
- When output DLP is active (Pillar 4) and correlation in Sentinel is needed
- To detect the agent-as-intermediary exfiltration vector:
  a user asks the agent to summarize/export data → the agent accesses a large
  volume → the data leaves via an unmonitored channel

## Exfiltration vectors covered

1. **Bulk access**: an agent accesses N files in a short time from a single user request
2. **Summary as exfil**: a user asks for a summary of confidential documents → copies the text out
3. **Connector abuse**: an agent uses a generic HTTP connector to send data to an external URL
4. **Email relay**: an agent with `Mail.Send` permission sends data to an external account
5. **Cross-tenant**: an agent in a multi-tenant context shares data across tenants

## Workflow

### Step 1 — Create rule: bulk file access via an agent

```kql
// See queries/sentinel-exfiltration.kql — Query 1
// Threshold: > 50 unique files in 30 minutes by the same user via an agent
```

Sentinel configuration:
- **Name**: `AISEC-Agent-Bulk-File-Access`
- **Frequency**: every 15 minutes
- **Lookback**: last 2 hours
- **Severity**: High

### Step 2 — Create rule: agent sending email to external domains

```kql
// See queries/sentinel-exfiltration.kql — Query 2
```

Configuration:
- **Name**: `AISEC-Agent-Email-External-Domain`
- **Frequency**: every 5 minutes
- **Lookback**: last 24 hours
- **Severity**: High (Critical if it contains sensitive data)

### Step 3 — Create rule: outbound HTTP calls from agents to unapproved URLs

```kql
// See queries/sentinel-exfiltration.kql — Query 3
// Requires Foundry agents to have network logging active
```

### Step 4 — Correlate with Purview DLP events

```kql
// See queries/sentinel-exfiltration.kql — Query 4
// Join agent events with DLP matches to prioritize by sensitivity
```

### Step 5 — Configure a high-volume alert in Purview AI Hub

```
Purview AI Hub → Policies → Create policy
→ Type: Data volume threshold
→ Threshold: > 100 interactions in 1 hour per user
→ Action: Alert + Restrict
```

## Verification

- [ ] Bulk access rule created and tested with synthetic data
- [ ] External email rule created (if agents have Mail.Send)
- [ ] Correlation with Purview DLP active
- [ ] Test incident generated with simulated bulk access
- [ ] Containment playbook linked to the rules (see next skill)

## Implementation notes

- Activate the Purview Audit connector in Sentinel to enable DLP correlation in the exfiltration queries
- To simulate exfiltration in a test tenant: create a SharePoint folder with 60+ test files and access them all in one session
- The email relay vector requires the agent SP to hold `Mail.Send` — verify with the `secure-least-privilege-agent-identity` skill
- If the agent HTTP connector has no logging enabled: use NSG flow logs as a proxy to detect egress
