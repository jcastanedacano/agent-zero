# KQL Library

Production-ready queries for detecting agentic AI security risks in Microsoft Sentinel and Defender Advanced Hunting.

Each file maps to one of the five security domains. Queries are designed to run against standard M365 E5 tables — no custom ingestion required unless noted.

---

## Query Index

| File | Domain | Tables | Description |
|------|--------|--------|-------------|
| [P01-Agent-Discovery.kql](./P01-Agent-Discovery.kql) | Discover & Prioritize | `AgentsInfo`, `CloudAppEvents`, `OfficeActivity` | Inventory agents by type and management status |
| [P02-Governance-Gaps.kql](./P02-Governance-Gaps.kql) | Govern & Control | `AgentsInfo`, `AuditLogs` | Detect agents without Entra Agent ID or technical owner |
| [P03-Access-Anomalies.kql](./P03-Access-Anomalies.kql) | Secure Access | `CloudAppEvents`, `EntraIdSpnSignInEvents`, `AuditLogs`, `AgentsInfo`, `BehaviorInfo` | Identify over-permissioned agents, OAuth consent drift, real-time protection blocks, and Agent ID object changes |
| [P04-Exfiltration-Detection.kql](./P04-Exfiltration-Detection.kql) | Protect Data | `CloudAppEvents`, `MicrosoftPurviewInformationProtection` | Detect data exfiltration via agent prompts and connectors |
| [P05-Jailbreak-Detection.kql](./P05-Jailbreak-Detection.kql) | Detect & Respond | `LLMActivity`, `CloudAppEvents`, `MicrosoftPurviewInformationProtection`, `AuditLogs` | Flag jailbreak attempts and behavioral anomalies |

---

## Usage

### Microsoft Sentinel
Paste queries directly into **Logs** or use as the basis for **Analytics Rules**.

### Defender Advanced Hunting
Most queries run unmodified in the Advanced Hunting interface. Tables exclusive to Sentinel (e.g., `MicrosoftPurviewInformationProtection`) require the Sentinel workspace.

---

## Required Permissions

| Minimum Role | Covers |
|---|---|
| Security Reader | Read-only query execution in Defender and Sentinel |
| Security Admin | Required to act on results (revoke tokens, modify policies) |
| Sentinel Reader | Read access to Sentinel workspace logs |
| Sentinel Contributor | Create and modify Analytics Rules and Playbooks |

---

## Adapting for Production

These queries use conservative time windows (`ago(7d)`, `ago(30d)`) suitable for demo tenants. In production:

- Extend retention windows based on your workspace configuration
- Replace hardcoded thresholds (e.g., `CallCount > 100`) with dynamic baselines using `percentile()` or `avg()` over longer periods
- Add `| where TenantId == "<your_tenant_id>"` when running in multi-tenant workspaces
- Schedule as Analytics Rules with appropriate alert frequency and suppression windows

## Schema validation status

KQL Library queries are validated against a live Microsoft 365 tenant using the Microsoft Graph Security `runHuntingQuery` API, with the date of the last validation listed per file. P04 queries Sentinel tables and has no validation date.

