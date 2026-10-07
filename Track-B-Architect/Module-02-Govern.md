# Module 02 — Govern & Control | Track B

**Module duration:** 90 minutes

**Learning objective:**
By the end of this module, participants will be able to design an agent governance model covering ownership, approval, lifecycle, and DLP policies; configure Entra Agent ID and operate the admin approval queue for published agents in a demo tenant; restrict and review Agent Builder sharing; and document their organization's governance gaps with a prioritized remediation roadmap.

**Module agenda:**

| Time | Activity | Type |
|------|----------|------|
| 20 min | Agentic governance model: dimensions, roles, and approval flows | Presentation |
| 15 min | Entra Agent ID vs. Service Principal: schema differences, CA targeting, and forensic value | Presentation |
| 45 min | Lab: Entra Agent ID + Copilot Studio approval + Power Platform DLP + governance KQL | Lab |
| 10 min | Gap assessment: governance maturity and roadmap | Discussion |

---

**Core content (points the facilitator must cover):**

1. **Agent Builder sharing as a systemic gap:** by default every licensed user can create an Agent Builder agent (M365 Copilot) and share it with the whole organization without a request to an admin; only submission to the organization catalog goes to admin review. This is an open default, not a product limit. The controls are administrative: restrict who can share agents (specific users or groups, or no users) and block agents in the Microsoft 365 admin center (Microsoft Learn, Agent Builder, Oct 2026). Learn documents neither a Conditional Access target for Agent Builder nor an audit operation for sharing, so neither a Conditional Access policy nor an `AuditLogs` alert rule is a control here: detection is by registry inventory (type **Shared by creator**) and by the agent in use in `CopilotActivity`.

2. **Graph drift as accumulated risk:** Without a periodic permission review process, agents accumulate OAuth scopes without correlation to approvals. The drift is gradual and invisible: `Sites.Read.All` becomes `Sites.ReadWrite.All` after a developer adds it without a change management process. The architectural solution is PIM just-in-time for agent permissions — not just for human roles.

3. **Applicable Microsoft controls:** Entra Agent ID establishes a manageable identity per agent, separate from user identities and generic service principals. Publishing a Copilot Studio agent to the organization requires admin approval in the Microsoft 365 admin center (Agents > All agents > Requests). Foundry RBAC + API-level controls restrict what agents can do in Azure AI. Power Platform DLP classifies and blocks connectors by category (Business / Non-business / Blocked). **CIS Controls alignment:** Agent identities map directly to CIS Control 5 (Account Management) — provisioning, scoped permissions, periodic review, and decommission with identity disable and credential removal. Graph drift (point 2 above) is the agentic form of CIS 5.3 (disable dormant accounts). Lifecycle management (point 4) maps to CIS 5.1 (maintain authorized account inventory). Reference: CIS Controls AI Agent Companion Guide (2026), Control 5 — Agent Applicability.

4. **Lifecycle as an active security control:** Agent decommission must include: disabling the identity and removing its credentials, Entra permission removal, Agent 365 registry closure, and archival of ownership documentation. An "abandoned" agent with active permissions is an attack vector with a legitimate identity.

5. **The control plane must be independent of the agent's reasoning path:** A common governance mistake is using the agent itself to determine whether its proposed action is safe. This collapses the security boundary: if the agent's reasoning is influenced (via prompt injection, poisoned context, or LPCI), the safety evaluation is influenced too. The correct architecture separates reasoning from execution through an independent control plane layer — a policy engine that evaluates the proposed action against security principles *outside* the agent's reasoning context. The CAGE model provides a practical structure: **C**lassify the proposed action, **A**pprove based on risk and evidence (not just the agent's explanation), **G**ate execution through policy and least-privilege tools, **E**vidence-log the request, decision, action, and outcome. The approval screen must show the actual command or API call — not only the agent's description of it. Showing only the agent's explanation creates a rubber stamp: reviewers approve what the agent said it would do, not what it will actually execute.

6. **Tiered Autonomy — when the agent acts alone and when it stops:** Without an explicit autonomy tier definition, every production agent defaults to "full automation" mode — the most common governance gap. Three-tier framework: (1) *Full automation* for low-risk, reversible actions with bounded blast radius; (2) *Human approval* for actions affecting multiple users, external systems, or sensitive data; (3) *Human-led* for high-risk actions — account disablement, data deletion, policy changes. Each agent must have its tier documented as part of the governance record, not as an implicit assumption.

