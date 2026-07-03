# Module 07 — Vendor & Third-Party AI Risk | Track B

**Module duration:** 90 minutes  
**Format:** Presentation + vendor evaluation exercise  
**Audience:** Security architects, procurement leads, risk managers

---

## Learning Objective

By the end of this module, participants will be able to evaluate third-party AI vendors and MCP server providers using a structured security checklist, use KQL to audit which external AI endpoints their agents already connect to, and document third-party AI risk in the format required by EU AI Act Article 25 and NIST AI RMF GOVERN-5.1.

---

## Module Agenda

| Time | Activity | Type |
|------|----------|------|
| 15 min | The third-party AI attack surface: MCP servers, plugins, model APIs, AI-as-a-service | Presentation |
| 15 min | Vendor evaluation framework: 5 domains, 20 questions | Presentation |
| 50 min | Lab: audit existing external AI connections in your tenant + score one vendor | Exercise |
| 10 min | Remediation roadmap for vendor gaps | Discussion |

---

## Core Content

1. **Third-party AI risk is supply chain risk:** Every MCP server your agent connects to, every external model API it calls, and every AI plugin it loads is a potential supply chain entry point. The attack surface is wider than traditional software supply chain because: (a) AI model weights can be backdoored before delivery; (b) MCP server tools can be updated remotely without your knowledge; (c) model responses can be manipulated if the provider is compromised. MITRE ATLAS `AML.T0051` (prompt injection via third-party content) and `AML.T0040` (model extraction) are both supply chain vectors.

