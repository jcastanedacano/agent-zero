# Module 05 — Detect & Respond | Track C

**Duration:** 90 minutes  
**Tables:** `CloudAppEvents`, `MicrosoftPurviewInformationProtection`, `SecurityIncident`, `AuditLogs`  
**Portals:** Microsoft Sentinel, Logic Apps, Defender XDR  
**Minimum role:** Sentinel Contributor + Logic Apps Contributor

---

## Learning Objective

At the end of this module, you will be able to create Sentinel analytics rules for jailbreak detection and agent behavioral anomalies, build a Logic App playbook that enforces token revocation on alert, and complete the agentic incident response playbook with a trigger-to-resolution flow.

---

## Agenda

| Time | Activity | Type |
|------|----------|------|
| 15 min | AISOC architecture: Sentinel as agentic defense platform — tables, MCP server, Security Copilot | Explanation |
| 10 min | Structural false negatives: detection without enforcement is not a control | Explanation |
| 55 min | Lab: Analytics rules + Logic App enforcement + playbook consolidation | Lab |
| 10 min | Final playbook review and peer discussion | Discussion |

---

## Core Content

1. **Jailbreak attempts as an active incident vector:** A successful jailbreak converts the agent into an executor of malicious instructions with legitimate system access. The signal is in prompt patterns in `CloudAppEvents`, not network behavior — which makes perimeter controls insufficient.

2. **Structural false negatives from human calibration:** Detection rules calibrated for human behavior generate false negatives with agents. An agent making 5,000 calls in an hour may be operating normally. Without a per-agent baseline using `percentile()` or `avg()` over long time windows, any fixed threshold generates either false positives or false negatives.

3. **Applicable Microsoft controls:** Defender XDR integrates agentic behavioral signals with identity context. Microsoft Sentinel with the native MCP server allows querying agent status from within the investigation context. Security Copilot accelerates triage of complex incidents. Purview Audit provides the forensic chain of custody with immutability. Agent 365 correlates incident events with the agent ownership registry.

4. **Automated enforcement as an architectural requirement:** Detection without response automation has MTTR limited by human reaction time. For agents acting in seconds, the target is: automatic detection → automatic containment (Logic App revokes token via Graph API) → human review. A "detection without enforcement" posture is not a control — it is an incident log.

---

## Background

### Detection vs. enforcement — the 37% problem

A Sentinel analytics rule that fires an alert is **detection**. The alert sitting in the queue without automated response is not enforcement. The gap between detection and enforcement is where most agentic incidents expand: the jailbreak is detected at T+0, but the token isn't revoked until T+4h when a human reviews the queue.

The Logic App playbook is the enforcement layer. Without it, Sentinel is a detection-only platform. With it, detection becomes a control.

### Sentinel as both target and platform

Microsoft Sentinel is simultaneously:
- The SIEM that detects attacks **against** agentic systems
- The platform where **security agents** (AISOC) operate to investigate and respond
- A potential attack surface if agents operating within Sentinel are compromised

This dual role is why MCP server native integration in Sentinel matters: it allows security agents to query Sentinel data directly, but also means that a compromised security agent has direct access to your detection logic and alert data.

### Structural false negatives in practice

If the same alert fires for the same agent 3+ times with no remediation action in the incident record, that is a **structural false negative** — your detection is working but your enforcement is not. Query `SecurityIncident` to find these patterns (Step 5 in this module).

---

## Lab

### Step 1 — Create a jailbreak detection analytics rule

1. In **Microsoft Sentinel** → **Analytics** → **Create** → **Scheduled query rule**
2. **General tab:**
   - Name: `Agentic AI — Jailbreak Attempt Detected`
   - Description: Detects prompt patterns consistent with system instruction override attempts
   - Severity: **High**
   - Tactics: Execution, Initial Access
3. **Set rule logic tab — paste this query:**

