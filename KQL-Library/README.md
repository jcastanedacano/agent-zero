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
