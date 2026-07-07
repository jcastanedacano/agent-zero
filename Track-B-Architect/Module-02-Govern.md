# Module 02 — Govern & Control | Track B

**Module duration:** 90 minutes

**Learning objective:**
By the end of this module, participants will be able to design an agent governance model covering ownership, approval, lifecycle, and DLP policies; configure Entra Agent ID and the Copilot Studio approval flow in a demo tenant; detect Agent Builder bypass via KQL; and document their organization's governance gaps with a prioritized remediation roadmap.

**Module agenda:**

| Time | Activity | Type |
|------|----------|------|
| 20 min | Agentic governance model: dimensions, roles, and approval flows | Presentation |
| 15 min | Entra Agent ID vs. Service Principal: schema differences, CA targeting, and forensic value | Presentation |
| 45 min | Lab: Entra Agent ID + Copilot Studio approval + Power Platform DLP + governance KQL | Lab |
| 10 min | Gap assessment: governance maturity and roadmap | Discussion |

---

**Core content (points the facilitator must cover):**

1. **Agent Builder bypass as a systemic gap:** Agent Builder (M365 Copilot) activates agents immediately without going through the Copilot Studio approval flow. This is a product-level design bypass — not a configuration error. The compensating control is a Conditional Access policy on the Agent Builder App ID, or a Sentinel alert rule on `AuditLogs` filtering `AgentSource == "AgentBuilder"`.

2. **Graph drift as accumulated risk:** Without a periodic permission review process, agents accumulate OAuth scopes without correlation to approvals. The drift is gradual and invisible: `Sites.Read.All` becomes `Sites.ReadWrite.All` after a developer adds it without a change management process. The architectural solution is PIM just-in-time for agent permissions — not just for human roles.

3. **Applicable Microsoft controls:** Entra Agent ID establishes a manageable identity per agent, separate from user identities and generic service principals. Copilot Studio governance enables the pre-publication approval flow. Foundry RBAC + API-level controls restrict what agents can do in Azure AI. Power Platform DLP classifies and blocks connectors by category (Business / Non-business / Blocked).

4. **Lifecycle as an active security control:** Agent decommission must include: token revocation, Entra permission removal, Agent 365 registry closure, and archival of ownership documentation. An "abandoned" agent with active permissions is an attack vector with a legitimate identity.

5. **The control plane must be independent of the agent's reasoning path:** A common governance mistake is using the agent itself to determine whether its proposed action is safe. This collapses the security boundary: if the agent's reasoning is influenced (via prompt injection, poisoned context, or LPCI), the safety evaluation is influenced too. The correct architecture separates reasoning from execution through an independent control plane layer — a policy engine that evaluates the proposed action against security principles *outside* the agent's reasoning context. The CAGE model provides a practical structure: **C**lassify the proposed action, **A**pprove based on risk and evidence (not just the agent's explanation), **G**ate execution through policy and least-privilege tools, **E**vidence-log the request, decision, action, and outcome. The approval screen must show the actual command or API call — not only the agent's description of it. Showing only the agent's explanation creates a rubber stamp: reviewers approve what the agent said it would do, not what it will actually execute.

6. **Tiered Autonomy — when the agent acts alone and when it stops:** Without an explicit autonomy tier definition, every production agent defaults to "full automation" mode — the most common governance gap. Three-tier framework: (1) *Full automation* for low-risk, reversible actions with bounded blast radius; (2) *Human approval* for actions affecting multiple users, external systems, or sensitive data; (3) *Human-led* for high-risk actions — account disablement, data deletion, policy changes. Each agent must have its tier documented as part of the governance record, not as an implicit assumption.

---

**Exercise / Lab:**

- **Name:** Governance model implementation in demo tenant
- **Format:** Individual
- **Description:**
  1. In Entra ID → App registrations, create `demo-sales-agent` with `Sites.Read.All` permission and mark it as an Entra Agent ID in the manifest (`"tags": ["agent365", "EntraAgentId"]`)
  2. In Copilot Studio admin center → Settings → Agent publishing, enable the approval flow and configure an approver
  3. In Power Platform admin center, create the DLP policy "Agentic AI — Restrict External Connectors" blocking HTTP and HTTP with Azure AD
  4. Run the governance queries from the KQL Library (P02-Governance-Gaps.kql): agents without Entra Agent ID, agents published without approval, graph drift
  5. Complete the "Domain 2 — Govern" section of the Gap Assessment Template with real findings from the demo tenant
- **Required tools:** Entra ID (App registrations + Manifest editor), Copilot Studio admin center, Power Platform admin center, Microsoft Sentinel (Logs), KQL Library P02, Gap Assessment Template
- **Deliverable:** Entra Agent ID created and verified in Agent 365 Registry + Domain 2 section of the Gap Assessment completed with identified gaps, assigned owners, and target dates

---

**Closing questions for the facilitator:**
- When running the query for agents without an Entra Agent ID, what percentage of the total agent count appeared in that result? What process in your organization would have registered them correctly?
- If you had to implement the governance model designed today in production, what would be the first organizational (non-technical) obstacle you would encounter?

**Connection to the next domain:** Governance defines who approves an agent and what process it follows. Domain 3 takes those approved identities and defines what they can access — verifiable least privilege, CA policies specific to agents, and how to audit OAuth consent drift before it escalates.

→ [Module 03 — Secure Access](./Module-03-SecureAccess.md)
