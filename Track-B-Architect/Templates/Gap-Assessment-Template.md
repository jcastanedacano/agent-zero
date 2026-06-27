# Agentic AI Security Gap Assessment

**Organization:** [ORGANIZATION NAME]  
**Assessment date:** [DATE]  
**Completed by:** [NAME / ROLE]  
**Reviewer:** [NAME / ROLE]  
**Framework version:** Agentic AI Security Labs v1.0

---

## How to Use This Template

Complete one section per security domain during the Track B workshop. For each domain:

1. Mark current state (what exists today)
2. Identify the gap (delta between current and target)
3. Assign an owner and a target date
4. Estimate effort (S = < 1 week, M = 1–4 weeks, L = > 1 month)

This document is the primary deliverable of the Track B workshop. Share it with your SOC team before scheduling Track C.

---

## Domain 1 — Discover: Agent Inventory & Visibility

### Current State

| Question | Answer |
|----------|--------|
| Do you have a current inventory of all AI agents in your tenant? | ☐ Yes / ☐ No / ☐ Partial |
| Which platforms are agents deployed on? | ☐ Copilot Studio ☐ Azure AI Foundry ☐ Power Automate ☐ Agent Builder ☐ Third-party ☐ Unknown |
| Is Defender AI Agent Inventory enabled? | ☐ Yes / ☐ No |
| Is Microsoft Purview DSPM for AI enabled? | ☐ Yes / ☐ No |
| Are endpoint agents (local/MCP) tracked? | ☐ Yes / ☐ No / ☐ Not applicable |
| Estimated number of active agents: | |

### Gap Analysis

| Gap | Severity | Owner | Target Date | Effort |
|-----|----------|-------|-------------|--------|
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |

### Architecture Notes

> Document your current agent discovery topology here — data flow, telemetry sources, blind spots.

---

## Domain 2 — Govern: Identity, Approval & Lifecycle

### Current State

| Question | Answer |
|----------|--------|
| Are agents registered with Entra Agent ID? | ☐ All ☐ Some ☐ None |
| Is there an approval process before agents go to production? | ☐ Yes ☐ No ☐ Informal |
| Is Copilot Studio agent approval flow enabled? | ☐ Yes / ☐ No |
| Do agents have a designated technical owner? | ☐ All ☐ Some ☐ None |
| Is there a lifecycle process for decommissioning agents? | ☐ Yes / ☐ No / ☐ In progress |
| Are Power Platform DLP policies configured for AI connectors? | ☐ Yes / ☐ No |
| Known Agent Builder bypass instances: | |

### Gap Analysis

| Gap | Severity | Owner | Target Date | Effort |
|-----|----------|-------|-------------|--------|
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |

### Architecture Notes

> Document your agent governance model: who approves, what's the SLA, how are orphaned agents detected.

---

## Domain 3 — Secure Access: Identity & Least Privilege

### Current State

| Question | Answer |
|----------|--------|
| Are agent identities using managed identities (vs. stored secrets)? | ☐ All ☐ Some ☐ None |
| Are Conditional Access policies applied to agent service principals? | ☐ Yes / ☐ No / ☐ Partial |
| Are OAuth permissions reviewed at the time of consent? | ☐ Yes / ☐ No |
| Is PIM (Privileged Identity Management) used for agent roles? | ☐ Yes / ☐ No / ☐ In evaluation |
| Are secrets stored in Key Vault (not in code or environment variables)? | ☐ All ☐ Some ☐ None |
| Network isolation in place for agent compute? | ☐ Yes / ☐ No |

### Known Misconfiguration Patterns

- [ ] `grantControls: mfa` applied to agent CA policy (invalid for non-human identities — must use `block`)
- [ ] Service principals with `Directory.ReadWrite.All` or `Mail.ReadWrite` without justification
- [ ] Client secret expiring within 30 days with no rotation plan
- [ ] Agent using user-delegated permissions instead of application permissions

### Gap Analysis

| Gap | Severity | Owner | Target Date | Effort |
|-----|----------|-------|-------------|--------|
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |

### Architecture Notes

> Document your identity model for agents: managed vs. app registration, secret rotation process, CA policy scope.

---

## Domain 4 — Protect Data: DLP & Information Barriers

### Current State

