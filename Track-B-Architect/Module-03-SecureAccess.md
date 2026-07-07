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

7. **Model extraction via API as IP theft and evasion vector:** An attacker with access to an Azure AI Foundry endpoint can reconstruct a proprietary model through systematic queries (input/output pairs), without needing direct model access. Signals: >500 inferences/hour from a single identity, high rate of distinct prompts, grid-pattern query sequences (decision space exploration). Correct access control: per-identity rate limiting in Foundry + monitoring with P03-Q6. This vector maps to OWASP Agentic AG06 and is particularly relevant when the model was fine-tuned with proprietary data.

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
