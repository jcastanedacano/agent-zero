# Module 03 — Secure Access | Track B

**Module duration:** 90 minutes

**Learning objective:**
By the end of this module, participants will be able to design a Conditional Access architecture specific to agent identities, configure a valid CA policy using `clientApplications.includeAgentIdServicePrincipals`, validate it with the What If tool, detect OAuth consent drift via KQL, and document the critical difference between CA for users and CA for agents in their organization's Gap Assessment.

**Module agenda:**

| Time | Activity | Type |
|------|----------|------|
| 20 min | CA architecture for agents: scopes, valid and invalid grant controls, Blueprint-level vs. per-instance | Presentation |
| 15 min | Uncontrolled OAuth consent: how agents accumulate unreviewed permissions | Presentation |
| 45 min | Lab: CA policy for agents + What If validation + access audit KQL | Lab |
| 10 min | Gap assessment: access control and least privilege roadmap | Discussion |

---

**Core content (points the facilitator must cover):**

1. **The `grantControls: mfa` trap for agents:** A CA policy using `mfa` as a grant control on agent identities is **silently invalid** — it neither blocks nor authenticates. The agent cannot complete interactive MFA, and the policy generates no enforcement event in the logs. The only valid option to block an agent with CA is `"builtInControls": ["block"]`. This is not a bug — it is documented in the CA for workload identities reference.

2. **Blueprint-level CA as a scaling pattern:** Creating a CA policy per agent instance fails at scale. The correct architecture is a Blueprint-level CA policy using `clientApplications.includeAgentIdServicePrincipals` to cover all current and future agent identities derived from the same blueprint — without per-instance configuration.

3. **Applicable Microsoft controls:** Entra CA for Agents with `clientApplications.includeAgentIdServicePrincipals` enables agent-specific policies. Entra ID Protection evaluates service principal risk and can feed CA conditions. PIM just-in-time limits the elevated permission exposure window. Defender for Cloud Apps audits OAuth consent and surfaces application anomalies.

4. **OAuth consent as a silent accumulation vector:** An agent can accumulate additional permissions without any administrator explicitly approving them if the consent flow is unrestricted. The signal is in `AuditLogs` under `Add delegated permission grant` — without correlation to an approval event, it is a drift indicator.

5. **Credential isolation for non-managed-identity agents:** Managed identity (Azure-native, no credential on disk) is the correct architecture for agents running on Azure infrastructure. For agents running outside Azure — open source agents, local agents, third-party platforms — the token management problem is structurally different and typically solved insecurely: the real token lands inside the agent environment where it can be exfiltrated, committed to a git repo, or abused if the agent is compromised. The recommended pattern for these scenarios is a **placeholder token / proxy architecture**: a broker service issues the agent a placeholder JWT (signed by the broker, useless to any third party), and all API calls route through a proxy that intercepts the placeholder, verifies the broker signature, and swaps in the real token before forwarding. The agent never holds a real credential. For environments with SPIFFE/SVID support, the placeholder JWT can embed a representation of the agent's client certificate, enabling mTLS binding at the proxy — the token can only be used from the instance it was issued to. Reference: RFC 8705 (OAuth 2.0 mTLS), fly.io token proxy pattern (2023), Matthew Garrett (2026). Microsoft equivalent: managed identity + Key Vault references eliminates the problem entirely for Azure-hosted agents.

6. **CNAPP for Azure-hosted agent workloads:** If agents run as containerized workloads on Azure (AKS, Container Apps, Azure Functions), Defender for Cloud (CNAPP capability) extends security posture management to the infrastructure layer: container vulnerability assessment, runtime threat detection, and misconfiguration alerts for the environment hosting the agent. This is complementary to the identity and access controls covered in this module — Entra Agent ID secures the agent identity, CNAPP secures the compute it runs on. Enable the Defender for Containers plan in Defender for Cloud for any Azure subscription hosting agent workloads.

7. **Interactive (OBO) vs. Autonomous (client credentials) — two identity patterns with different attack surfaces:** Microsoft Entra Agent ID distinguishes two fundamental agent identity patterns with distinct security profiles. *Interactive agents* act on behalf of a signed-in user using the **on-behalf-of (OBO) flow** with delegated permissions — the risk is an agent misusing inherited user permissions or the user being unaware of what the agent executes in their name. *Autonomous agents* authenticate with their **own agent identity via client credentials flow** — no user in the loop; the risk is an agent operating without constraint if the identity has excessive permissions and no CA policy enforces a limit. A third pattern, the **agent's user account**, pairs 1:1 with an agent identity to give the agent a mailbox, Teams membership, and calendar — use only when the agent must access systems requiring a user object; risk: compromised agent joins meetings under false pretenses, sends communications as a trusted team member, or reads documents through collaborative access. Each pattern requires a distinct CA targeting strategy: OBO → target user + agent combination; autonomous → target agent identity blueprint (all instances inherit); agent user account → separate CA policy scoped to agent user object type.

