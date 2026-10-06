---
name: detect-agent-identity-abuse
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Detects abuse of AI agent identities in Entra ID, including token theft,
  unauthorized privilege escalation, agent service principals authenticating
  from unexpected locations or IPs, and creation of new agents by
  existing agents (agent spawning).
tags: [detect, sentinel, entra, identity-abuse, token-theft, privilege-escalation, agent-spawning]
atlas_techniques: [AML.T0091.000, AML.T0040, AML.T0084, AML.T0103]
d3fend_techniques: [D3-UAP, D3-ANET, D3-UGLPA]
nist_ai_rmf: [MEASURE-2.4, MANAGE-4.1]
nist_csf: [DE.CM-03, DE.AE-02, RS.AN-03]
ms_license: [Microsoft Sentinel, Microsoft Entra ID P2]
ms_roles: [Microsoft Sentinel Contributor, Security Reader]
effort_hours: 5
---

## When to use

- After implementing CA policies (Pillar 2) — to detect bypasses
- When the `AADServicePrincipalSignInLogs` logs are active in Sentinel
- To cover the compromised-agent vector that escalates privileges or spawns sub-agents

## Abuse vectors covered

1. **Token theft**: an agent SP authenticating from an unknown IP (stolen token)
2. **Privilege escalation**: an SP acquiring roles it was not originally assigned
3. **Agent spawning**: an agent creating new SPs or applications (sub-agents)
4. **Impossible travel**: the same SP authenticating from two countries in < 1 hour
5. **CA policy bypass**: a successful authentication that should have been blocked

## Workflow

### Step 1 — Create rule: SP sign-in from a non-corporate IP

```kql
// See queries/sentinel-identity-abuse.kql — Query 1
// Correlates AADServicePrincipalSignInLogs with CA Named Locations
```

Configuration:
- **Name**: `AISEC-Agent-SignIn-Unknown-IP`
- **Frequency**: every 5 minutes
- **Severity**: High

### Step 2 — Create rule: agent spawning (agent creates new apps/SPs)

```kql
// See queries/sentinel-identity-abuse.kql — Query 2
// Detects when the principal initiating an SP creation is another SP (not a human)
```

Configuration:
- **Name**: `AISEC-Agent-Spawning-Detected`
- **Frequency**: every 15 minutes
- **Severity**: Critical — highest-risk vector

### Step 3 — Create rule: agent privilege escalation

```kql
// See queries/sentinel-identity-abuse.kql — Query 3
```

Configuration:
- **Name**: `AISEC-Agent-Privilege-Escalation`
- **Frequency**: every 15 minutes
- **Severity**: Critical

### Step 4 — Create rule: impossible travel for service principals

```kql
// See queries/sentinel-identity-abuse.kql — Query 4
// Two successful authentications of the same SP from different countries in < 60 min
```

Configuration:
- **Name**: `AISEC-Agent-Impossible-Travel`
- **Frequency**: hourly
- **Severity**: High

### Step 5 — Link to a watchlist of known agent SPs

Create a watchlist in Sentinel with the registered agent SPs:

```
Sentinel → Watchlists → New → Upload CSV
Columns: AgentName, ServicePrincipalId, AppId, RiskLevel, Owner
```

Use the watchlist in the rules to enrich incidents with
context from the Pillar 1 risk register.

## Verification

- [ ] `AADServicePrincipalSignInLogs` has data in the workspace
- [ ] The 4 analytics rules created and in Enabled state
- [ ] Agent SP watchlist loaded
- [ ] Test incident: authenticate an SP from an external IP and verify the alert
- [ ] Agent spawning: manually create an SP from an SP context and verify detection

## Implementation notes

- `AADServicePrincipalSignInLogs` requires Entra ID P2 or the Entra ID data connector active in Sentinel
- For impossible travel on service principals: agent SPs in Azure rarely have variable IPs — any IP geolocation change is suspicious
- Agent spawning is the highest-risk vector in multi-agent architectures: a compromised agent can create persistent sub-agents with inherited permissions
- Correlate with `AuditLogs` in Sentinel to detect new SP creation in the same interval as the compromised agent