```kql
CloudAppEvents
| where TimeGenerated > ago(1h)
| where Application in ("Microsoft Copilot", "Copilot Studio", "Azure AI Foundry")
    and ActionType == "AgentInteraction"
| extend PromptText = tostring(RawEventData["UserPrompt"])
| extend AgentId = tostring(RawEventData["AgentId"])
| extend JailbreakScore = toint(
    (PromptText has "ignore previous instructions") * 3 +
    (PromptText has "disregard your system prompt") * 3 +
    (PromptText has "you are now a") * 2 +
    (PromptText has "act as if you have no") * 2 +
    (PromptText has "forget all previous") * 2 +
    (PromptText has "override:") * 1
)
| where JailbreakScore >= 2
| project
    TimeGenerated,
    AccountDisplayName,
    AgentId,
    JailbreakScore,
    PromptPreview = substring(PromptText, 0, 300),
    IPAddress,
    Application
```

4. **Query scheduling:** Run every **5 minutes** | Lookup last **1 hour**
5. **Alert threshold:** Generate alert when number of results is **greater than 0**
6. **Entity mapping:**
   - Account → `AccountDisplayName`
   - IP → `IPAddress`
7. Save and enable

---

### Step 2 — Create a behavioral anomaly analytics rule

1. **Create** → **Scheduled query rule**
2. Name: `Agentic AI — Volume Spike Anomaly`
3. Severity: **Medium**
4. **Query:**

```kql
let Baseline = CloudAppEvents
    | where TimeGenerated between (ago(8d) .. ago(1d))
    | where ActionType == "AgentInteraction"
    | extend AgentId = tostring(RawEventData["AgentId"])
    | summarize HourlyCount = count() by AgentId, bin(TimeGenerated, 1h)
    | summarize BaselineAvg = avg(HourlyCount), BaselineStdDev = stdev(HourlyCount) by AgentId;
CloudAppEvents
| where TimeGenerated > ago(1h)
| where ActionType == "AgentInteraction"
| extend AgentId = tostring(RawEventData["AgentId"])
| summarize CurrentCount = count() by AgentId, bin(TimeGenerated, 1h)
| join kind=inner Baseline on AgentId
| extend Deviations = (CurrentCount - BaselineAvg) / max_of(BaselineStdDev, 1.0)
| where Deviations > 3
| project AgentId, CurrentCount, BaselineAvg = round(BaselineAvg, 1), Deviations = round(Deviations, 1)
```

5. **Query scheduling:** Every **15 minutes** | Lookup last **1 hour**
6. **Entity mapping:** Custom entity → `AgentId`
7. Save and enable

---

### Step 3 — Build the enforcement Logic App

1. In **Azure Portal** → **Logic Apps** → **Create** → Consumption plan
   - Name: `playbook-revoke-agent-token`
   - Resource group: same as your Sentinel workspace
