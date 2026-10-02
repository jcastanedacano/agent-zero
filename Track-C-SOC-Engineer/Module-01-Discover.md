# Module 01 — Discover & Prioritize | Track C

**Duration:** 90 minutes  
**Tables:** `AgentsInfo`, `CloudAppEvents`, `OfficeActivity`, `MicrosoftPurviewInformationProtection`  
**Minimum role:** Security Reader (Defender + Sentinel)

---

## Learning Objective

At the end of this module, you will be able to configure Defender AI Agent Inventory and Purview DSPM for AI to detect active agents in an M365 E5 tenant, and write KQL queries to classify agents by management status and surface exposure gaps.

---

## Agenda

| Time | Activity | Type |
|------|----------|------|
| 15 min | Technical architecture: how Defender and Purview detect agents — tables, connectors, gaps | Explanation |
| 10 min | `AgentsInfo` schema walkthrough: fields, values, limitations | Explanation |
| 55 min | Lab: KQL queries for agent inventory and classification | Lab |
| 10 min | Results review + playbook section 1 documentation | Discussion |

---

## Core Content

1. **Differentiated telemetry by agent type:** Copilot Studio and Azure AI Foundry generate telemetry in `AgentsInfo`. Power Automate with AI steps appears in `CloudAppEvents`. Local agents (Claude Code, MCP servers, LLM scripts on endpoints) generate no cloud signal without an active MDE endpoint connector — this is the structural blind spot that no Sentinel query can resolve without the connector.

2. **Shadow AI as the baseline condition:** Agent Builder allows any licensed user to create and publish an agent without approval. These agents appear in Agent 365 Registry but without an Entra Agent ID, no technical owner, and no DLP review. They are not the exception — they are the most common case in M365 E5 tenants with Copilot enabled.

3. **Applicable Microsoft controls:** Purview DSPM for AI maps agent interactions with sensitive data. Defender AI Agent Inventory requires active connectors per platform. SharePoint Advanced Management audits which sites agents access. Agent 365 is the central registry, but only covers agents that completed the registration process.

4. **The cost of an incomplete inventory:** An agent absent from inventory does not appear in Conditional Access policies, has no owner for escalation, and is not covered by Sentinel analytics rules. The visibility gap is the gap across every subsequent security layer.

---

## Background

### Why local agents are the hardest gap

Defender AI Agent Inventory covers Copilot Studio, Azure AI Foundry, AWS Bedrock, GCP Vertex, and 20+ agent types — but only when the relevant connector is active and endpoints are onboarded via MDE. Agents running locally (Claude Code, MCP servers, OpenClaw on endpoints) generate no cloud telemetry without an active endpoint connector. The gap isn't a policy problem — it's a telemetry problem.

### What `AgentsInfo` doesn't capture by default

- Agents deployed via third-party APIs without Agent 365 registration
- Local agents on endpoints without MDE onboarding
- Power Automate flows with AI steps that aren't registered as agents
- Agents created via Agent Builder (M365 Copilot) that bypass Copilot Studio registry

### `AgentsInfo` schema — official fields (July 2026)

| Field | Type | Notes |
|-------|------|-------|
| `Timestamp` | datetime | Use for time filters (XDR table) |
| `AgentId` | string | Unique agent identifier |
| `Name` | string | Agent display name (not `AgentName`, confirmed live via `getschema` against tenant `AgentsInfo`, Sep 2026) |
| `Platform` | string | Copilot Studio, Azure AI Foundry, etc. |
| `LifecycleStatus` | string | Active / Blocked / Uninstalled / Deleted |
| `PublishedStatus` | string | Draft / Published |
| `Owners` | dynamic | Can be null — use `isnull()` check |
| `EntraAgentID` | string | Object id of the agent identity (a service principal). Empty if the agent has no agent identity in this tenant |
| `EntraBlueprintID` | string | Id of the agent identity blueprint the agent derives from. Can be present while `EntraAgentID` is empty (blueprint only) |
| `CreatedDateTime` | datetime | Agent creation timestamp |
| `McpServers` | dynamic | External MCP endpoints declared |
| `DeclaredTools` | dynamic | Tool definitions declared by agent |

---

## Lab

### Setup

