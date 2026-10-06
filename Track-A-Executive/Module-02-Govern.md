# Module 02 — Govern & Control | Track A

**Module duration:** 45 minutes

**Learning objective:**
By the end of this module, participants will be able to evaluate the governance maturity of their organization's agent model, identify the most critical ownership and lifecycle gaps, and prioritize the policy decisions that reduce identity graph drift risk in their Microsoft 365 environment.

**Module agenda:**

| Time | Activity | Type |
|------|----------|------|
| 10 min | Agent governance: why it differs from traditional application governance | Presentation |
| 10 min | The four most common gaps: no owner, uncontrolled makers, no lifecycle, graph drift | Presentation |
| 20 min | Exercise: Governance maturity assessment | Exercise |
| 5 min | Wrap-up and connection to Domain 3 | Discussion |

---

**Core content (points the facilitator must cover):**

1. **The absent owner problem:** When an agent has no assigned technical owner, no team is accountable for its permissions, behavior, or decommission. In M365 E5 environments, the most common vector is Agent Builder: any licensed user can share an agent that enters production without admin review; only agents submitted to the organization catalog are approved by an admin.

2. **Identity graph drift:** Agents accumulate permissions over time without review. An agent that starts with `Sites.Read.All` can end up with `Mail.ReadWrite` after several integrations. Without a permission review process, the agent's identity graph diverges from what was originally approved.

3. **Applicable Microsoft controls:** Entra Agent ID provides a dedicated, manageable identity per agent. The Copilot Studio approval flow controls publication. Foundry RBAC and API controls restrict what agents can do in Azure AI. Power Platform DLP classifies and blocks unauthorized connectors.

4. **Lifecycle as an active security control:** A decommissioned agent with active permissions is an attack vector. The offboarding process must include disabling the identity and removing its credentials, Entra permission removal, and closure of the Agent 365 registry entry.

---

**Exercise:**

- **Name:** Governance maturity assessment
- **Format:** Individual
- **Description:**
  1. Participants receive a rubric with 5 dimensions: ownership, approval process, permission review, lifecycle, and maker traceability
  2. For each dimension, select the organization's maturity level: Initial / Developing / Defined / Managed
  3. Identify the lowest-maturity dimension and describe in two sentences what executive decision could advance it one level
  4. Calculate the overall governance maturity average
  5. Record the result in the "Domain 2" section of the Risk Posture Map
- **Required tools:** Maturity rubric (provided by facilitator); no system access required
- **Deliverable:** Governance maturity documented in the Risk Posture Map + one prioritized executive decision for the weakest dimension

---

**Closing questions for the facilitator:**
- Does your organization today have a formal approval process before an AI agent enters production? Who approves it and with what criteria?
- If an agent deployed six months ago is no longer used by the team that created it, what happens to its permissions? Who would detect it?

**Connection to the next domain:** Knowing who owns an agent does not solve the question of what that agent can do. Domain 3 addresses access control: how to ensure agents operate with verifiable least privilege and what an agent's identity means in the context of Conditional Access policies.

→ [Module 03 — Secure Access](./Module-03-SecureAccess.md)
