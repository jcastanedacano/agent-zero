---
name: detect-anomalous-agent-behavior
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Detects statistical deviations in AI agent behavior against its baseline,
  including unusual API call volume, access to resources outside the normal
  pattern, anomalous operating hours, and sudden changes in the type of data
  processed.
tags: [detect, sentinel, behavioral-analytics, anomaly, baseline, aisoc, ueba]
atlas_techniques: [AML.T0040, AML.T0056, AML.T0048]
d3fend_techniques: [D3-NTA, D3-PA, D3-ANET]
nist_ai_rmf: [MEASURE-2.6, MEASURE-2.5]
nist_csf: [DE.AE-01, DE.CM-06]
ms_license: [Microsoft Sentinel, Microsoft Sentinel UEBA]
ms_roles: [Microsoft Sentinel Contributor]
effort_hours: 6
---

## When to use

- Post-deployment of basic rules (prompt injection) — adds behavioral detection
- When agents have enough history (minimum 14 days) to establish a baseline
- To detect compromised agents that do not use known injection techniques

## Detection logic

A compromised or misconfigured agent manifests as:
- Call volume 3x+ over its daily baseline
- Access to resources it had never touched before
- Operation outside the hours it is normally invoked
- Change in the type of data accessed (from read-only to write)
- Unusually low latency (automation) or high latency (bulk processing)

## Workflow

### Step 1 — Establish a per-agent baseline (minimum 14 days)

```kql
// See queries/sentinel-agent-baseline.kql — Query 1
// Run first to verify there is enough history
```

If there are fewer than 7 days of data: document it and wait before activating
the baseline-based anomaly rules.

### Step 2 — Create rule: anomalous call volume

```kql
// See queries/sentinel-agent-baseline.kql — Query 2
// Threshold: > 3x daily baseline
```

Sentinel rule configuration:
- **Name**: `AISEC-Agent-Anomalous-Volume`
- **Frequency**: hourly
- **Lookback**: last 24 hours
- **Severity**: Medium (escalate to High if the agent has High-risk connectors)

### Step 3 — Create rule: access to new resources

```kql
// See queries/sentinel-agent-baseline.kql — Query 3
// Detect resources accessed for the first time in the last 7 days
```

Configuration:
- **Name**: `AISEC-Agent-New-Resource-Access`
- **Frequency**: every 15 minutes
- **Lookback**: last 24 hours
- **Severity**: High (if the resource is SharePoint or Exchange)

### Step 4 — Create rule: off-hours operation

```kql
// See queries/sentinel-agent-baseline.kql — Query 4
```

Configuration:
- **Name**: `AISEC-Agent-Off-Hours-Operation`
- **Frequency**: hourly
- **Lookback**: last 8 hours
- **Severity**: Medium

### Step 5 — Enable UEBA for agents

```
Sentinel → Settings → UEBA
→ Enable entity behavior analytics
→ Entities: Accounts (include service principals if in scope)
```

UEBA generates the `BehaviorAnalytics` table with per-entity anomaly scores.

### Step 6 — Correlate with UEBA scores

```kql
// See queries/sentinel-agent-baseline.kql — Query 5
```

## Verification

- [ ] Baseline computed with a minimum of 7 days of data (14 recommended)
- [ ] The three analytics rules created and in Enabled state
- [ ] UEBA enabled and the `BehaviorAnalytics` table has data
- [ ] Test: artificially modify the call volume of a test agent
  and verify it generates an incident

## Implementation notes

- `BehaviorAnalytics` (UEBA) requires explicit activation in Sentinel — verify under Settings → UEBA before using the table
- For agents with little history (under 7 days of data): use a 7-day lookback instead of 14 for the baseline
- Anomaly rules have a higher false positive rate than signature rules — tune thresholds against observed behavior
- Start with a single agent type (for example Copilot Studio) to validate the baseline before extending to all agents
