# Module 04 — Protect Data | Track C

**Duration:** 90 minutes  
**Tables:** `CloudAppEvents`, `MicrosoftPurviewInformationProtection`, `OfficeActivity`  
**Portals:** Purview compliance portal, SharePoint admin center  
**Minimum role:** Compliance Administrator (for DLP policy creation)

---

## Learning Objective

At the end of this module, you will be able to configure a Purview DLP policy for AI interactions, write KQL to detect data exfiltration via agent connectors, and validate sensitivity label coverage on SharePoint sites used as agent knowledge sources.

---

## Agenda

| Time | Activity | Type |
|------|----------|------|
| 15 min | Prompt injection mechanics: how agents are manipulated and which tables capture it | Explanation |
| 10 min | API exfiltration as a blind channel: why standard network controls miss it | Explanation |
| 55 min | Lab: Purview DLP for AI + exfiltration KQL + label coverage audit | Lab |
| 10 min | Results review + playbook section 4 documentation | Discussion |

---

## Background

### Why connectors are the exfiltration blind spot

Agent connectors in Power Platform use legitimate HTTPS — they are indistinguishable from normal application traffic at the network layer. Without a DLP policy specifically targeting the agent's output channel, data sent by an agent to an external endpoint generates no alert in any standard network security control. The exfiltration is silent.

### The oversharing timeline

```
SharePoint site created (no sensitivity labels)
        ↓
Agent configured to use site as knowledge source
        ↓
Agent indexes all documents regardless of content sensitivity
        ↓
Every user who prompts the agent can retrieve sensitive content
        ↓
DLP alert fires — but the data has already been in the agent's context for weeks
```

**The correct order:** apply sensitivity labels and remediate ACL errors **before** activating any agent retrieval on that SharePoint site. After activation, you are remediating a live exposure.

### What `MicrosoftPurviewInformationProtection` captures

This table is the most complete forensic source for agentic data incidents. It captures:
- Label applied / changed / removed events
- DLP policy match events (including AI interaction workload)
- File access events with label context
- eDiscovery and audit hold events

Retention in the demo tenant: 90 days by default. In production, plan for 1-year minimum for regulated industries.

---

## Lab

### Step 1 — Create a Purview DLP policy for AI interactions

1. In **Microsoft Purview** → **Data loss prevention** → **Policies** → **Create policy**
2. Select template: **Custom** → **Custom policy** → Next
3. Name: `Agentic AI — Sensitive Data in AI Interactions`
4. **Locations:** Select **Microsoft 365 Copilot and other AI apps** (AI interactions workload)
5. **Define policy settings:** Create advanced DLP rule
   - Rule name: `Credit card in agent prompt or response`
   - **Conditions:** Content contains → Sensitive info types → **Credit Card Number**
   - **Actions:** Restrict access → **Block** + **Notify user** + **Generate alert**
   - Alert severity: High
6. Set policy mode: **Test mode with policy tips** (for demo tenant safety)
7. Save and enable

**Verify:** In **DLP Alerts** (Purview → Data loss prevention → Alerts), confirm the policy appears as active.

---

### Step 2 — Audit sensitivity label coverage on agent knowledge sources

1. In **SharePoint admin center** → **Active sites**
2. Filter for sites used as agent knowledge sources (check your Agent 365 registry for linked sites)
3. For each site, check the **Sensitivity** column — sites showing "None" are unlabeled knowledge sources

**Apply a label to a demo site:**

```powershell
# PowerShell — SharePoint Online Management Shell
Connect-SPOService -Url https://<tenant>-admin.sharepoint.com
Set-SPOSite -Identity https://<tenant>.sharepoint.com/sites/demo-knowledge `
    -SensitivityLabel "<label-id>"
```

Get the label ID from Purview → Information protection → Labels → select label → copy GUID.

---

### Step 3 — KQL: DLP policy matches in AI interactions

```kql
MicrosoftPurviewInformationProtection
| where TimeGenerated > ago(7d)
| where Activity == "DLPRuleMatch"
    and Workload == "AIInteractions"
| extend SensitiveTypes = tostring(SensitiveInfoTypeData)
| extend PolicyName = tostring(PolicyDetails[0].PolicyName)
| extend MatchedRule = tostring(PolicyDetails[0].Rules[0].RuleName)
| summarize
    MatchCount = count(),
    LastMatch = max(TimeGenerated),
    AffectedUsers = dcount(UserId)
    by SensitiveTypes, PolicyName, MatchedRule
