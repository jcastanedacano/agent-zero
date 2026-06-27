# Module 01 — Discover & Prioritize | Track C

**Duration:** 90 minutes  
**Tables:** `AIAgentsInfo`, `CloudAppEvents`, `OfficeActivity`, `MicrosoftPurviewInformationProtection`  
**Minimum role:** Security Reader (Defender + Sentinel)

---

## Learning Objective

At the end of this module, you will be able to configure Defender AI Agent Inventory and Purview DSPM for AI to detect active agents in an M365 E5 tenant, and write KQL queries to classify agents by management status and surface exposure gaps.

---

## Agenda

| Time | Activity | Type |
|------|----------|------|
| 15 min | Technical architecture: how Defender and Purview detect agents — tables, connectors, gaps | Explanation |
| 10 min | `AIAgentsInfo` schema walkthrough: fields, values, limitations | Explanation |
| 55 min | Lab: KQL queries for agent inventory and classification | Lab |
| 10 min | Results review + playbook section 1 documentation | Discussion |

---

## Background

### Why local agents are the hardest gap

Defender AI Agent Inventory covers Copilot Studio, Azure AI Foundry, AWS Bedrock, GCP Vertex, and 20+ agent types — but only when the relevant connector is active and endpoints are onboarded via MDE. Agents running locally (Claude Code, MCP servers, OpenClaw on endpoints) generate no cloud telemetry without an active endpoint connector. The gap isn't a policy problem — it's a telemetry problem.

### What `AIAgentsInfo` doesn't capture by default

- Agents deployed via third-party APIs without Agent 365 registration
- Local agents on endpoints without MDE onboarding
- Power Automate flows with AI steps that aren't registered as agents
- Agents created via Agent Builder (M365 Copilot) that bypass Copilot Studio registry

---

## Lab

### Setup

1. Open **Microsoft Defender XDR** → Advanced Hunting, or **Microsoft Sentinel** → Logs
2. Verify `AIAgentsInfo` returns results: run `AIAgentsInfo | take 5`
3. If the table is empty, use `CloudAppEvents` as fallback for agent activity signals

---

### Step 1 — Full agent inventory by type and management status

```kql
AIAgentsInfo
| where TimeGenerated > ago(30d)
| summarize
    LastSeen = max(TimeGenerated),
    AgentCount = dcount(AgentId)
    by AgentType, Platform, ManagementStatus, AgentName
| extend RiskLevel = case(
    ManagementStatus == "Unmanaged", "High",
    ManagementStatus == "PartiallyManaged", "Medium",
    "Low"
)
| sort by RiskLevel asc, LastSeen desc
| project AgentName, AgentType, Platform, ManagementStatus, RiskLevel, AgentCount, LastSeen
```

**Expected output:** Table of agents grouped by type and platform, classified by management status.

**Document in your playbook:** How many agents appear as `Unmanaged`? What platforms have the highest count?

---

### Step 2 — Agents without a technical owner

```kql
AIAgentsInfo
| where TimeGenerated > ago(30d)
| where ManagementStatus == "Unmanaged"
    or isempty(TechnicalOwner)
| distinct AgentId, AgentName, AgentType, Platform, CreatedTime, TechnicalOwner
| extend DaysSinceCreation = datetime_diff('day', now(), CreatedTime)
| sort by DaysSinceCreation desc
```

**Expected output:** List of identity orphans — agents operating with no assigned owner.

**Note:** `TechnicalOwner` is only populated if the agent was registered through Agent 365. Agents created via Agent Builder or direct API calls will appear with empty owner fields.

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

**Expected output:** Sites accessed by agents that have no sensitivity label — these are your oversharing candidates.

**Critical note:** Remediate oversharing in SharePoint **before** enabling retrieval on any agent. Every ACL error in the corpus is inherited by the agent and amplified to all users interacting with it.

---

### Step 4 — New agent registrations in the last 24 hours

```kql
AIAgentsInfo
| where TimeGenerated > ago(1d)
| where CreatedTime > ago(1d)
| project
    AgentId,
    AgentName,
    AgentType,
    Platform,
    TechnicalOwner,
    ManagementStatus,
    CreatedTime
| extend AlertDetail = strcat(
    "New agent registered: ", AgentName,
    " | Type: ", AgentType,
    " | Owner: ", iff(isempty(TechnicalOwner), "UNASSIGNED", TechnicalOwner)
)
| sort by CreatedTime desc
```

**Expected output:** Agents registered in the last 24 hours. This is your candidate for a Sentinel analytics rule with daily frequency.

---

### Step 5 — Convert Step 4 to a Sentinel Analytics Rule

1. In Microsoft Sentinel → **Analytics** → **Create** → **Scheduled query rule**
2. Name: `New Unmanaged Agent Registered`
3. Paste the query from Step 4; add filter: `| where ManagementStatus == "Unmanaged" or isempty(TechnicalOwner)`
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
| Unmanaged agents | |
| Agents without technical owner | |
| SharePoint sites accessed without labels | |
| New agents in last 24h | |

### Queries Deployed as Analytics Rules
- [ ] New Unmanaged Agent Registered (hourly)

### Top Risk Findings
1.
2.
3.
```

---

## Closing Questions

- What type of agent in your tenant had the largest gap between cloud inventory and expected count? What explains the difference?
- If you had to convert the Step 3 query into a weekly scheduled report for the security team, what additional fields would you add?

---

## Connection to Module 02

You now have a list of agents — some with owners, many without. The next module focuses on governance: configuring Entra Agent ID for proper identity, setting up the Copilot Studio approval flow, and using KQL to detect agents that bypassed governance controls entirely.

→ [Module 02 — Govern & Control](./Module-02-Govern.md)