1. Open **Microsoft Defender XDR** → Advanced Hunting, or **Microsoft Sentinel** → Logs
2. Verify `AgentsInfo` returns results: run `AgentsInfo | take 5`
3. If the table is empty, verify Agent 365 / Microsoft 365 Copilot license is assigned and allow 2–4 hours for propagation. Use `CloudAppEvents` as a fallback for agent activity signals.

---

### Step 1 — Full agent inventory by platform and lifecycle status

```kql
AgentsInfo
| where Timestamp > ago(30d)
| summarize
    LastSeen = max(Timestamp),
    AgentCount = dcount(AgentId),
    WithoutOwner = dcountif(AgentId, isnull(Owners) or array_length(Owners) == 0),
    NoEntraIdentity = dcountif(AgentId, isempty(EntraAgentID) and isempty(EntraBlueprintID)),
    BlueprintOnly = dcountif(AgentId, isempty(EntraAgentID) and isnotempty(EntraBlueprintID))
    by Platform, LifecycleStatus, PublishedStatus, Name
| extend RiskLevel = case(
    WithoutOwner > 0 and NoEntraIdentity > 0, "High",
    WithoutOwner > 0 or NoEntraIdentity > 0 or BlueprintOnly > 0, "Medium",
    LifecycleStatus in ("Blocked", "Deleted"), "Medium",
    "Low"
)
| extend RiskRank = case(RiskLevel == "High", 0, RiskLevel == "Medium", 1, 2)
| sort by RiskRank asc, LastSeen desc
| project Name, Platform, LifecycleStatus, PublishedStatus, RiskLevel,
          WithoutOwner, NoEntraIdentity, BlueprintOnly, AgentCount, LastSeen
```

**Expected output:** Agent inventory grouped by platform and lifecycle status, classified by risk level based on ownership and Entra identity coverage.

**Reading the identity columns:** `NoEntraIdentity` counts agents with neither `EntraAgentID` nor `EntraBlueprintID`; `BlueprintOnly` counts agents that have a blueprint but no agent identity in this tenant. They are different findings. The second is common for third-party agents (in a validated tenant they appeared under platform `Other`) and means *confirm how the agent authenticates*, not *identity laundering*. An agent with an `EntraAgentID` has a dedicated identity whether or not a blueprint is recorded. `High` requires no owner **and** no Entra identity at all. Counts are distinct agents (`dcountif` on `AgentId`), not snapshot rows: `AgentsInfo` keeps a snapshot per agent per day.

**Document in your playbook:** How many agents appear as High risk? Which platforms have the highest count of agents without an owner? How many are `BlueprintOnly`, and who is accountable for each vendor?

---

### Step 2 — Shadow AI — agents without owner or Entra identity

```kql
AgentsInfo
| where Timestamp > ago(30d)
| where isnull(Owners) or array_length(Owners) == 0
    or isempty(EntraAgentID)
| extend OwnersStr = tostring(Owners)
| distinct AgentId, Name, Platform, CreatedDateTime, OwnersStr, EntraAgentID, EntraBlueprintID
| extend OwnerDisplay = iff(OwnersStr == '' or OwnersStr == '[]', 'UNASSIGNED', OwnersStr)
| extend NoOwner = (OwnersStr == "" or OwnersStr == "[]")
| extend IdentityState = case(
    isnotempty(EntraAgentID), "AgentIdentity",
    isnotempty(EntraBlueprintID), "BlueprintOnly",
    "NoEntraIdentity"
)
| extend RiskSignal = case(
    IdentityState == "NoEntraIdentity" and NoOwner,
        "No owner + no Entra identity — shadow AI",
    IdentityState == "NoEntraIdentity",
        "No Entra identity (no agent identity, no blueprint) — identity laundering risk",
    IdentityState == "BlueprintOnly" and NoOwner,
        "No owner; blueprint only, no agent identity in this tenant — confirm how it authenticates",
    IdentityState == "BlueprintOnly",
        "Blueprint only, no agent identity in this tenant — confirm how it authenticates",
    "No owner assigned"
)
| extend DaysSinceCreation = datetime_diff('day', now(), CreatedDateTime)
| sort by DaysSinceCreation desc
| project AgentId, Name, Platform, OwnerDisplay, IdentityState, RiskSignal, DaysSinceCreation
```

**Expected output:** List of agents lacking an owner or an agent identity, each with an `IdentityState` (`NoEntraIdentity`, `BlueprintOnly`, or `AgentIdentity`) and a `RiskSignal`. Shadow AI is the `NoEntraIdentity` rows without an owner: operating without formal registration or ownership.