| File | Tables | Last Validated | Notes |
|------|--------|---------------|-------|
| [P01-Agent-Discovery.kql](./P01-Agent-Discovery.kql) | `AgentsInfo`, `CloudAppEvents`, `OfficeActivity` | 2026-10-02 | Migrated from `AIAgentsInfo` (deprecated July 1, 2026). Display-name column is `Name`, not `AgentName` (confirmed live via `getschema` against tenant `AgentsInfo`, Sep 2026 — an earlier pass had this backwards). Q6 added: MCP server + tool count risk. Q1 and Q2 now classify identity in three states (`NoEntraIdentity`, `BlueprintOnly`, `AgentIdentity`) from `EntraAgentID` and `EntraBlueprintID`; a blueprint-only agent no longer counts as "no identity" or reaches High on its own. Q1 counts distinct agents (`dcountif`), not snapshot rows, and sorts High, Medium, Low (validated live, Oct 2026). Q3 now reads local agents from AgentsInfo (Platform LocalAgents) instead of an unverified CloudAppEvents action; validated live, 9 agents in 7 days. |
| [P02-Governance-Gaps.kql](./P02-Governance-Gaps.kql) | `AgentsInfo`, `AuditLogs`, `CloudAppEvents` | 2026-10-01 | Migrated from `AIAgentsInfo`. `Owners` (dynamic) cast to string before grouping. Q6 added: compound actions without per-step HITL events (AIRT Taxonomy v2.0 §5.4). Q1 splits identity orphans into `NoEntraIdentity` and `BlueprintOnly`. Q2, Q4 and Q6 rely on `AuditLogs` operation names (`AgentPublished`, `AgentPermissionApproved`, `AgentActionApproved`, ...) that do not exist on the validated tenant (no agent-named operation in 90 days) and are marked NOT VERIFIED; Microsoft documents Copilot Studio publish events in the Purview audit log (`BotUpdateOperation-BotPublish`). |
| [P03-Access-Anomalies.kql](./P03-Access-Anomalies.kql) | `CloudAppEvents`, `EntraIdSpnSignInEvents`, `AuditLogs`, `AgentsInfo`, `BehaviorInfo` | 2026-10-01 | Migrated from `AADSpnSignInEventsBeta` (deprecated Dec 2025). Field is `Country` (not `Location`). Q5b: capability/architecture disclosure (AIRT Taxonomy v2.0 §4.9). Q7: membership inference detection (privacy classification per Microsoft threat modeling). Q8: model inversion / training data reconstruction. Q10: `AgentsInfo` display-name column is `Name`, not `AgentName`. Q11 added: real-time protection blocks via `BehaviorInfo` (Microsoft Defender Security for AI). Q12 added: credential, owner, and sponsor changes on Agent ID objects, correlating `AuditLogs` with `AgentsInfo` by object id (validated on a live tenant, Oct 2026). Q12 deduplicates the `AgentsInfo` join (one agent can appear with and without a blueprint id); validated live, 7 rows over 90 days. Q12 is mapped to MITRE ATT&CK v19.2 (T1098.001, T1098), checked against the ATT&CK data. |
| [P04-Exfiltration-Detection.kql](./P04-Exfiltration-Detection.kql) | `CloudAppEvents`, `MicrosoftPurviewInformationProtection` | — | Sentinel tables — `TimeGenerated` correct. |
| [P05-Jailbreak-Detection.kql](./P05-Jailbreak-Detection.kql) | `LLMActivity`, `CloudAppEvents`, `MicrosoftPurviewInformationProtection`, `AuditLogs` | 2026-09-16 | Q1 rewritten to use `LLMActivity` (`RecordType == "CopilotInteraction"`, `mv-expand` on `LLMEventData.Messages`, `JailbreakDetected`), matching the official Microsoft example — confirmed live that `CloudAppEvents` has no `AgentInteraction` ActionType for this scenario. Q6: goal hijacking via sustained objective drift (AIRT Taxonomy v2.0 §4.4). Q7: LPCI via tool responses (OWASP AST03, arXiv:2507.10457). Q8: agentic ransomware chain detection — JadePuffer pattern (discovery → credential → lateral → encryption in compressed time window). |

**Live tenant findings (June 2026):** P01-Q2 returned shadow AI agents (Mural, Matter, 1Page, Teamflect, Priority Matrix) that had been operating for 951 days without an Entra Agent ID or assigned owner — validating the shadow AI detection logic.

> **Migration note:** `AIAgentsInfo` is deprecated on **July 1, 2026**. All queries in this repository already use `AgentsInfo`. If you have saved queries outside Defender XDR that reference `AIAgentsInfo`, migrate them before that date.