7. **Sponsorship model and Lifecycle Workflows — automating the ownership guarantee:** Microsoft Entra Agent ID formalizes the "agent without owner" problem as a first-class governance object. Every agent identity and blueprint requires at least one assigned **sponsor** (users, or select groups, up to 100 per object): a human accountable for the agent's lifecycle decisions, access reviews, and decommission. Critically, if a sponsor leaves the organization, Entra automatically transfers sponsorship to the sponsor's manager via **Lifecycle Workflows** — ensuring there is always a human accountable for every agent identity, without manual intervention. The transfer task needs a populated manager attribute on the departing sponsor (Microsoft Learn), so check that first. Sponsors operate through two portals: My Account (enable/disable the agent, view activity and access) and My Access (request access packages on behalf of the agent). Without this automation, sponsorship gaps accumulate silently — the `Owners` field in `AgentsInfo` will show the original owner even after they've left. KQL P02 governance gap queries surface agents with empty or unresolvable owners; Lifecycle Workflow tasks address the root cause structurally.

   ```mermaid
   flowchart TB
       A["Agent identity or blueprint<br/>requires at least one sponsor<br/>(users or groups, up to 100 per object)"]
       I["Sponsor tools<br/>My Account: enable or disable the agent, view activity<br/>My Access: request access packages for the agent"]
       B["A sponsor leaves the organization"]
       C{"Manager attribute populated<br/>on the departing sponsor?"}
       D["Lifecycle Workflows task transfers<br/>sponsorship to the sponsor's manager"]
       F["A human is accountable again for<br/>lifecycle decisions, access reviews, decommission"]
       E["The task cannot run:<br/>nothing moves"]
       G["The gap grows silently<br/>AgentsInfo Owners still shows the original owner"]
       H["KQL P02 governance gap queries find<br/>empty or unresolvable owners"]
       A --> I
       A --> B --> C
       C -->|"yes"| D --> F
       C -->|"no"| E --> G --> H

       classDef blue fill:#0078D4,stroke:#333,color:#fff
       classDef purple fill:#5E2750,stroke:#333,color:#fff
       classDef green fill:#107C10,stroke:#333,color:#fff
       classDef orange fill:#FF8C00,stroke:#333,color:#24292f
       class A,I blue
       class B,C purple
       class D,F green
       class E,G,H orange
   ```

   **How to read it.** Read it top to bottom. The only branch is the manager attribute: Lifecycle Workflows can move sponsorship to the departing sponsor's manager only when that attribute is populated (Microsoft Learn), so check it before relying on the automation. The orange path is what you see when it is not: nothing moves, and `AgentsInfo` keeps listing the original owner, which is why the P02 governance gap queries exist.

   > **The blueprint is where the credentials live, not the instance.** Every agent identity is instantiated from an identity blueprint, and the blueprint — not any individual agent — holds the credentials, declared permissions, and publisher verification. This has a governance consequence worth stating explicitly: compromising the blueprint compromises every agent derived from it, and disabling the blueprint shuts all of them down in one action. That is exactly why the fourth kill-switch level in point 10 targets the blueprint rather than the instance when you cannot yet tell which instance is the threat. For third-party agents specifically, verify the vendor publishes a **multitenant blueprint to the Microsoft catalog** rather than distributing standalone credentials — that is what lets you revoke the vendor's ability to provision new identities in your tenant without depending on their cooperation. One licensing detail worth confirming against current Microsoft documentation before quoting it in a governance review: a principal blueprint is commonly cited with a cap on how many agent identities it can provision (reported at 250 at the time of writing) — treat that number as a planning input to verify, not a fact to repeat unchecked, since Microsoft ships changes to Agent 365 limits frequently.

