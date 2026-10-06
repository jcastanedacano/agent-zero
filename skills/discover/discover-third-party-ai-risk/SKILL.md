---
name: discover-third-party-ai-risk
description: Evaluate and inventory third-party AI agents — ISV extensions, MCP servers, Copilot plugins, and marketplace agents — that operate in the tenant without the same governance controls applied to first-party agents.
pillar: 01-Discover
subdomain: third-party-inventory
tags:
  - third-party
  - supply-chain
  - copilot-plugins
  - mcp-servers
  - shadow-ai
frameworks:
  mitre_atlas:
    - AML.T0010      # AI Supply Chain Compromise
    - AML.T0010.005  # AI Supply Chain Compromise: AI Agent Tool (MCP servers, plugins)
    - AML.T0109      # AI Supply Chain Rug Pull (trusted tool turns malicious via update)
    - AML.T0016      # Obtain Capabilities
  d3fend:
    - D3-SFA    # Software Feature Analysis
    - D3-AC     # Application Configuration
  nist_ai_rmf:
    - GOVERN-1.2  # Organizational risk tolerance — third-party
    - MAP-3.5     # AI supply chain risks
  nist_csf_2:
    - ID.SC-2    # Suppliers and third-party partners assessed
    - ID.RA-6    # Risk responses are chosen and communicated
license_requirements:
  - Microsoft 365 E3 or E5 (Copilot admin center)
  - Microsoft Defender XDR (CloudAppEvents)
  - Entra ID P1 or P2 (App registrations audit)
role_requirements:
  - Global Reader
  - Security Reader
  - Compliance Administrator
---

## Objective

Identify and evaluate every active third-party AI agent in the tenant — ISV Copilot plugins, external MCP servers, Agent 365 extensions, and third-party Power Platform agents — and assign each a risk level before it accesses organizational data.

## Why it matters

First-party agents (built by the internal team) go through Entra Agent ID and Copilot Studio governance. Third-party agents are typically installed from the marketplace or connected directly, bypassing that same review.

The reference framework is the OWASP Top 10 for Agentic Applications (2026), ASI04 — Agentic Supply Chain Vulnerabilities, and MITRE ATLAS AML.T0010 (ML Supply Chain Compromise).

## Workflow

### Step 1 — Inventory third-party Copilot plugins and extensions

```powershell
# PowerShell — Microsoft Graph API
# Lists every active Copilot plugin in the tenant
$graphUri = "https://graph.microsoft.com/v1.0/admin/microsoft365Apps/installations"
$response = Invoke-MgGraphRequest -Uri $graphUri -Method GET
$response.value | Where-Object { $_.publisher -ne "Microsoft" } |
    Select-Object displayName, publisher, appId, installationStatus |
    Sort-Object publisher
```

### Step 2 — Audit third-party application permissions in Entra

> Run on a Sentinel workspace (Oct 2026): the earlier version read `modifiedProperties[0]`, which holds `IsAdminConsent`, so no scope could match. The scopes are in the property `ConsentAction.Permissions`. The query lists every high-privilege consent, not only third-party ones: review the publisher of each app.

```kql
// Entra consents with high-privilege delegated scopes
AuditLogs
| where TimeGenerated > ago(30d)
| where OperationName == "Consent to application"
| extend AppName = tostring(TargetResources[0].displayName)
| extend ConsentedBy = tostring(InitiatedBy.user.userPrincipalName)
| mv-apply MP = TargetResources[0].modifiedProperties on (
    where tostring(MP.displayName) == "ConsentAction.Permissions"
    | summarize ScopesGranted = take_any(tostring(MP.newValue)))
| extend IsHighPrivilege = ScopesGranted has_any (
    "Files.ReadWrite.All",
    "Mail.ReadWrite",
    "Sites.ReadWrite.All",
    "Directory.ReadWrite.All",
    "User.ReadWrite.All",
    "Calendars.ReadWrite"
)
| where IsHighPrivilege == true
| project TimeGenerated, AppName, ScopesGranted, ConsentedBy, IsHighPrivilege
| sort by TimeGenerated desc
```

