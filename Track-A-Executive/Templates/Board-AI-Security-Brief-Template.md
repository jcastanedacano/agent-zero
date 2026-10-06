# Board AI Security Brief — Template

**Organization:** [ORGANIZATION NAME]  
**Prepared by:** [CISO / Security Lead]  
**Review date:** [DATE]  
**Next review:** [DATE + 90 days]  
**Classification:** Board Confidential

---

## Executive Summary (1 page — stop here for board briefing)

### Current AI Security Posture

| Domain | Status | Trend |
|--------|--------|-------|
| Agent Visibility | 🔴 At Risk / 🟡 Improving / 🟢 Managed | ↑ ↓ → |
| Governance & Control | 🔴 At Risk / 🟡 Improving / 🟢 Managed | ↑ ↓ → |
| Identity & Access | 🔴 At Risk / 🟡 Improving / 🟢 Managed | ↑ ↓ → |
| Data Protection | 🔴 At Risk / 🟡 Improving / 🟢 Managed | ↑ ↓ → |
| Detection & Response | 🔴 At Risk / 🟡 Improving / 🟢 Managed | ↑ ↓ → |
| Regulatory Compliance | 🔴 At Risk / 🟡 Improving / 🟢 Managed | ↑ ↓ → |
| Third-Party AI Risk | 🔴 At Risk / 🟡 Improving / 🟢 Managed | ↑ ↓ → |

### Three decisions requested from the board

| # | Decision | Business impact | Risk if deferred |
|---|---------|----------------|-----------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### AI agent landscape (as of [DATE])

| Metric | Value | Change vs. last quarter |
|--------|-------|------------------------|
| Total AI agents in tenant | | |
| Agents without approved owner | | |
| Agents without Entra identity | | |
| External AI vendors connected | | |
| Open security incidents (AI-related) | | |

---

## Section 1 — Business Context

### Why AI agents require board-level attention

AI agents differ from traditional software in three ways that affect board risk oversight:

1. **Autonomous action at machine speed:** Agents can draft emails, read files, send messages, and call external services without human approval — in milliseconds. A compromised agent can cause damage faster than any human attacker.

2. **Accumulated permissions without review:** Agents accumulate OAuth permissions over time. Unlike users (who leave the organization), agents persist indefinitely unless explicitly decommissioned. An agent created 18 months ago may have permissions that no longer reflect current business need.

3. **Regulatory exposure is now quantified:** The EU AI Act imposes fines of up to €30M or 6% of global annual turnover for high-risk AI non-compliance. ISO 42001 certification is becoming a customer and partner requirement. The risk is no longer hypothetical.

### AI adoption in our organization

[Describe: which business units are deploying AI agents, which use cases, what data they access, which external services they connect to. This section should be 2-3 sentences maximum for a board audience.]

---

## Section 2 — Key Risks (Board-level)

### Risk 1 — Shadow AI

**What it is:** Any employee with a Microsoft 365 Copilot license can create and publish an AI agent in minutes, without IT approval or security review. These agents have full access to the same SharePoint, email, and Teams data as the user who created them.

**Current exposure:** [X] agents detected in tenant without approved owner or formal security review.

**Regulatory implication:** EU AI Act Article 9 requires a risk management system for all AI systems. Undocumented agents violate this requirement.

**Proposed control:** Copilot Studio approval flow + Conditional Access policy (estimated implementation: 2 weeks, no additional license cost).

---

### Risk 2 — Third-Party AI Supply Chain

**What it is:** AI agents can connect to external Model Context Protocol (MCP) servers — third-party tools that extend agent capabilities. When connected, these servers can execute code and access data in the context of the agent's permissions. If a vendor is compromised, attackers can inject malicious instructions into our agents' tool responses.

**Current exposure:** [X] agents have active external MCP server connections. [Y] of these have no vendor security assessment on file.

**Regulatory implication:** EU AI Act Article 25, NIST AI RMF GOVERN-5.1, ISO 42001 Clause 8.6 all require documented third-party AI risk management.