| Question | Answer |
|----------|--------|
| Are sensitivity labels applied to SharePoint sites used as agent knowledge sources? | ☐ All ☐ Some ☐ None |
| Is Purview DLP configured to cover AI interactions? | ☐ Yes / ☐ No |
| Are information barriers configured for sensitive agent deployments? | ☐ Yes / ☐ No / ☐ Not applicable |
| Is DSPM for AI monitoring agent-accessed content? | ☐ Yes / ☐ No |
| Are agent outputs (responses) scanned for sensitive data before delivery? | ☐ Yes / ☐ No |

### Oversharing Risk Inventory

List SharePoint sites currently used (or planned) as agent knowledge sources:

| Site URL | Sensitivity Label | Agent Retrieval Enabled | Oversharing Risk | Action |
|----------|-------------------|------------------------|-----------------|--------|
| | ☐ Yes / ☐ None | ☐ Yes / ☐ No | ☐ High ☐ Med ☐ Low | |
| | ☐ Yes / ☐ None | ☐ Yes / ☐ No | ☐ High ☐ Med ☐ Low | |
| | ☐ Yes / ☐ None | ☐ Yes / ☐ No | ☐ High ☐ Med ☐ Low | |

> **Remediation order matters:** Apply sensitivity labels and remediate ACL errors **before** enabling agent retrieval. Reversing this order creates a live exposure window.

### Gap Analysis

| Gap | Severity | Owner | Target Date | Effort |
|-----|----------|-------|-------------|--------|
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |

### Architecture Notes

> Document your data classification model as it applies to agent-accessible content.

---

## Domain 5 — Detect & Respond: Monitoring & Incident Response

### Current State

| Question | Answer |
|----------|--------|
| Are Sentinel analytics rules in place for agentic AI threats? | ☐ Yes ☐ No ☐ Partial |
| Is there a defined incident response process for agent-related incidents? | ☐ Yes / ☐ No / ☐ In progress |
| Is automated enforcement (Logic App / playbook) configured? | ☐ Yes / ☐ No |
| Is jailbreak detection enabled? | ☐ Yes / ☐ No |
| Are agent-related alerts routed to the correct SOC queue? | ☐ Yes / ☐ No / ☐ Unknown |
| Mean time to detect (MTTD) for agent anomalies: | |
| Mean time to respond (MTTR) for agent incidents: | |

### Analytics Rules Inventory

| Threat | Rule Exists | Severity | Table | Frequency | Automated Response |
|--------|-------------|----------|-------|-----------|-------------------|
| New unmanaged agent | ☐ Yes / ☐ No | | | | |
| Jailbreak attempt | ☐ Yes / ☐ No | | | | |
| Data exfiltration via connector | ☐ Yes / ☐ No | | | | |
| OAuth consent outside review | ☐ Yes / ☐ No | | | | |
| Agent activity off-hours | ☐ Yes / ☐ No | | | | |

### Gap Analysis

| Gap | Severity | Owner | Target Date | Effort |
|-----|----------|-------|-------------|--------|
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |
| | ☐ High ☐ Med ☐ Low | | | ☐ S ☐ M ☐ L |

### Architecture Notes

> Document your detection architecture: data sources → Sentinel → triage → enforcement.

---

## Consolidated Remediation Roadmap

### Immediate (0–30 days)

| Action | Domain | Owner | Status |
|--------|--------|-------|--------|
| | | | ☐ Not started |
| | | | ☐ Not started |
| | | | ☐ Not started |

### Short-term (30–90 days)

| Action | Domain | Owner | Status |
|--------|--------|-------|--------|
| | | | ☐ Not started |
| | | | ☐ Not started |
| | | | ☐ Not started |

### Strategic (90+ days)

| Action | Domain | Owner | Status |
|--------|--------|-------|--------|
| | | | ☐ Not started |
| | | | ☐ Not started |

---

## Assessment Summary

| Domain | Current Maturity | Target Maturity | Critical Gaps | Total Gaps |
|--------|-----------------|-----------------|---------------|------------|
| 01 Discover | ☐ Initial ☐ Developing ☐ Defined ☐ Managed | | | |
| 02 Govern | ☐ Initial ☐ Developing ☐ Defined ☐ Managed | | | |
| 03 Secure Access | ☐ Initial ☐ Developing ☐ Defined ☐ Managed | | | |
| 04 Protect Data | ☐ Initial ☐ Developing ☐ Defined ☐ Managed | | | |
| 05 Detect & Respond | ☐ Initial ☐ Developing ☐ Defined ☐ Managed | | | |

**Recommended next step:** Schedule Track C (SOC Engineer workshop) to operationalize the detection and response gaps identified in Domain 5.

→ [Track C — SOC Engineer Workshop](../../Track-C-SOC-Engineer/README.md)
