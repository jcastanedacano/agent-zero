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

## Core content (points the facilitator must cover)

1. **Prompt injection over an unlabeled corpus:** An attacker with write access to SharePoint can insert malicious instructions into documents the agent indexes and trusts. The agent does not validate the source of an instruction — it executes it as if it came from a legitimate user. This vector generates no alert in standard user activity logs, which is why P04 queries look at the access pattern rather than the content.

2. **The oversharing multiplier effect:** An ACL error that exposes a site to all users is a manageable risk for humans — someone has to actively search for it. For an agent with retrieval enabled, that same error is amplified to every user who interacts with the agent: exposure becomes passive and automatic. The agent does not discriminate between sensitive and non-sensitive content; it indexes everything it can read.

3. **Applicable Microsoft controls:** Purview DLP configured over "AI interactions" detects sensitive data in prompts and responses — not only in documents and email. Sensitivity labels applied to SharePoint sites constrain what the agent can index. SharePoint Advanced Management audits and remediates oversharing at site and site-collection level. Insider Risk Management detects exfiltration patterns by volume and data type.

4. **Remediation order as an architectural control:** Enabling retrieval before applying labels and remediating ACLs creates an active exposure window that can last weeks. The correct order is: (1) classify and label every candidate site, (2) audit and remediate ACL errors, (3) enable agent retrieval. Inverting this order is the most common error in agent deployments that touch SharePoint.

5. **Memory/session poisoning vs. corpus poisoning:** These are two distinct vectors. Corpus poisoning lives in SharePoint documents the agent retrieves, and it persists until the document is removed. Memory/session poisoning injects malicious instructions into the agent's persistent memory, which affects every future interaction for every user, and it survives removal of the original document. The detection surfaces differ: corpus poisoning is visible in file access logs, memory poisoning is not.

6. **Model supply chain vs. poisoned corpus:** Souly et al. document that roughly 250 malicious training documents are enough to backdoor models up to 13B parameters, with persistence through safety training, and critically that the number is near-constant rather than proportional to model size ([arXiv:2510.07192](https://arxiv.org/abs/2510.07192)). This is not detectable with KQL: it requires provider evaluation and post-deployment behavioral drift monitoring (P05-Q6). Corpus poisoning, by contrast, is detectable in your own telemetry.

7. **Multi-agent trust boundaries:** When a compromised agent invokes another agent, it pivots into a second blast radius with that agent's own permissions. The correct architectural design treats every agent-to-agent call as untrusted: verify explicit user authorization and limit permission inheritance between agents. Reference: Anthropic, Zero Trust for AI Agents.

8. **Membership inference — privacy without visible exfiltration:** An attacker can infer whether a specific PII record was in a model's fine-tuning set by systematically querying it and analyzing response patterns, without ever extracting the data directly. The result is a privacy violation that DLP and standard Purview audit cannot see. Controls: do not fine-tune with PII without differential anonymization, restrict who can query models fine-tuned on sensitive data via Foundry RBAC, and monitor inference volume per identity (P03-Q7). OWASP Agentic AG07.

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