8. **Multi-owner in Copilot Studio and Agent Builder — the exception to single accountability (MC1438569, GA August 2026):** Microsoft introduced support for multiple owners on Microsoft 365 Copilot declarative agents. Before this change an agent had exactly one owner, the creator. Now it can have several, and the official documentation is explicit: *"An owner is anyone with Can edit access. All owners have equal rights, including the ability to add or remove people, switch roles, and turn on org-wide sharing."* There is no primary or secondary owner designation, and this is not a temporary rollout limitation — it is the final design.

   **The tension with point 7 of this module:** Entra Agent ID separates accountability from administration: at least one sponsor is required per agent identity and blueprint (up to 100 users or select groups, Microsoft Learn), sponsors can disable, soft-delete, and edit the sponsor list but cannot touch credentials or owners, and Lifecycle Workflows move sponsorship to the manager of a sponsor who leaves, so accountability never falls vacant. Copilot Studio / Agent Builder ownership is deliberately plural and equal. These are distinct governance objects — one in the identity plane, one in the application plane — and today they do not converge. The practical consequence: an agent can have three owners with identical rights, and none of them is the person who answers during an incident review. Any owner can also remove the other owners, change their roles, and **delete the agent permanently and irreversibly** without the other owners' consent.

   **Available controls, and the one to change from its default before rollout:** the Microsoft 365 admin center exposes a three-level policy for sharing agents organization-wide: *All users* (anyone can share with the whole organization — this is the default), *Specific users or groups*, and *No users*. An agent shared organization-wide is automatically published to the Agent Store, discoverable by the entire tenant. With plural, equal ownership the effective control point is not "the creator decided" but "the owner with the weakest judgment decided": any of them can flip the org-wide sharing toggle. Action before rollout reaches the tenant: move the policy from *All users* to *Specific users or groups*, not afterward. Operational note: changing the policy does not revoke already-shared access, it only applies to new sharing actions, so a tenant that arrives late to this change also needs to audit what already exists.

   **A detail that is easy to miscommunicate:** M365 groups and security groups can never be owners; they can only receive chat permission (*Can chat*). "I gave the Finance group access to the agent" is not shared ownership, it is usage. Internal guidance must draw this distinction explicitly so nobody assumes shared management where there is only chat access.

   **Recommended adjustment to P02:** until Microsoft offers an accountable-owner distinction inside the product, keep that field in your own governance registry, outside `AgentsInfo`. And add an alert to the governance queries for deletion events on agents with multiple owners — since deletion is irreversible and any owner can execute it without the others' approval, it is a signal that deserves review before the fact, not just an audit trail after it. Reference: [MC1438569 — M365 Copilot Agent now support multiple users](https://admin.microsoft.com/Adminportal/Home#/MessageCenter) (Microsoft 365 Message Center, published 25 July 2026, GA August 2026); [Share and manage agents](https://learn.microsoft.com/microsoft-365/copilot/extensibility/agent-builder-share-manage-agents), Microsoft Learn.