**Note:** `Owners` is a dynamic field that can be null (third-party or external agents) or an empty array. The null check `isnull(Owners) or array_length(Owners) == 0` is required to capture both cases.

---

### Step 3 — SharePoint sites accessed by agents without sensitivity labels

```kql
OfficeActivity
| where TimeGenerated > ago(7d)
| where RecordType == "SharePointFileOperation"
    and UserAgent has_any ("agent", "copilot", "power-automate", "bot")
| join kind=leftouter (
    MicrosoftPurviewInformationProtection
    | where TimeGenerated > ago(7d)
    | where Activity == "LabelApplied"
    | distinct ObjectId
) on $left.ObjectId == $right.ObjectId
| where isempty(ObjectId1)
| summarize
    AgentAccesses = count(),
    LastAccess = max(TimeGenerated)
    by SiteUrl, OfficeObjectId, UserId
| sort by AgentAccesses desc
| project SiteUrl, OfficeObjectId, AgentAccesses, LastAccess, UserId
```

**Expected output:** Sites accessed by agents that have no sensitivity label — oversharing candidates.

**Critical note:** Remediate oversharing in SharePoint **before** enabling retrieval on any agent. Every ACL error in the corpus is inherited by the agent and amplified to all users interacting with it.

---

### Step 4 — New agent registrations in the last 24 hours

```kql
AgentsInfo
| where Timestamp > ago(1d)
| where CreatedDateTime > ago(1d)
| extend OwnerDisplay = iff(isnull(Owners) or array_length(Owners) == 0, "UNASSIGNED", tostring(Owners))
| project
    AgentId,
    Name,
    Platform,
    OwnerDisplay,
    LifecycleStatus,
    PublishedStatus,
    CreatedDateTime,
    DeclaredTools,
    McpServers
| extend AlertDetail = strcat(
    "New agent registered: ", Name,
    " | Platform: ", Platform,
    " | Owner: ", OwnerDisplay,
    " | MCP servers: ", tostring(array_length(McpServers))
)
| sort by CreatedDateTime desc
```

**Expected output:** Agents registered in the last 24 hours — candidate for a Sentinel analytics rule with hourly frequency.

---

### Step 5 — Convert Step 4 to a Sentinel Analytics Rule

1. In Microsoft Sentinel → **Analytics** → **Create** → **Scheduled query rule**
2. Name: `New Agent Without Owner or Entra Identity`
3. Paste the query from Step 4; add filter: `| where isnull(Owners) or array_length(Owners) == 0 or (isempty(EntraAgentID) and isempty(EntraBlueprintID))` (blueprint-only agents are left to the Step 2 hunting query; alerting on each one would be noise)
4. Frequency: Every 1 hour | Lookback: 1 day
5. Severity: **Medium**
6. Map entity: `AgentId` → Custom entity
7. Save and enable

---

## Playbook Section 1 — Document Your Findings

Add to your [Incident Response Playbook Template](./Templates/Incident-Response-Playbook-Template.md):

```markdown
## Section 1: Agent Inventory Baseline

**Date of assessment:** [DATE]
**Tenant:** [TENANT NAME]

### Inventory Summary
| Metric | Value |
|--------|-------|
| Total agents detected | |
| Agents without owner | |
| Agents with no Entra identity (no agent identity, no blueprint) | |
| Blueprint-only agents (no agent identity in this tenant) | |
| Shadow AI (no owner + no Entra identity) | |
| SharePoint sites accessed without labels | |
| New agents in last 24h | |

### Queries Deployed as Analytics Rules
- [ ] New Agent Without Owner or Entra Identity (hourly)

### Top Risk Findings
1.
2.
3.
```

---

## Closing Questions

- What platform in your tenant had the largest count of agents with no Entra identity at all, and how many more were blueprint-only? What process would have prevented that condition?
- If you had to convert the Step 3 query into a weekly scheduled report for the security team, what additional fields would you add?

---

## Connection to Module 02

You now have a list of agents — some with owners, many without. The next module focuses on governance: configuring Entra Agent ID for proper identity, setting up the Copilot Studio approval flow, and using KQL to detect agents that bypassed governance controls entirely.

→ [Module 02 — Govern & Control](./Module-02-Govern.md)
