# Controls and risk vectors

Detail behind the domain table in the [main README](../README.md#domain-coverage-at-a-glance): the Microsoft controls each domain deploys, and the risk vectors each domain defends against.

## Microsoft controls coverage

Every domain maps to named, configurable Microsoft controls. Expand a domain to see what it deploys.

<details>
<summary><b>01 — Discover & Prioritize</b> · 6 controls</summary>


- Purview DSPM for AI
- Defender AI Agent Inventory
- Agent 365 Registry
- SharePoint Advanced Management
- CloudAppEvents (third-party agent discovery)
- Defender AI agent posture risk (Preview, July 2026): a risk level and risk indicators per agent, reviewed in Assets > AI agents

</details>

<details>
<summary><b>02 — Govern & Control</b> · 12 controls</summary>


- Entra Agent ID
- Copilot Studio governance + approval flow
- Foundry RBAC + API controls
- Power Platform DLP
- Tiered Autonomy (Logic Apps playbook tiers)
- CAGE model (independent control plane from reasoning path)
- Entitlement Management access packages (time-bound least privilege)
- Three-level kill switch (mark compromised and revoke user or agent-user sessions → Entra `accountEnabled=false` → runtime quarantine, unpublish or deployment delete) with measured RTO
- Human-on-the-loop override for tier 3 actions
- Direct tool invocation awareness (approval events must be cryptographically bound to the request, not readable claims in session history)
- Multi-owner agent governance (org-wide sharing policy default hardening, accountable-owner tracking outside the product, deletion-event monitoring for multi-owner agents)
- Named Conditional Access templates for agents (On behalf of / Autonomous agent access policy, Agent execution environments condition, Custom Security Attribute targeting at scale)

</details>

<details>
<summary><b>03 — Secure Access</b> · 11 controls</summary>


- Entra CA for Agents (`clientApplications.includeAgentIdServicePrincipals`)
- Named CA templates (On behalf of / Autonomous agent access policy)
- Entra ID Protection
- PIM just-in-time
- Defender for Cloud Apps
- Foundry rate limiting (model extraction prevention)
- Placeholder token/proxy pattern (non-Azure agents, RFC 8705 mTLS)
- Credential brokering vs. credential injection (token never enters agent memory)
- Defender for Cloud CNAPP (Azure-hosted agent workloads; AI agent inventory requires Microsoft Agent 365 license as of 1 Jul 2026)
- Direct tool invocation defenses (cryptographically-bound approval events, tool-call telemetry independent of model telemetry)
- AI gateway hardening (default credential rotation, admin/API credential separation, metadata-endpoint egress block, runtime-vs-config drift audit)

</details>

<details>
<summary><b>04 — Protect Data</b> · 8 controls</summary>


- Purview DLP (AI interactions workload)
- Insider Risk Management
- Sensitivity labels
- SharePoint Advanced Management
- Foundry RBAC (membership inference prevention)
- Context governance: ABAC + data minimization at data-to-agent boundary
- Context gap detection (audit of what data agent received as input)
- Cross-tenant vector search leakage (Azure AI Search security trimming + row-level access control per document + separate index per tenant — OWASP LLM09:2026)

</details>

<details>
<summary><b>05 — Detect & Respond</b> · 16 controls</summary>


- Defender XDR
- Microsoft Sentinel + native MCP server
- Security Copilot agents
- Purview Audit
- Agent 365
- Logic Apps (tiered automated response)
- KQL P05-Q8 agentic ransomware chain detection
- Behavioral drift monitoring (refusal rate baseline per agent, Sentinel Workbook 90-day rolling window)
- Canary tokens (decoy credentials for exfiltration detection)
- Honeytokens (decoy RAG documents for corpus access control validation)
- Agent-to-agent prompt injection (Prompt Shield indirect mode on subagent outputs, AgentId audit trail)
- Sequence signatures for autonomous operations (retry-with-variation, inter-action latency distribution, post-access verification)
- Agent honeypots (decoy environment with LLM-only discrimination instruction, placement, interaction depth, canary mechanism)
- Security agent configuration integrity (prompt/tool-set hashing + change-record correlation)
- Defender threat detection for Agent 365 agents (Preview, July 2026): near-real-time alerts for jailbreak, indirect prompt injection, malicious content propagation, secret leakage, evasion, LLM reconnaissance and suspicious user or IP access
- Defender real-time protection for Agent 365 tooling servers (GA, July 2026): allow or block tool invocations to Work IQ MCP and customer MCP tools

</details>

<details>
<summary><b>06 — Regulatory Compliance</b> · 6 controls</summary>


- Microsoft Purview Compliance Manager (EU AI Act + ISO 42001 + NIST AI RMF 1.0 templates)
- Purview Audit (immutable record keeping)
- Copilot Studio disclosure settings (Art. 13)
- Autonomy-graded incident taxonomy (human-directed / agent-initiated in scope / agent-initiated out of scope)
- Jurisdictional reach documented per agent connector and MCP server
- Assurance case structure over the Gap Assessment

</details>

<details>
<summary><b>07 — Vendor & Third-Party AI Risk</b> · 10 controls</summary>


- Power Platform DLP (block unapproved connectors)
- Microsoft 365 admin center Agents and Tools (MCP server allow/block)
- AgentsInfo.McpServers + CloudAppEvents ExecuteToolByGateway (audit)
- Azure AI Foundry model layer controls (prompt shields, content filters, groundedness detection)
- Open source AI platform hardening (Langflow, Flowise, n8n)
- Denial-of-Wallet mitigation (APIM rate limiting + Azure Cost Management alerts + input token pre-filter + per-deployment TPM quotas)
- AI-BOM (machine-readable bill of materials: model version, dataset provenance, fine-tuning lineage, MCP server hashes — maps to EU AI Act Art. 13 and NIST AI RMF GOVERN-4)
- Agent KYC (Entra Agent ID sponsor as deployer attestation + per-agent APIM subscription key for attribution and granular revocation + no payment instruments held by agents)
- Model weight security posture as a vendor question (B5)
- Purview Claude Enterprise connector (prompt/response visibility into a monitored external model vendor)

</details>

## Risk vectors covered

What each domain is defending against. These are the vectors the labs actually exercise and the KQL actually detects. **56 distinct vectors** across 6 domains.

<details>
<summary><b>01 — Discover & Prioritize</b> · 5 vectors</summary>


- Shadow AI
- Identity exposure
- Data exposure
- Local AI agents without endpoint connector
- Third-party agents (ISV plugins, MCP servers)

</details>

<details>
<summary><b>02 — Govern & Control</b> · 9 vectors</summary>


- No technical owner
- Makers without controls
- No lifecycle
- Graph drift
- Multi-agent trust boundaries
- Unsafe agent autonomy (no tiered autonomy model)
- Control plane collapsed into reasoning path (description laundering / rubber-stamp approval)
- No tested emergency shutdown (untested kill switch, or a kill switch that depends on the agent's own reasoning path)
- Diffused accountability under equal-rights multi-owner agents (any owner can delete the agent, remove co-owners, or enable org-wide sharing)

</details>

<details>
<summary><b>03 — Secure Access</b> · 10 vectors</summary>


- CA inherited from users
- Over-permissioned agents
- Uncontrolled OAuth consent
- Identity laundering
- Model extraction via API
- Token exfiltration from non-managed-identity agent environments
- Internet-exposed AI dev platforms (Langflow CVE-2025-3248 class)
- Direct tool invocation bypassing the reasoning path entirely (no model call, no prompt-layer detection)
- Forged approval events collapsing tiered autonomy to full automation
- AI gateway compromise (auth bypass, guardrail sandbox escape to root, SSRF defeating IMDSv2, config-vs-runtime drift)

</details>

<details>
<summary><b>04 — Protect Data</b> · 8 vectors</summary>


- Prompt injection
- Oversharing
- API exfiltration
- Corpus poisoning (SharePoint)
- Model supply chain poisoning
- Memory/session poisoning
- Membership inference (privacy without exfiltration)
- Context gap (agent acting on stale, misrouted, or wrong data at machine speed)

</details>

<details>
<summary><b>05 — Detect & Respond</b> · 13 vectors</summary>


- Jailbreak attempts
- Agent anomaly
- Structural false negatives
- Evasion at inference boundary
- Goal hijacking (sustained objective drift)
- Capability/architecture disclosure
- LPCI via tool responses
- Agentic ransomware chain (autonomous multi-stage, adaptive, no human pause)
- Behavioral drift (silent safety degradation without config change)
- Agent-to-agent prompt injection (multi-agent trust boundary compromise)
- Exfiltration confirmation gap (no detection signal when controls fail — addressed by canary tokens and honeytokens)
- Signature-varying autonomous operations (IOC-based detection fails against an attacker that regenerates artifacts on every attempt)
- Compromised or subverted monitoring agent (security agent configuration altered without a change record)

</details>

<details>
<summary><b>07 — Vendor & Third-Party AI Risk</b> · 11 vectors</summary>


- MCP server tool injection
- Credential exposure via tool return values
- Silent remote tool updates
- Open source AI platform RCE
- Model layer risks (prompt logging, training data use, no red team documentation)
- Foundry model layer misconfiguration (no content filters, no prompt shields)
- Denial-of-Wallet (high-cost sponge example flooding of pay-per-token API depleting monthly budget)
- AI supply chain opacity (no model provenance, no dataset lineage, no fine-tuning documentation)
- No agent-level identity verification at the provider (shared tenant key destroys attribution and granular revocation)
- Model weight exposure (open-weight or self-hosted deployments transfer the entire weight-security burden to your organization)
- Autonomous offensive tooling adopted without scoped written authorization (dual-use, Cobalt Strike trajectory)

</details>
