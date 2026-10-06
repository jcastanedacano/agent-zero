# Module 03 — Secure Access | Track A

**Module duration:** 45 minutes

**Learning objective:**
By the end of this module, participants will be able to explain why access policies designed for human users do not apply directly to AI agents, evaluate the risk of inherited configurations in their environment, and make investment decisions on agent identity controls in the context of an enterprise Conditional Access strategy.

**Module agenda:**

| Time | Activity | Type |
|------|----------|------|
| 10 min | Agent identity vs. human identity: why policy inheritance creates false security | Presentation |
| 10 min | Risk vectors: inherited CA, excessive permissions, uncontrolled OAuth, identity laundering | Presentation |
| 20 min | Exercise: Decision scenario — Agentic access crisis | Roleplay |
| 5 min | Wrap-up and connection to Domain 4 | Discussion |

---

**Core content (points the facilitator must cover):**

1. **The MFA assumption for agents:** Conditional Access policies that require MFA for human users do not cover agents: an agent cannot complete interactive MFA, and Microsoft Learn documents Block as the only access control for agent identities. An organization that relies on its user MFA policy has no policy on its agents. The result is a false sense of security, and the fix is a separate policy for agents.

2. **Verifiable least privilege:** Agents accumulate permissions without a systematic review process. Uncontrolled OAuth consent allows an agent to obtain `Mail.ReadWrite` without any administrator explicitly approving it. The gap is not one of intent — it is one of process.

3. **Applicable Microsoft controls:** Entra CA for Agents enables policies specific to agent identities, through the Agents assignment. Entra ID Protection detects anomalous service principal behavior. PIM just-in-time limits the exposure window for elevated permissions. Defender for Cloud Apps audits connected application behavior.

4. **Identity laundering as a risk vector:** An agent can operate under a human user's delegated identity, executing actions that appear in logs as performed by the person. Without a separate agent identity (Entra Agent ID), forensic traceability is impossible.

---

**Exercise:**

- **Name:** Agentic access crisis
- **Format:** Groups of 3–4
- **Description:**
  1. Facilitator presents the scenario: "A sales agent deployed three months ago starts accessing HR folders in SharePoint. Logs show the activity under the Sales Director's name, who states they did not initiate those actions."
  2. Each team has 8 minutes to answer: how did you detect it (or why didn't you detect it earlier)? Who is accountable?
  3. The team must decide: revoke agent access immediately or investigate first? How do you revoke if you don't know exactly what permissions it has?
  4. Each team presents their decision in 2 minutes and justifies it
  5. Facilitator reveals which Domain 03 controls would have prevented or accelerated detection
- **Required tools:** Scenario description (printed or projected); cards with the Domain 03 available controls
- **Deliverable:** Decision documented per team: what they did, who was accountable, and what control they would have needed to respond faster. Added to the Risk Posture Map.

---

**Closing questions for the facilitator:**
- In the scenario presented, how long would it take your organization to identify that it was an agent and not the Sales Director who performed those actions? What process would make that possible?
- Which risk posture is more acceptable: blocking agent access until the identity is confirmed, or keeping it active while investigating? What factors in your organization determine that decision?

**Connection to the next domain:** Controlling who has access is not sufficient if the data the agent can read is not classified or protected. Domain 4 covers data protection: how to prevent an agent with legitimate access from becoming an exfiltration vector.

→ [Module 04 — Protect Data](./Module-04-ProtectData.md)