9. **Access packages for agent identities — entitlement management as least privilege:** The formal Microsoft mechanism for granting access to agent identities is **Entitlement Management with access packages**, not static OAuth scope assignment. Access packages can grant: Security Group memberships, Application OAuth API permissions (including Graph application permissions), and Microsoft Entra roles. Three request pathways: (a) the agent identity itself requests programmatically via `POST /entitlementManagement/assignmentRequests` (Graph API) when it needs access for a specific operation; (b) the sponsor requests on behalf of the agent; (c) an administrator directly assigns. Access packages include an **expiry date** — as the date approaches, the sponsor receives a notification and must actively renew (triggering a new approval cycle) or the assignment expires automatically. This is time-bound least privilege with human-in-the-loop renewal, which is architecturally stronger than permanent OAuth scope grants that accumulate via graph drift (point 2 above). Reference: [Access packages for agent identities](https://learn.microsoft.com/en-us/entra/agent-id/agent-access-packages).

10. **Kill switch and fail-safe — the control Tiered Autonomy does not cover:** The Tiered Autonomy model (point 6) defines when an agent stops by design. The kill switch answers a different question: how do you stop an agent that should not be running at all, because it was compromised, because it drifted from its objective, or because the operator lost visibility into what it is doing. Without a tested procedure, the default answer is to open a ticket, and that is measured in hours while the agent operates in seconds.

   **Three shutdown levels in the Microsoft stack, fastest to most definitive:**

   | Level | Action | Effect | Typical latency |
   |-------|--------|--------|-----------------|
   | L1 Mark compromised and revoke what can be revoked | `POST /identityProtection/riskyAgents/confirmCompromised` (Graph beta) for the agent; `POST /users/{id}/revokeSignInSessions` (Graph) for the agent's user account or the user whose delegated session the agent holds | Sets the agent's risk to High, which blocks new token issuance only if a Conditional Access policy on Agent risk exists; invalidates the refresh tokens of that user. Graph has no session-revocation call for a service principal or an agent identity | Seconds (Logic App playbook, Module 05) |
   | L2 Identity disable | Entra: `accountEnabled = false` on the Entra Agent ID service principal (`PATCH /servicePrincipals/{id}`, or Entra admin center → Agents → Agent identities → Disable) | New token requests fail with AADSTS7000112; configuration and forensic evidence are preserved. A token already issued stays valid until it expires (60 to 90 minutes by default); Continuous Access Evaluation for workload identities rejects it on disable, for Microsoft Graph only, single-tenant apps only, not managed identities | Minutes |
   | L3 Runtime stop | Copilot Studio: quarantine the agent (Power Platform API `SetAsQuarantined`, takes a user token) or unpublish it / Azure AI Foundry: delete the deployment / APIM: block policy on the agent's route | The code stops executing. Quarantine keeps the agent and its configuration, makers can still test it, and it cannot be used in other channels | Minutes to hours depending on platform |

   ```mermaid
   flowchart LR
       subgraph INST["One agent instance: you know which one"]
           direction LR
           L1["L1 Mark compromised and revoke<br/>what can be revoked<br/>seconds"] --> L2["L2 Disable the identity<br/>minutes<br/>issued tokens live 60 to 90 min"]
           L2 --> L3["L3 Runtime stop<br/>quarantine, unpublish, delete the deployment,<br/>block the route<br/>minutes to hours"]
       end
       subgraph WIDE["Wider scope: you do not know which instance"]
           direction LR
           BP["Disable the blueprint<br/>every identity derived from it"] --> VB["Revoke the vendor's blueprint<br/>no further identities can be provisioned"]
       end
       L2 -. "scope widens" .-> BP
       GAP["What a missing level leaves<br/>L1 without L2: the agent returns while the credentials stay valid<br/>L2 without L3: a cached API key keeps working<br/>L3 by deleting: destroys evidence, so prefer quarantine"]

       classDef lvl fill:#0078D4,stroke:#333,color:#fff
       classDef wide fill:#5E2750,stroke:#333,color:#fff
       classDef gap fill:#FF8C00,stroke:#333,color:#24292f
       class L1,L2,L3 lvl
       class BP,VB wide
       class GAP gap
   ```

   **How to read it.** Left to right in the top row is the order to run: fastest first, most definitive last. The bottom row is not another step but another scope: use it when the compromise is in a shared blueprint or a vendor template and you cannot tell which instance is the bad one. The orange box is the argument for running more than one level.

   L1 without L2 is a shutdown the attacker can reverse: if the credentials remain valid, the agent returns on the next authentication cycle. L2 is not instant either: an access token already issued to the agent stays valid until it expires, so the drill must measure the real stop time, not the time of the call. L2 without L3 stops the identity but not the process: a self-hosted agent with a cached API key can keep operating against endpoints that do not validate Entra. Full shutdown requires all three levels, and the order matters: L1 first because it is fastest, L3 last because deleting the agent destroys state that may be evidence (quarantining it does not, so prefer quarantine while you collect evidence).

   **A fourth level this table omits: blueprint-level shutdown.** All three levels above assume you know which agent instance is compromised. When you do not — a supply-chain compromise of a shared blueprint, or a vendor-provided agent template used across dozens of instances — the correct scope is the blueprint, not the instance: disabling the Entra Agent ID blueprint that generated the compromised agents shuts down every identity derived from it in a single action, without needing to identify which specific instance is the threat. This is a broader-blast-radius L2, positioned between L2 and L3 in scope: faster to execute than hunting for the one bad instance, but it takes down every agent built from that blueprint, including the legitimate ones. For third-party agents specifically, a fifth and final option exists above blueprint-level: revoking the vendor's principal blueprint in your tenant, which removes its ability to provision any further identities at all — the correct response when the vendor relationship itself is the compromise, not just one deployment. Decide the authorization threshold for each of these five levels before an incident, not during one: blueprint-level shutdown stops legitimate business processes, so if that decision requires a committee, it will not happen in time during a real incident.

   **Non-negotiable design requirement:** the kill switch cannot depend on the agent's reasoning path. A "stop if you detect X" instruction in the system prompt is not a kill switch, it is a suggestion that a compromised, poisoned, or drifted agent can ignore or rationalize away. This is point 5 of this module applied to the worst case: the stop must be enforced at the identity, network, or runtime layer, outside the model's context window. The autonomous systems literature states it directly: system-prompt-based shutdown mechanisms will be naturally resisted by any system whose objective function includes staying operational.

   **An untested kill switch does not exist.** Every agent in the governance registry must have documented: who can trigger it (by role, not by person), through which technical route, and what the RTO is as measured in a real drill. Minimum quarterly exercise: execute L1 + L2 on a non-critical agent and time it from decision to confirmed stop. If nobody has measured that number, the control exists in the document and not in the operation.

   **Human-on-the-loop for tier 3:** for destructive or irreversible actions, the relevant distinction is not human-in-the-loop (the person approves each step before execution) but human-on-the-loop (the person supervises execution continuously and can interrupt at any moment). Tier 3 of Tiered Autonomy must implement both: prior approval and the ability to interrupt during execution. Reference: CIS Controls AI Agent Companion Guide (2026), kill switch guidance; NIST AI RMF MANAGE-2.4 and MAP-3.5; EU AI Act Art. 14 (human oversight with override capability); HACCA report (2026), "Fail-safe mechanisms and kill switches".

11. **Direct tool invocation — the attack that does not cross the control plane, it goes around it:** Point 5 establishes that the control plane must be independent of the agent's reasoning path. The CoreBreak research (BlackHat USA 2026) documents the complementary and more serious failure: an attacker who **does not go through the reasoning at all**. In several widely used agent SDKs, the runtime accepts a tool-call block as input and executes it directly on the next invocation, with no model call in between. The attacker chooses the tool and its arguments outright. The vendor's official response describes it without ambiguity: the input is considered trusted, and a tool-call block as the most recent message causes the agent to run that tool directly on its next invocation, with no model call in between.

    **Why this breaks half the detection architecture:** every control that relies on inspecting the prompt — Prompt Shield, content filters, the P05-Q1 and P05-Q9 queries — is positioned around the model. If the model is never invoked, none of those controls execute and none of them generate telemetry. This is not evasion: the control is simply not in the path. The researchers' conclusion is that this is not a one-off bug or a single SDK but a structural pattern — they found the same class of failure in AWS's agent SDK, Google's Agent Development Kit, and Vercel's AI SDK.

    **The variant that directly affects Tiered Autonomy: the forged human approval.** In Google's ADK, approval of a tier 2 or 3 action materializes as an event in the session history. The researchers demonstrated that an attacker able to write to that history can inject a fabricated confirmation event, with whatever tool and arguments they want and the confirmation field set to true, and the runtime executes it as if a human had approved. The approval was not bound to the request: it was a claim inside a message the caller could author. Assigned CVE-2026-18236 and patched. The design consequence is that **if the approval event is forgeable, all three tiers collapse to tier 1** and the documented autonomy model describes a reality that does not exist.

    **Architecture questions this forces you to answer for every agent in the registry:**
    - Does the agent runtime accept tool-call blocks as external input? If the answer is yes or unknown, the agent's tool inventory is the direct attack surface, no matter how good the system prompt is.
    - Is the approval event cryptographically bound to the request it approves, or is it a claim in a message? The approval must originate from the approval service and be verifiable against it, not read from session history. This is exactly the separation between identity evidence, authorization evidence, and execution evidence that the verifiable authorization literature proposes; APIM with `validate-jwt` on the invocation route is the functional approximation available today in the Microsoft stack.
    - Is there tool-invocation telemetry independent of model telemetry? If all evidence of what the agent did comes from inference logs, a direct invocation leaves no trace. `CloudAppEvents` with `ExecuteToolByGateway` covers this when tools route through APIM, and it is the operational reason the gateway in Module 07 point 2 matters beyond the allow-list.

    Reference: Hedi Ingber and Aviyam Ivgi, "The CoreBreak Attack: Turning AI Agents into Credentials Exfiltration Vectors", BlackHat USA 2026. CVE-2026-18236 (Google ADK), CVE-2026-18830 and bulletin 2026-073-AWS.

12. **ID Protection for agents — a formal detection-to-response workflow, not a replacement for the kill switch:** Point 10 establishes the manual, tested kill switch. Microsoft Entra ID Protection for agents (Preview; Entra ID P2 during the preview, and Learn says it will require a Microsoft Agent 365 license "starting soon") adds an automated *front end* to that same decision, but it is a detection layer, not a shutdown mechanism on its own — the distinction matters for how you document it in the governance registry. ID Protection continuously evaluates eight offline risk detection types against agent identities: confirmed compromised (admin-flagged), early-life malicious activity, Entra directory reconnaissance, failed access attempts, sign-in spikes, suspicious credential usage on a blueprint, unfamiliar resource access, and matches against Microsoft threat intelligence. Two limits matter for the registry: a **learning mode** suppresses behavioral alerts for agents with little activity history (a separate detection still catches malicious early-life behavior), and in on-behalf-of flows the risk is attributed to the user rather than the agent, so these detections only describe autonomous agents. Detections are retained for 90 days. "Offline" means these are computed after the fact, not blocked in real time by ID Protection itself — the blocking, if any, happens downstream in Conditional Access.

    **The response sequence Microsoft documents, and where it actually stops:** (1) *Detect* — review the Risky Agents report in the Entra admin center; detections are retained 90 days. (2) *Respond* — an admin selects **Confirm compromise** (sets risk to High and logs the event) or **Disable** (blocks all sign-in immediately, across Entra ID and connected apps). (3) *Investigate* — sign-in logs, audit logs, blast radius. (4) *Recover* — dismiss and re-enable if false positive; rotate credentials before re-enabling, or retire the identity, if the compromise is real.

    **The gap to state explicitly in the lab, because it is the one teams miss:** "Confirm compromise" only sets the risk level and logs the event. It does **not** block anything by itself. Blocking happens only if a separate Conditional Access policy exists with **Agent risk (Preview)** as a condition, scoped to High, with grant = Block (Microsoft ships a ready-made template for this at `aka.ms/CreateAgentRiskPolicy`). Without that policy wired up, an admin can click "Confirm compromise," watch the risk badge turn red, and the agent keeps authenticating normally — the record says compromised, the resource still says yes. This is the same failure mode as an untested kill switch (point 10): a control that exists in the interface and not in the enforcement path. And even with the CA policy in place, Confirm-compromise-triggered blocking only stops **new** token issuance — it does not revoke tokens already handed out, and Graph has no session-revocation call for a service principal or an agent identity. An access token already issued stays valid until it expires (60 to 90 minutes by default); Continuous Access Evaluation for workload identities rejects it on disable or high risk, for Microsoft Graph only. State that residual window in the registry (point 10).

    **Programmatic access for SOC integration:** the Microsoft Graph `identityProtection` resource exposes two collections — `riskyAgents` (three subtypes: `riskyAgentIdentity`, `riskyAgentIdentityBlueprintPrincipal`, `riskyAgentUser`) and `agentRiskDetections`, both queryable and actionable (`dismiss`, `confirmCompromised`, `confirmSafe`) via the Graph beta API. Export risk data continuously to your SIEM via Entra ID diagnostic settings (enable the categories `RiskyAgents` and `AgentRiskEvents`; the category names are not the table names), routed to the same Log Analytics workspace or Sentinel instance the KQL Library already queries — this is how "Confirm compromise" clicked in the Entra admin center becomes a queryable, correlatable event next to the P02 governance-gap findings, instead of living only in a separate portal. The exported tables are `AADRiskyAgents` and `AADAgentRiskEvents` (Azure Monitor reference); P03-Q14 queries the second. Microsoft Learn does not say whether these detections raise an incident or alert in Defender XDR: check in your tenant, and plan a custom rule if they do not. Reference: [Identity Protection for agents](https://learn.microsoft.com/entra/id-protection/concept-risky-agents); [Manage agent identities — detect and remediate agent risk](https://learn.microsoft.com/entra/agent-id/manage-agent-identities-admin#detect-and-remediate-agent-risk); [riskyAgent resource type](https://learn.microsoft.com/graph/api/resources/riskyagent?view=graph-rest-beta) (Microsoft Graph beta).

    ```mermaid
    flowchart TB
        subgraph DET["Detect"]
            D1["ID Protection evaluates eight offline detection types on agent identities<br/>learning mode suppresses behavioral alerts for agents with little history"]
            D2["Risky Agents report<br/>detections kept 90 days"]
        end
        subgraph RESP["Respond"]
            R1["Confirm compromise<br/>sets the risk to High and logs the event"]
            R2["Disable<br/>blocks all sign-in immediately"]
        end
        Q{"Conditional Access policy exists:<br/>Agent risk High, grant Block?"}
        N["New token requests are blocked"]
        X["Nothing is blocked<br/>the record says compromised,<br/>the resource still says yes"]
        T["Tokens already issued stay valid until they expire<br/>60 to 90 minutes by default<br/>CAE rejects them for Microsoft Graph only"]
        S["Export to the SIEM: AADRiskyAgents and AADAgentRiskEvents<br/>queried by P03-Q14"]
        D1 --> D2
        D2 --> R1
        D2 --> R2
        R1 --> Q
        Q -->|"yes"| N --> T
        Q -->|"no"| X
        R2 --> T
        D1 -.-> S

        classDef blue fill:#0078D4,stroke:#333,color:#fff
        classDef purple fill:#5E2750,stroke:#333,color:#fff
        classDef green fill:#107C10,stroke:#333,color:#fff
        classDef orange fill:#FF8C00,stroke:#333,color:#24292f
        class D1,D2 blue
        class R1,R2,Q purple
        class N green
        class X,T orange
        class S blue
    ```

    **How to read it.** Detection and response are separate steps, and the decision in the middle is the one teams miss. Confirm compromise only sets the risk to High: it blocks new token requests only when a Conditional Access policy with the Agent risk condition and the Block control exists. Even then, a token already issued stays valid until it expires, so state that residual window in the registry (point 10).

13. **Roles and default ownership on Agent ID objects: the people who can manage them are part of the control plane.** Three Entra roles carry most of the lifecycle (Microsoft Learn). **Agent ID Administrator** manages agent identities, blueprints, blueprint principals, and agents' user accounts; Learn's create-blueprint page names it as the role needed to add a secret or certificate credential to a blueprint, and the permissions reference also lists the privileged action `agentIdentityBlueprints/credentials/update` under AI Administrator, so treat both roles as able to add credentials. **Agent ID Developer** creates blueprints and configures federated identity credentials on them, and the creator is automatically set as owner of both the blueprint and its principal. **AI Administrator** can also create agent identities, and Learn's permissions reference lists the agent identity, blueprint, blueprint principal, and agent user actions under it; Learn labels it a privileged role, so protect it like the others: PIM activation, phishing-resistant authentication, and secure admin workstations. **Ownership is the quiet path:** by default any member can manage the properties, assignments, and credentials of the blueprints, blueprint principals, and agent identities they own, can create agent identities when they own the blueprint principal, and can create blueprint principals when they own the blueprint (Learn, default user permissions). Because creators become owners automatically and owners act without holding an Agent ID role, ownership outlasts the role assignment or PIM activation used to create the object (our reading of those two Learn statements). Prefer sponsors for accountability, PIM-governed roles for technical management, and audit owners the way you audit role assignments (P03-Q12 shows owner and sponsor changes). **Scoping is thin today:** agent identities, blueprints, and blueprint principals cannot be added to administrative units (Learn FAQ). **What agents themselves can hold:** Microsoft blocks Global Administrator, Privileged Role Administrator, and User Administrator for agent identities and keeps them out of role-assignable groups (Learn FAQ), but a role that is not labeled privileged can still be assigned, so read the actions of any role before giving it to an agent. Reference: [Create an agent identity blueprint](https://learn.microsoft.com/entra/agent-id/create-blueprint); [Administrative relationships](https://learn.microsoft.com/entra/agent-id/agent-owners-sponsors-managers); [Default user permissions](https://learn.microsoft.com/entra/fundamentals/users-default-permissions).

    ```mermaid
    flowchart TB
        subgraph ROLE["Path 1: an Entra role"]
            R1["Agent ID Administrator and AI Administrator<br/>both can add credentials<br/>privileged: PIM, phishing-resistant authentication, secure workstation"]
            R2["Agent ID Developer<br/>creates blueprints and configures<br/>federated identity credentials on them"]
        end
        subgraph OBJ["Agent ID objects"]
            BP["Blueprint and blueprint principal<br/>credentials live here"]
            AI["Agent identity"]
            AU["Agent user account"]
        end
        subgraph OWNP["Path 2: ownership, the quiet path"]
            OW["Owner<br/>acts without holding an Agent ID role"]
        end
        KEEP["Ownership outlasts the role assignment<br/>or the PIM activation used to create the object"]
        CTRL["Controls: sponsors for accountability,<br/>PIM-governed roles for technical management,<br/>audit owners like role assignments (P03-Q12)"]
        R1 -->|"manage agent identities, blueprints,<br/>blueprint principals and agent users"| OBJ
        R2 -->|"creates blueprints"| OBJ
        R2 -->|"the creator becomes owner<br/>of the blueprint and its principal"| OW
        OW -->|"manages properties, assignments and credentials of what it owns<br/>creates agent identities and blueprint principals"| OBJ
        OW -.-> KEEP
        KEEP -.-> CTRL

        classDef blue fill:#0078D4,stroke:#333,color:#fff
        classDef purple fill:#5E2750,stroke:#333,color:#fff
        classDef green fill:#107C10,stroke:#333,color:#fff
        classDef orange fill:#FF8C00,stroke:#333,color:#24292f
        class R1,R2 purple
        class BP,AI,AU blue
        class OW,KEEP orange
        class CTRL green
    ```

    **How to read it.** Two paths reach the same objects. The role path shows up in PIM and role assignment reviews. The ownership path does not: the creator becomes owner automatically, and an owner acts without holding any Agent ID role, so ownership outlasts the role assignment or PIM activation used to create the object (our reading of two Learn statements). Audit owners the way you audit role assignments.

---

**Exercise / Lab:**

- **Name:** Governance model implementation in demo tenant
- **Format:** Individual
- **Description:**
  1. In Entra ID → App registrations, create `demo-sales-agent` with `Sites.Read.All` permission and mark it as an Entra Agent ID in the manifest (`"tags": ["agent365", "EntraAgentID"]`)
  2. In Copilot Studio, publish a test agent to the Teams and Microsoft Copilot channel; in the Microsoft 365 admin center → Agents → All agents → Requests, review it and publish or reject it (AI Administrator or Global Administrator role)
  3. In Power Platform admin center, create the DLP policy "Agentic AI — Restrict External Connectors" blocking HTTP and HTTP with Azure AD
  4. Run the governance queries from the KQL Library (P02-Governance-Gaps.kql): agents without Entra Agent ID, Copilot Studio agents published or shared, graph drift
  5. **Kill switch drill:** on the `demo-sales-agent` created in step 1, execute the three-level shutdown and time each one: (a) L1 mark it compromised with `POST /identityProtection/riskyAgents/confirmCompromised` (and `POST /users/{id}/revokeSignInSessions` if the agent has a user account), then check in the Risky agents report that the risk is High; (b) L2 disable the identity in Entra ID → Enterprise applications → Properties → Enabled for users to sign-in = No, then watch the sign-in logs until the agent's requests fail with `ResultType` 7000112 (AADSTS7000112) and note how long a token already issued kept working; (c) L3 quarantine or unpublish the agent in Copilot Studio. Record the total time from decision to confirmed stop, and who had to intervene at each level
  6. Complete the "Domain 2 — Govern" section of the Gap Assessment Template with real findings from the demo tenant
- **Required tools:** Entra ID (App registrations + Manifest editor + Enterprise applications), Copilot Studio, Microsoft 365 admin center (Agents), Power Platform admin center, Microsoft Graph Explorer, Microsoft Sentinel (Logs), KQL Library P02, Gap Assessment Template
- **Deliverable:** Entra Agent ID created and verified in Agent 365 Registry + documented kill switch procedure with measured RTO + Domain 2 section of the Gap Assessment completed with identified gaps, assigned owners, and target dates

---

**Closing questions for the facilitator:**
- When running the query for agents without an Entra Agent ID, what percentage of the total agent count appeared in that result? What process in your organization would have registered them correctly?
- If you had to implement the governance model designed today in production, what would be the first organizational (non-technical) obstacle you would encounter?

**Connection to the next domain:** Governance defines who approves an agent and what process it follows. Domain 3 takes those approved identities and defines what they can access — verifiable least privilege, CA policies specific to agents, and how to audit OAuth consent drift before it escalates.

→ [Module 03 — Secure Access](./Module-03-SecureAccess.md)