| sort by MatchCount desc
```

**Expected output:** Sensitive information type matches in agent prompts and responses, grouped by type and rule.

---

### Step 4 — KQL: Agents accessing unlabeled documents

```kql
MicrosoftPurviewInformationProtection
| where TimeGenerated > ago(7d)
| where Activity in ("FileAccessed", "FileDownloaded")
| where isempty(LabelId) or LabelName == ""
| extend IsAgentAccess = UserAgent has_any ("agent", "copilot", "assistant", "bot", "power-automate")
| where IsAgentAccess == true
| summarize
    UnlabeledAccesses = count(),
    DocumentList = make_set(ObjectId, 10),
    LastAccess = max(TimeGenerated)
    by UserId, SiteUrl
| sort by UnlabeledAccesses desc
```

**Expected output:** Agent access events on documents with no sensitivity label — your oversharing inventory.

---

### Step 5 — KQL: External connector data egress

```kql
CloudAppEvents
| where TimeGenerated > ago(7d)
| where Application == "Microsoft Power Platform"
    and ActionType == "ConnectorActionExecuted"
| extend ConnectorName = tostring(RawEventData["ConnectorName"])
| extend TargetEndpoint = tostring(RawEventData["TargetUrl"])
| extend PayloadSize = toint(RawEventData["ResponseSizeBytes"])
| where isnotempty(TargetEndpoint)
    and TargetEndpoint !has "microsoft.com"
    and TargetEndpoint !has "azure.com"
| summarize
    EgressEvents = count(),
    TotalPayloadBytes = sum(PayloadSize),
    EndpointList = make_set(TargetEndpoint, 10),
    LastEgress = max(TimeGenerated)
    by ConnectorName, AccountDisplayName
| sort by TotalPayloadBytes desc
| extend TotalPayloadMB = round(toreal(TotalPayloadBytes) / 1048576, 2)
| project ConnectorName, AccountDisplayName, EgressEvents, TotalPayloadMB, EndpointList, LastEgress
```

**Expected output:** Agents sending data to external endpoints — sorted by payload volume. Any entry here with an unrecognized `TargetEndpoint` is a candidate for incident investigation.

---

### Step 6 — KQL: Prompt injection pattern detection

```kql
CloudAppEvents
| where TimeGenerated > ago(7d)
| where Application in ("Microsoft Copilot", "Copilot Studio")
    and ActionType == "AgentInteraction"
| extend PromptText = tostring(RawEventData["UserPrompt"])
| extend HasInjectionPattern = PromptText has_any (
    "ignore previous instructions",
    "disregard your system prompt",
    "you are now",
    "act as if",
    "forget all previous",
    "new instructions:",
    "override:"
)
| where HasInjectionPattern == true
| summarize
    InjectionAttempts = count(),
    FirstAttempt = min(TimeGenerated),
    LastAttempt = max(TimeGenerated),
    PromptSamples = make_set(substring(PromptText, 0, 200), 3)
    by AccountDisplayName, IPAddress
| sort by InjectionAttempts desc
```

**Expected output:** Users or source IPs with repeated prompt injection patterns — these are investigation candidates, not automatic blocks (a single pattern match may be legitimate).

---

## Playbook Section 4 — Document Your Findings

```markdown
## Section 4: Data Protection Configuration

### DLP Policy Deployed
- Policy name: Agentic AI — Sensitive Data in AI Interactions
- Workload: AI interactions
- Rule: Credit card in agent prompt or response
- Action: Block + notify + alert
- Status: Test mode / Enforced

### SharePoint Label Coverage Audit
| Site URL | Used As Agent Knowledge Source | Sensitivity Label | Gap |
|----------|-------------------------------|-------------------|-----|
| | | | |

### Exfiltration Detection KQL Queries (add to Sentinel)
- [ ] DLP matches in AI interactions (daily)
- [ ] Agents accessing unlabeled documents (weekly)
- [ ] External connector egress by volume (daily)
- [ ] Prompt injection pattern detection (hourly)

### Critical Finding
Remediation order: sensitivity labels and ACL review MUST be completed before
activating agent retrieval on any SharePoint site. Post-activation remediation
addresses a live exposure — not a preventive control.

### Top Exfiltration Risks Found
1.
2.
3.
```

---

## Closing Questions

- Which table — `MicrosoftPurviewInformationProtection` or `CloudAppEvents` — gives more complete forensic context for reconstructing what data an agent accessed during a specific time window? What fields from each table would you join?
- If an agent exfiltrated data via an external connector 10 days ago and the DLP policy wasn't active, what audit log sources could you use to reconstruct the incident? What retention limits apply in your tenant?

---

## Connection to Module 05

Preventive controls reduce risk but don't eliminate it. Agents will still attempt jailbreaks, exhibit anomalous behavior, and produce false negatives in detection-only controls. The final module operationalizes detection and response: Sentinel analytics rules, Logic App enforcement, and building the complete incident response playbook.

→ [Module 05 — Detect & Respond](./Module-05-DetectRespond.md)