**Proposed control:** Vendor assessment process (22-question checklist) + Power Platform DLP policy to block unapproved external connectors.

---

### Risk 3 — Data Exfiltration via AI

**What it is:** An AI agent with access to sensitive SharePoint content and an external email or webhook connector can be instructed — via a manipulated document or malicious user prompt — to forward sensitive data to an attacker-controlled destination. This is AI-enabled data exfiltration using legitimate business tools.

**Current exposure:** [X] SharePoint sites accessed by agents have no sensitivity labels, meaning Purview DLP policies do not apply to their content when retrieved by agents.

**Regulatory implication:** GDPR Article 32 requires technical measures to ensure data security. An agent exfiltrating personal data through a legitimate connector would constitute a data breach.

**Proposed control:** Microsoft Purview DLP for AI interactions + sensitivity labels on all SharePoint sites used as agent knowledge sources (estimated: 4-6 weeks for full labeling).

---

## Section 3 — Regulatory Status

### EU AI Act

| Agent deployment | Risk tier | Compliance status | Gap |
|-----------------|-----------|------------------|-----|
| [Agent name] | Limited / High / Minimal | ☐ Compliant ☐ Gap | |
| [Agent name] | Limited / High / Minimal | ☐ Compliant ☐ Gap | |

**Next deadline:** EU AI Act prohibited uses enforcement began February 2025. High-risk system obligations apply from August 2026.

### NIST AI RMF

Overall maturity: [Initial / Repeatable / Defined / Managed / Optimizing]

**Least mature function:** [GOVERN / MAP / MEASURE / MANAGE]

### ISO 42001

Certification status: ☐ Pursuing ☐ Not applicable ☐ Certified (expires: [DATE])

---

## Section 4 — Incident Summary

### AI-related security incidents in the last quarter

| Incident | Date | Impact | Status |
|---------|------|--------|--------|
| | | | |

### Near-misses and detection events

| Event | Date | Detection method | Time to detect |
|-------|------|-----------------|----------------|
| | | | |

---

## Section 5 — 90-Day Roadmap

| Priority | Action | Owner | Target date | Cost |
|---------|--------|-------|-------------|------|
| 🔴 Critical | | | | |
| 🔴 Critical | | | | |
| 🟡 High | | | | |
| 🟡 High | | | | |
| 🟢 Medium | | | | |

---

## Appendix — Metrics Definitions

| Metric | Definition | Data source |
|--------|-----------|-------------|
| Agents without approved owner | `AgentsInfo` where `Owners` is null or empty | Defender XDR Advanced Hunting |
| Agents without Entra identity | `AgentsInfo` where `EntraAgentID` and `EntraBlueprintID` are both empty (report blueprint-only agents separately) | Defender XDR Advanced Hunting |
| External AI vendors connected | `AgentsInfo` where `McpServers` count > 0, distinct vendor domains | Defender XDR Advanced Hunting |
| Shadow AI agents | Agents without owner AND without any Entra identity (no agent identity, no blueprint) | Defender XDR Advanced Hunting |
| AI-related incidents | `SecurityIncident` where Title contains agent/copilot/AI | Microsoft Sentinel |
| Time to detect jailbreak | Minutes from a message flagged `JailbreakDetected` in `CopilotActivity` to `SecurityIncident` created | Microsoft Sentinel |
| Time to contain | Minutes from incident creation to the containment action (session revocation or identity disable) in the Logic App | Microsoft Sentinel automation |

---

## Notes for the Presenter

- **Keep the executive summary to 1 page.** Board members typically read 30 seconds per page.
- **Lead with business risk, not technology.** "An agent accessed 847 files containing personal data without a DLP policy" lands better than "we have a Purview DLP gap."
- **Tie every risk to a decision.** If you cannot tie a risk to a board decision, it belongs in an operational report, not a board brief.
- **Use the three-number rule:** Lead with the number of agents, the number at risk, and the number of incidents. Everything else is supporting evidence.
- **Regulatory fines are a board-level number.** €30M or 6% of global revenue gets attention. Use it once, contextually, not as an alarm.