2. **The MCP server risk profile:** When an agent connects to an MCP server, it declares tools it can invoke at runtime. Those tools execute in the context of the agent's identity — with the agent's permissions. A malicious or compromised MCP server can: inject instructions into tool responses (indirect prompt injection / XPIA), exfiltrate data through tool return values, escalate privilege through tool chain abuse. Microsoft's own documentation warns: *"When you connect to non-Microsoft MCP servers, you do so at your own risk. MCP implementations are vulnerable to attacks, cascading failures, and loss of human oversight."* The `AgentsInfo.McpServers` field in Defender Advanced Hunting is your inventory of connected external MCP servers. If it's not empty and the server isn't internal, it needs a vendor assessment.

   > **Microsoft MCP certification path:** Microsoft requires third-party MCP servers to undergo certification through the Power Platform connector certification program before being made available to all users. Only certified MCP servers appear in the Microsoft 365 admin center **Agents and Tools** section, where IT admins can allow or block them at the tenant level. Uncertified MCP servers connected directly to agents bypass this control. Reference: [Microsoft MCP server certification](https://learn.microsoft.com/microsoft-copilot-studio/mcp-server-certification).

3. **Model API risk — what you don't control:** When your agent calls an external model API (non-Microsoft), you don't control the model weights, the inference infrastructure, the logging policy, or the data retention. Key questions: Does the provider log your prompts? Does the provider use your data for training? Is the model's safety training documented? Has the model been independently red-teamed? For Microsoft environments: Azure OpenAI and Azure AI Foundry are the approved paths — external model APIs require explicit approval and security assessment.

4. **AI-as-a-service vendor categories and their risk profiles:**

   | Vendor type | Examples | Risk profile | Key concern |
   |------------|---------|-------------|------------|
   | Foundation model API | OpenAI, Anthropic, Cohere | High — data leaves tenant | Prompt logging, data retention |
   | MCP server provider | Zapier, Composio, custom | High — tool execution in agent context | Tool injection, credential exposure |
   | AI plugin provider | Copilot plugins, Teams apps | Medium — runs in M365 context | Permission scope, data access |
   | AI-enhanced SaaS | Salesforce AI, ServiceNow AI | Medium — embedded AI in existing tool | Existing vendor review + AI addendum |
   | On-prem / self-hosted | Ollama, LM Studio | Low cloud risk — endpoint risk instead | Endpoint security, no audit trail |

5. **Regulatory requirements for third-party AI:**
   - **EU AI Act Art. 25:** Importers and distributors of high-risk AI systems must verify supplier compliance documentation. For operators (organizations using AI): contractual obligations must require providers to maintain compliance.
   - **NIST AI RMF GOVERN-5.1:** Organizational policies require AI risk management of third-party entities.
   - **ISO 42001 Clause 8.6:** Externally provided AI systems and components must be controlled. Documented requirements must be communicated to external providers.

---

## Vendor Evaluation Framework — 5 Domains, 20 Questions

Use this checklist before connecting any external AI vendor to your agent environment.

### Domain A — Data Security & Privacy

| # | Question | Pass criterion |
|---|----------|----------------|
| A1 | Does the vendor log inference requests (prompts + responses)? | Log retention ≤ 30 days or opt-out available |
| A2 | Is your data used to train or fine-tune the vendor's models? | Contractual prohibition on training use |
| A3 | Does the vendor process data in your region? | Data residency matches your compliance requirements |
| A4 | What is the vendor's data breach notification SLA? | ≤ 72 hours (GDPR requirement) |

### Domain B — Model Security

| # | Question | Pass criterion |
|---|----------|----------------|
| B1 | Has the model been independently red-teamed? | Published red team report or third-party attestation |
| B2 | Does the vendor have documented safety training and alignment process? | Published model card or safety documentation |
| B3 | Can the model be fine-tuned by other customers on your data? | No cross-customer fine-tuning |
| B4 | Is the model supply chain (training data provenance) documented? | Data lineage report available |

### Domain C — Access & Identity

| # | Question | Pass criterion |
|---|----------|----------------|
| C1 | How does the vendor authenticate API calls? | API key scoped per customer, or Entra-based auth |
| C2 | Does the vendor support key rotation without service interruption? | Key rotation < 4h downtime |
| C3 | Is access logging available for all API calls? | Per-call audit log exportable to your SIEM |
| C4 | Can access be revoked instantly (kill switch)? | Token revocation < 5 minutes |

### Domain D — MCP Server Specific (if applicable)

| # | Question | Pass criterion |
|---|----------|----------------|
| D1 | Are tool definitions static or can they be updated remotely? | Static or change-controlled with notification |
| D2 | Does the MCP server execute code in your tenant or the vendor's environment? | Documented execution boundary |
| D3 | What data does the MCP server send back to the vendor on tool invocation? | Disclosed in data processing agreement |
| D4 | Is the MCP server open source or auditable? | Source available or security audit report |

### Domain E — Compliance & Governance

| # | Question | Pass criterion |
|---|----------|----------------|
| E1 | Does the vendor hold ISO 27001 or SOC 2 Type II? | Current certificate < 12 months old |
| E2 | Does the vendor have an AI-specific security policy? | Published AI security posture documentation |
| E3 | Is there a documented incident response process for AI-specific incidents? | SLA for AI model compromise notification |
| E4 | Does the vendor contractually accept liability for AI-specific risks? | AI liability clause in contract |

**Scoring:** Each "Pass" = 1 point. Score interpretation:
- 18–20: Approved for production use
- 14–17: Conditional approval — remediate gaps within 90 days
- 10–13: Limited use only — no sensitive data; remediation required before expansion
- < 10: Do not connect. Escalate to CISO.

---

## Lab Exercise

### Step 1 — Audit existing external AI connections in your tenant

Run this query to identify agents with external MCP servers already connected:

```kql
// Query 1: Agent inventory with MCP server connections (from AgentsInfo)
AgentsInfo
| where Timestamp > ago(30d)
| where not(isnull(McpServers)) and array_length(McpServers) > 0
| extend OwnersStr = tostring(Owners)
| extend OwnerDisplay = iff(OwnersStr == "" or OwnersStr == "[]", "UNASSIGNED", OwnersStr)
| extend McpServerCount = array_length(McpServers)
| project
    AgentName, Platform, OwnerDisplay, LifecycleStatus,
    McpServerCount, McpServers,
    RiskNote = "Agent has external MCP server connections — vendor assessment required"
| sort by McpServerCount desc
```

```kql
// Query 2: Live MCP tool invocations (official action type: ExecuteToolByGateway)
// Use this to monitor which MCP tools agents actually called at runtime
CloudAppEvents
| where TimeGenerated > ago(7d)
| where ActionType == "ExecuteToolByGateway"
| extend AgentName = tostring(RawEventData["AgentName"])
| extend McpServerName = tostring(RawEventData["McpServerName"])
| extend ToolName = tostring(RawEventData["ToolName"])
| extend CallerIdentity = AccountDisplayName
| summarize
    InvocationCount = count(),
    DistinctTools = dcount(ToolName),
    ToolList = make_set(ToolName),
    LastCall = max(TimeGenerated)
    by AgentName, McpServerName, CallerIdentity
| sort by InvocationCount desc
```

For each MCP server found in Query 1: check whether a vendor assessment exists in your vendor registry. Query 2 shows which tools were actually invoked — prioritize assessments for servers with highest invocation counts and broadest tool usage.

---

### Step 2 — Score one vendor using the 20-question checklist

Pick the highest-priority external AI connection from Step 1. Complete the Domain A–E checklist. Document:

```
Vendor name: ________________
Connection type: ☐ Foundation model API ☐ MCP server ☐ AI plugin ☐ AI-enhanced SaaS
Total score: ___ / 20
Approval status: ☐ Approved ☐ Conditional ☐ Limited use ☐ Do not connect
Top 3 gaps:
1.
2.
3.
Remediation owner: ________________
Target date: ________________
```

---

### Step 3 — Map vendor gaps to regulatory obligations

For each gap identified in Step 2, identify which regulatory obligation it violates:

| Gap | EU AI Act | NIST AI RMF | ISO 42001 |
|-----|-----------|-------------|-----------|
| | | | |

---

## Closing Questions

- Which of the 20 checklist items would be hardest to verify contractually for a foundation model provider? What alternative evidence would you accept?
- If a vendor fails Domain D (MCP server) but passes all other domains, what conditional approval conditions would you impose?
- An agent in your tenant has an MCP server connection that wasn't in the vendor registry. What is your incident response process?

---

## Track B Complete

You have now built the complete **AI Security Architecture** for your organization:

| Module | Domain | Deliverable |
|--------|--------|-------------|
| 01 — Discover | Visibility | Agent inventory + shadow AI baseline |
| 02 — Govern | Control | Governance model + approval flow + DLP |
| 03 — Secure Access | Identity | CA policies + OAuth audit |
| 04 — Protect Data | Data | DLP for AI + sensitivity labels |
| 05 — Detect & Respond | Detection | KQL strategy + Sentinel integration |
| 06 — Regulatory | Compliance | EU AI Act + NIST AI RMF + ISO 42001 mapping |
| 07 — Vendor Risk | Supply chain | Third-party AI assessment + MCP server audit |

The Gap Assessment Template consolidates findings across all seven domains into the prioritized remediation roadmap your CISO and board need.
