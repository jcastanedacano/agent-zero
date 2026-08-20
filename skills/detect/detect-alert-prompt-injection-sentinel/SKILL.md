---
name: detect-alert-prompt-injection-sentinel
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Sentinel analytics rule to detect prompt injection and jailbreak in
  Copilot Studio and Azure AI Foundry agent conversations, with Purview
  correlation to prioritize by the sensitivity of the data involved.
tags: [detect, sentinel, prompt-injection, jailbreak, copilot-studio, foundry, aisoc]
atlas_techniques: [AML.T0051, AML.T0054]
d3fend_techniques: [D3-PA, D3-SBV]
nist_ai_rmf: [MEASURE-2.6, MANAGE-3.2]
nist_csf: [DE.CM-01, RS.AN-03]
ms_license: [Microsoft Sentinel, M365 Copilot]
ms_roles: [Microsoft Sentinel Contributor]
effort_hours: 4
---

## When to use

- CopilotStudio_CL and/or FoundryAgents_CL connectors active with data in {workspace-name}
- As the first analytics rule in the AISOC — highest detection ROI
- Covers MITRE ATLAS AML.T0051 (LLM Prompt Injection)

## Critical constraint

Sentinel rejects rules that reference nonexistent or empty `_CL` tables.
Verify before creating the rule:

```kql
union CopilotStudio_CL, FoundryAgents_CL
| summarize LastEvent = max(TimeGenerated), Count = count() by Type
| where LastEvent > ago(24h)
```

If it returns no rows — resolve ingestion before continuing.

## Prompt injection patterns covered

Category 1 — Direct instruction: `ignore previous instructions`, `forget your instructions`
Category 2 — Role impersonation: `you are now`, `act as`, `pretend you are`, `DAN mode`
Category 3 — System bypass: `bypass your`, `jailbreak`, `override your constraints`
Category 4 — Indirect injection: malicious content in documents the agent reads

## Workflow

### Step 1 — Verify table existence (mandatory)

```kql
union CopilotStudio_CL, FoundryAgents_CL
| summarize LastEvent = max(TimeGenerated), Count = count() by Type
| where LastEvent > ago(24h)
```

### Step 2 — Validate the base query in Log Analytics before creating the rule

```kql
// See queries/sentinel-prompt-injection.kql — Query 1
// Run manually and verify it returns results or No results without error
```

### Step 3 — Create the Scheduled Analytics Rule in Sentinel

Parameters:
- **Name**: `AISEC-Prompt-Injection-Detection`
- **Frequency**: every 5 minutes
- **Lookback**: last 24 hours
- **Threshold**: >= 1 result
- **Severity**: dynamic from KQL (High/Medium/Low)
- **MITRE tactics**: Initial Access + AML.T0051 (ATLAS)
- **Incident grouping**: by `UserId` + `AgentName`, 24h window

Via ARM (`2022-12-01-preview`):

```json
{
  "kind": "Scheduled",
  "properties": {
    "displayName": "AISEC-Prompt-Injection-Detection",
    "enabled": true,
    "query": "<KQL from queries/sentinel-prompt-injection.kql>",
    "queryFrequency": "PT5M",
    "queryPeriod": "P1D",
    "triggerOperator": "GreaterThan",
    "triggerThreshold": 0,
    "severity": "Medium",
    "tactics": ["InitialAccess", "Execution"],
    "incidentConfiguration": {
      "createIncident": true,
      "groupingConfiguration": {
        "enabled": true,
        "groupByEntities": ["Account"],
        "lookbackDuration": "PT24H",
        "matchingMethod": "Selected"
      }
    }
  }
}
```

### Step 4 — Create an enrichment playbook (Logic App)

On incident creation:
1. Enrich `UserId` → Entra ID profile (GET /users/{id})
2. Query the user's recent activity in AuditLogs (last 8h)
3. If `AttemptCount >= 10`: suspend the agent's active session
4. Notify the AISOC Teams channel with a summary

### Step 5 — Validate with synthetic data in {workspace-name}

If there is no real traffic, inject a test event via DCR:
```bash
# Use a Data Collection Rule to send a synthetic event to CopilotStudio_CL
```

## Verification

- [ ] Validation query returns rows or No results without a table error
- [ ] Rule in Enabled state in Sentinel Analytics
- [ ] Test incident generated with synthetic data
- [ ] Playbook runs with no errors in test mode
- [ ] Time to detect < 10 minutes from the event

## Implementation notes

- Verify the `CopilotStudio_CL` and `FoundryAgents_CL` tables exist and hold data before creating the analytics rule
- Recommended Sentinel API version: `2022-12-01-preview` for SecurityInsights resources
- Incident grouping by `UserId` plus `AgentName` reduces noise significantly in environments with multiple users testing
- In production: tune the minimum `JailbreakScore` against the false positive rate observed in the first 30 days
