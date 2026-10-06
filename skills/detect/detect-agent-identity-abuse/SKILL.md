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
atlas_techniques: [AML.T0012, AML.T0091.000, AML.T0103]
d3fend_techniques: [D3-UAP, D3-ANET, D3-UGLPA]
nist_ai_rmf: [MEASURE-2.4, MANAGE-4.1]
nist_csf: [DE.CM-03, DE.AE-02, RS.AN-03]
ms_license: [Microsoft Sentinel, Microsoft Entra ID P2]
ms_roles: [Microsoft Sentinel Contributor, Security Reader]
effort_hours: 5
---

## When to use

- After implementing CA policies (Pillar 2): they reduce the abuse but do not detect it
- When the `AADServicePrincipalSignInLogs` logs are active in Sentinel
- To cover the compromised-agent vector that escalates privileges or spawns sub-agents

## Abuse vectors

1. **Token theft**: an agent SP authenticating from an unknown IP (stolen token)
2. **Privilege escalation**: an SP acquiring roles it was not originally assigned
3. **Agent spawning**: an agent creating new SPs or applications (sub-agents)
4. **Impossible travel**: the same SP authenticating from two countries in < 1 hour
5. **CA policy gaps**: a successful sign-in with no Conditional Access policy applied. This skill has no rule for it: read it with `secure-ca-policy-agents` (`queries/sentinel-ca-agents.kql`, Query 1). A report-only result is not a bypass, it only shows what the policy would have blocked

```mermaid
flowchart LR
    subgraph VEC["Abuse vectors"]
        V1["1 Token theft<br/>agent SP signs in from an unknown IP"]
        V2["2 Privilege escalation<br/>SP acquires roles it was not assigned"]
        V3["3 Agent spawning<br/>agent creates new SPs or applications"]
        V4["4 Impossible travel<br/>same SP in two countries in under 1 hour"]
        V5["5 CA policy gaps<br/>a success with no policy applied"]
    end
    subgraph RUL["Rules, enriched by the Step 5 watchlist"]
        R1["Step 1: AISEC-Agent-SignIn-Unknown-IP<br/>every 5 min, High"]
        R3["Step 3: AISEC-Agent-Privilege-Escalation<br/>every 15 min, Critical"]
        R2["Step 2: AISEC-Agent-Spawning-Detected<br/>every 15 min, Critical"]
        R4["Step 4: AISEC-Agent-Impossible-Travel<br/>hourly, High"]
        NR["Not a rule here:<br/>secure-ca-policy-agents, Query 1"]
    end
    V1 --> R1
    V2 --> R3
    V3 --> R2
    V4 --> R4
    V5 -.-> NR

    classDef blue fill:#0078D4,stroke:#333,color:#fff
    classDef purple fill:#5E2750,stroke:#333,color:#fff
    classDef green fill:#107C10,stroke:#333,color:#fff
    classDef orange fill:#FF8C00,stroke:#333,color:#24292f
    class V1,V2,V3,V4,V5 blue
    class R1,R2,R3,R4 green
    class NR orange
```

**How to read it.** Each abuse vector on the left is covered by one analytics rule on the right, and the rules enrich their incidents with the watchlist of known agent service principals from Step 5. The two Critical rules are privilege escalation and agent spawning, and spawning is the highest-risk vector because a compromised agent can create persistent sub-agents with inherited permissions. The fifth vector, CA policy gaps, has no rule in this workflow: the Verification section counts four rules, and the Conditional Access coverage of agent sign-ins is read with Query 1 of `secure-ca-policy-agents`.

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