Application permissions are granted by an app role assignment, which this query does not read: the app role branch of P02 Q4 lists those.

### Step 3 — Detect external MCP servers connected to agents

> **Not verified (Oct 2026).** The earlier version read `ConnectorActionExecuted`, `ExternalToolInvoked` and `MCPServerConnected` from `CloudAppEvents`; none of them is documented, and the validation tenant has no agent events there. Microsoft Learn documents `ExecuteToolByMCPServer` (alongside `InvokeAgent`, `InferenceCall`, `ExecuteToolBySDK` and `ExecuteToolByGateway`) for Agent 365 observability, but the tool endpoint is not surfaced in Advanced Hunting. The inventory of declared MCP servers does exist: `AgentsInfo.McpServers` is populated for local agents (1 agent on the validation tenant). Start from that, and use the ActionType below only once your tenant emits it.

```kql
// 1. Declared MCP servers per agent (AgentsInfo, Advanced Hunting)
AgentsInfo
| where Timestamp > ago(7d)
| summarize arg_max(Timestamp, *) by AgentId
| where isnotempty(McpServers) and tostring(McpServers) != "[]"
| project AgentId, Name, Platform, McpServers
| sort by Name asc

// 2. MCP tool executions (CloudAppEvents, once the ActionType is emitted in the tenant)
CloudAppEvents
| where Timestamp > ago(7d)
| where ActionType == "ExecuteToolByMCPServer"
| summarize InvocationCount = count(), LastSeen = max(Timestamp) by AccountDisplayName, Application
| sort by InvocationCount desc
```

### Step 4 — Assess the risk of each third-party agent

For each identified agent, complete the following table:

| Field | Key questions |
|-------|----------------|
| **Publisher verification** | Is the publisher in the official Microsoft marketplace? Is it certified? |
| **Data access scope** | What Graph API permissions does it hold? Does it access mail, calendar, SharePoint? |
| **Data residency** | Are prompts and responses processed outside the Microsoft tenant? |
| **Audit trail** | Do the third-party agent's actions appear in Purview audit? |
| **Update mechanism** | Is the agent code updated automatically without re-approval? |
| **Supply chain** | Does the agent depend on third-party models (not Azure OpenAI)? |

### Step 5 — Apply controls by risk level

**High risk** (sensitive data access + unverified publisher):
- Block via Power Platform DLP or a CA policy on the App ID
- Require a security review before re-activation

**Medium risk** (business data access + verified publisher):
- Restrict scopes to Read-only where possible
- Configure a Sentinel alert on anomalous access volume
- Review quarterly

**Low risk** (limited access + Microsoft or certified publisher):
- Document in the inventory
- Include in the annual app registration review cycle

## Verification

- [ ] Third-party plugin and extension inventory completed with publisher, scopes, and installation date
- [ ] Every third-party agent with access to highly sensitive data has an active CA policy or DLP
- [ ] P03 Query Q3 executed and high-privilege permissions reviewed
- [ ] External MCP servers identified and evaluated against the allowlist policy
- [ ] Third-party records added to the Gap Assessment Template (Domain 1 — Discover)

## Implementation notes

- Plugins installed from the Microsoft 365 App Store go through Microsoft's certification process, but they are not immune to post-certification compromise — treat certification as a starting point, not a guarantee
- External MCP servers are the highest-risk vector: a compromised MCP server can inject malicious instructions into any agent that invokes it, with the agent's own permissions
- Power Platform DLP can block external connectors at the environment level, which is the most effective control for unauthorized MCP servers.
- The `CloudAppEvents` agent ActionTypes (`InvokeAgent`, `ExecuteToolByMCPServer`, ...) depend on the Defender and Agent 365 configuration and were absent on the validation tenant — validate availability first