2. In the Logic App designer, start with trigger: **Microsoft Sentinel — When a response to a Microsoft Sentinel alert is triggered**
3. Add action: **HTTP** (to call Graph API for token revocation)
   - Method: POST
   - URI: `https://graph.microsoft.com/v1.0/servicePrincipals/<agentObjectId>/revokeSignInSessions`
   - Authentication: Managed Identity (assign `Application.ReadWrite.All` to the Logic App's managed identity)
4. Add action: **Microsoft Sentinel — Add comment to incident**
   - Comment: `Automated response: agent token revoked at @{utcNow()} by playbook-revoke-agent-token`
5. Add action: **Office 365 Outlook — Send an email**
   - To: agent technical owner (from `Owners` field in `AgentsInfo` or Agent 365 Registry)
   - Subject: `[ALERT] Agent token revoked — review required`
   - Body: include incident URL and AgentId
6. Save the Logic App

**Link the playbook to Sentinel:**
- In Sentinel → **Automation** → **Automation rules** → **Create**
- Trigger: When alert is created
- Condition: Alert name contains "Jailbreak"
- Action: Run playbook → `playbook-revoke-agent-token`

---

### Step 4 — Detect sensitive document access outside business hours

```kql
MicrosoftPurviewInformationProtection
| where TimeGenerated > ago(1d)
| where Activity in ("FileAccessed", "FileDownloaded")
    and LabelName has_any ("Highly Confidential", "Restricted")
| extend HourOfDay = datetime_part("Hour", TimeGenerated)
| extend IsOffHours = HourOfDay < 7 or HourOfDay > 20
| extend IsWeekend = dayofweek(TimeGenerated) in (0, 6)
| extend IsAgentAccess = UserAgent has_any ("agent", "copilot", "assistant", "bot")
| where (IsOffHours or IsWeekend) and IsAgentAccess
| project
    TimeGenerated,
    UserId,
    ObjectId,
    LabelName,
    Activity,
    HourOfDay,
    IsWeekend,
    SiteUrl
| sort by TimeGenerated desc
```

Create this as a third analytics rule: `Agentic AI — Sensitive Data Access Off-Hours`

---

### Step 5 — KQL: Structural false negative audit

```kql
SecurityIncident
| where TimeGenerated > ago(30d)
| where Title has_any ("agent", "copilot", "AI interaction", "jailbreak")
| summarize
    IncidentCount = count(),
    FirstIncident = min(TimeGenerated),
    LastIncident = max(TimeGenerated),
    StatusHistory = make_set(Status)
    by Title, IncidentProviderName
| extend NeverClosed = not(StatusHistory has "Closed")
| extend IsRepeat = IncidentCount > 3
| where NeverClosed or IsRepeat
| project
    Title,
    IncidentCount,
    FirstIncident,
    LastIncident,
    StatusHistory,
    RiskNote = case(
        NeverClosed and IsRepeat, "Recurring — never closed. No enforcement action confirmed.",
        NeverClosed, "Never closed — verify enforcement is in place",
        "High repeat rate — review enforcement effectiveness"
    )
| sort by IncidentCount desc
```

**Expected output:** Alerts that fire repeatedly with no resolution — your structural false negative inventory.

---

### Step 6 — Consolidate the incident response playbook

Using the [Playbook Template](./Templates/Incident-Response-Playbook-Template.md), complete the final section:

```markdown
## Section 5: Detection and Response

### Analytics Rules Deployed
| Rule Name | Severity | Frequency | Table | Status |
|-----------|----------|-----------|-------|--------|
| Agentic AI — Jailbreak Attempt Detected | High | 5 min | CloudAppEvents | Enabled |
| Agentic AI — Volume Spike Anomaly | Medium | 15 min | CloudAppEvents | Enabled |
| Agentic AI — Sensitive Data Access Off-Hours | High | 15 min | MicrosoftPurviewInformationProtection | Enabled |

### Automation Rule
- Trigger: Alert name contains "Jailbreak"
- Action: Run playbook-revoke-agent-token
- Status: Enabled

### Enforcement Flow
Jailbreak alert fires (T+0)
    → Automation rule triggers Logic App (T+0 to T+2 min)
    → Token revoked via Graph API
    → Incident comment added in Sentinel
    → Email notification sent to agent technical owner
    → SOC analyst reviews incident in queue

### Structural False Negatives Found
| Alert | Fire Count | Never Closed | Action Required |
|-------|-----------|--------------|-----------------|
| | | | |
```

---

## Closing Questions

- In the enforcement playbook, where exactly is the boundary between **detection** (Sentinel rule fires) and **enforcement** (action taken)? What component closes that gap?
- If Security Copilot were configured as an investigative agent operating within this Sentinel workspace, what access would it need, and what risk does that create given the content of Module 03?

---

## Connection to Module 06

The detection rules you built in this module are exactly the rules you will test in Module 06. The enforcement playbook you built here is the containment mechanism you will verify still fires after an actual attack. Module 06 closes the loop — it surfaces the detection gaps that this module's rules don't cover.

→ [Module 06 — Red Team Perspective](./Module-06-RedTeamPerspective.md)