8. **Identity Protection for agents — risk signals for non-human identities:** Microsoft Entra ID Protection detects anomalous activity for agent identities and generates risk scores from: (a) the agent's own actions (unusual authentication, out-of-scope resource access, high-velocity operations); (b) risk inherited from the sponsor (sponsor account compromise propagates to their agent identities). Risk signals feed directly into CA — a policy on the agent identity blueprint with `agentRisk = High` blocks all instances of that class in a single trigger. Microsoft Managed Policies provide a secure baseline: high-risk agent identities are blocked automatically. This creates a detection-to-containment chain for non-human identities: Identity Protection flags risk → CA blocks access → sponsor notified → human reviews and remediates. Reference: [Identity Protection for agents](https://learn.microsoft.com/en-us/entra/id-protection/concept-risky-agents).

9. **Global Secure Access for agents — network-level control plane:** Microsoft Entra Global Secure Access (GSA) adds a network enforcement layer independent of agent identity: (a) log all agent network activity (API calls, MCP server connections, web requests) to remote tools for audit and threat detection; (b) **web categorization** controls which APIs and MCP servers agents can reach — an agent cannot connect to an uncategorized or blocked MCP server even if its identity is authorized; (c) file upload/download restrictions by file type; (d) threat intelligence-based filtering blocks known malicious destinations automatically. Most architecturally significant for agentic security: GSA includes **prompt injection detection at the network level** — detecting and blocking attempts to inject malicious instructions through data the agent processes, before those instructions reach the model. This is a control plane layer independent of the agent's reasoning context (same principle as CAGE in Module 02 point 5), implemented at the network rather than the application layer. Reference: [Secure Web and AI Gateway for agents](https://learn.microsoft.com/en-us/entra/global-secure-access/concept-secure-web-ai-gateway-agents).

10. **Microsoft Edge Controls for shadow AI prevention at the endpoint:** The repo's discovery approach detects shadow AI after it exists (`AgentsInfo`, `CloudAppEvents`). Edge adds a prevention layer: organizations can configure Microsoft Edge browser policies to **block work-account users from accessing consumer-grade AI applications** (ChatGPT, Gemini, Claude.ai, Copilot without enterprise license, etc.) from corporate devices. This is enforced via Microsoft Intune device compliance + Edge browser policies applied to the work identity — when a user signs into Edge with their corporate account, the policy restricts which AI destinations they can access. Combined with Defender for Endpoint local agent discovery (Module 01), this closes the shadow AI gap at both the browser layer (consumer AI SaaS) and the endpoint layer (locally running agents). Configuration path: Intune → Device Configuration → Edge browser policies → `AIGenAIDefaultSettings` or per-site content policies.

11. **Model extraction via API as IP theft and evasion vector:** An attacker with access to an Azure AI Foundry endpoint can reconstruct a proprietary model through systematic queries (input/output pairs), without needing direct model access. Signals: >500 inferences/hour from a single identity, high rate of distinct prompts, grid-pattern query sequences (decision space exploration). Correct access control: per-identity rate limiting in Foundry + monitoring with P03-Q6. This vector maps to OWASP Agentic AG06 and is particularly relevant when the model was fine-tuned with proprietary data.

---

**Exercise / Lab:**

- **Name:** CA design and implementation for agent identities
- **Format:** Individual
- **Description:**
  1. In Entra ID → Security → Conditional Access, create the policy "Agentic AI — Risk-Based Access Control" with: users = none, apps = `clientApplications.includeAgentIdServicePrincipals`, condition = sign-in risk medium+, grant = block
  2. Validate with the **What If** tool: confirm the policy applies to `demo-sales-agent` with Medium risk, and does NOT apply to user accounts
  3. Attempt to configure the same policy with `grantControls: mfa` — document that What If generates no enforcement and record the finding in the Gap Assessment
  4. Run the KQL Library queries (P03-Access-Anomalies.kql): unreviewed OAuth consent, off-hours sign-ins, agents with excessive scopes
  5. Complete the "Domain 3 — Secure Access" section of the Gap Assessment Template
- **Required tools:** Entra ID (Conditional Access + What If), Microsoft Sentinel (Logs), KQL Library P03, Gap Assessment Template
- **Deliverable:** CA policy created and validated with What If (validation screenshot) + documented evidence of `grantControls: mfa` ineffectiveness + Domain 3 section of the Gap Assessment completed

---

**Closing questions for the facilitator:**
- When running What If with `grantControls: mfa`, what result did you get? How would you explain to a security team that an "active" policy in Entra CA is generating no real enforcement?
- In your CA architecture, where would you place PIM just-in-time for agent permissions? At the Entra role level or the OAuth scope level?

**Connection to the next domain:** Controlling agent access limits the potential scope of an attack, but does not protect the data the agent can read within that scope. Domain 4 covers the data layer: classification, labeling, DLP for AI interactions, and the correct remediation order before enabling retrieval.

→ [Module 04 — Protect Data](./Module-04-ProtectData.md)
