# Agentic Incident Response Playbook

**Organization:** [ORGANIZATION NAME]  
**Tenant:** [TENANT ID / DOMAIN]  
**Assessment date:** [DATE]  
**Completed by:** [NAME / ROLE]  
**Framework version:** Agentic AI Security Labs v1.0

---

## How to Use This Template

Complete one section per module during the Track C workshop. Each section maps to a security domain and includes:
- Configuration evidence (screenshots, policy names, rule IDs)
- KQL queries deployed as Sentinel analytics rules
- Findings specific to your demo tenant
- Gaps to address in production

---

## Section 1: Agent Inventory Baseline
*Completed in Module 01 — Discover & Prioritize*

### Inventory Summary

| Metric | Demo Tenant | Production Estimate |
|--------|-------------|-------------------|
| Total agents detected | | |
| Unmanaged agents | | |
| Agents without technical owner | | |
| SharePoint sites accessed without labels | | |
| New agents registered in last 24h | | |

### Analytics Rules Deployed

- [ ] `New Unmanaged Agent Registered` — Frequency: 1h | Severity: Medium

### KQL Queries Reference

| Query | Table | Purpose |
|-------|-------|---------|
| Full agent inventory | `AgentsInfo` | Baseline visibility |
| Agents without owner | `AgentsInfo` | Identity orphan detection |
| SharePoint sites without labels | `OfficeActivity` + `MicrosoftPurviewInformationProtection` | Oversharing audit |
| New agent registrations | `AgentsInfo` | Shadow AI near-real-time detection |

### Top Findings

1.
2.
3.

---

## Section 2: Governance Gap Inventory
*Completed in Module 02 — Govern & Control*

### Configuration Deployed

| Control | Status | Notes |
|---------|--------|-------|
| Entra Agent ID (demo agent) | ☐ Created | App ID: |
| Copilot Studio approval flow | ☐ Enabled | |
| Power Platform DLP policy | ☐ Created | Policy name: |

### Known Gaps — Agent Builder Bypass

**Gap:** Agent Builder (M365 Copilot) activates agents immediately without passing through Copilot Studio Requests approval flow. By default every user can share an agent with the whole organization; an admin can restrict who can.

**Affected agents identified:**

| Agent Name | Created By | Creation Date | Approval Status |
|------------|-----------|---------------|-----------------|
| | | | Bypassed |

**Current mitigation options:**
- Restrict who can share agents with the organization in the Microsoft 365 admin center (all users is the default; specific users or groups, or no users). When sharing is restricted, an admin must approve and deploy the agent before others can use it (Microsoft Learn, Agent Builder)
- Detection: no audit operation for sharing an Agent Builder agent is documented, so there is no sharing alert to build. Check the agent in use in `CopilotActivity` (`AgentName`, `AgentId`; not verified on a live tenant) and search the Purview audit log for the maker and the time (see Module 06, Attack 2)
- Review agent submissions in the Microsoft 365 admin center (Agent Store requests); sharing an agent is not covered by that review
- Manual review process (document owner and responsible)

### Analytics Rules Deployed

- [ ] `Agents Without Entra Agent ID` — Frequency: daily | Severity: Medium
- [ ] `Copilot Studio Agents Created, Published or Shared` (P02-Q2, Copilot Studio only) — Frequency: daily | Severity: Medium
- [ ] `Permission Grants Without Approval Correlation` — Frequency: weekly | Severity: Medium

### Top Findings

1.
2.
3.

---

## Section 3: Access Control Configuration
*Completed in Module 03 — Secure Access*

### CA Policy Deployed

| Field | Value |
|-------|-------|
| Policy name | Agentic AI — Risk-Based Access Control |
| Targeted identities | [list service principals] |
| Condition | Service principal risk: Medium+ |
| Grant control | Block |
| Status | Report-only / Enforced |

### Critical Configuration Notes

> **`grantControls: mfa` is INVALID for agent identities.**  
> Applies to policies targeting `clientApplications.includeAgentIdServicePrincipals`.  
> For agents: use `block` or `sessionControls` only.  
> Confirmed invalid in What If test on [DATE]. See screenshot: [ATTACH]

### What If Validation Evidence

- [ ] Policy applies to `demo-sales-agent` with Medium risk: [screenshot]
- [ ] Policy does NOT apply to user accounts: [screenshot]

### Analytics Rules Deployed

- [ ] `OAuth High-Privilege Consent Without Review` — Frequency: weekly | Severity: High
- [ ] `Agent Sign-ins Outside Business Hours` — Frequency: daily | Severity: Medium
- [ ] `Agents Accessing Excessive Resource Scope` — Frequency: weekly | Severity: Medium

### Access Gap Findings

| Agent | Resources Accessed | Declared Scope | Gap |
|-------|--------------------|----------------|-----|
| | | | |

---

## Section 4: Data Protection Configuration
*Completed in Module 04 — Protect Data*

### DLP Policy Deployed

| Field | Value |
|-------|-------|
| Policy name | Agentic AI — Sensitive Data in AI Interactions |
| Workload | AI interactions (Microsoft 365 Copilot and other AI apps) |
| Rule | Credit card in agent prompt or response |
| Sensitive info type | Credit Card Number |
| Action | Block + notify + alert |
| Status | Test mode / Enforced |

### SharePoint Label Coverage Audit

| Site URL | Agent Knowledge Source | Sensitivity Label | Action Required |
|----------|----------------------|-------------------|-----------------|
| | ☐ Yes / ☐ No | None / [label name] | |

### Remediation Sequencing — CRITICAL

```
CORRECT ORDER:
1. Apply sensitivity labels to all SharePoint sites
2. Audit and remediate ACL errors (oversharing)
3. Enable agent retrieval on the site

INCORRECT ORDER (live exposure):
1. Enable agent retrieval
2. Apply labels after the fact
   → Agent has already indexed unlabeled content
   → All users can retrieve sensitive data through agent prompts
   → DLP fires reactively, not preventively
```

### Analytics Rules Deployed

- [ ] `DLP Matches in AI Interactions` — Frequency: daily | Severity: High
- [ ] `Agents Accessing Unlabeled Documents` — Frequency: weekly | Severity: Medium
- [ ] `External Connector Egress by Volume` — Frequency: daily | Severity: High
- [ ] `Prompt Injection Pattern Detection` — Frequency: hourly | Severity: Medium

### Top Exfiltration Risks Found

1.
2.
3.

---

## Section 5: Detection and Response
*Completed in Module 05 — Detect & Respond*

### Analytics Rules Deployed

| Rule Name | Severity | Frequency | Table | Status |
|-----------|----------|-----------|-------|--------|
| Agentic AI — Jailbreak Attempt Detected | High | 5 min | CloudAppEvents | ☐ Enabled |
| Agentic AI — Volume Spike Anomaly | Medium | 15 min | CloudAppEvents | ☐ Enabled |
| Agentic AI — Sensitive Data Access Off-Hours | High | 15 min | MicrosoftPurviewInformationProtection | ☐ Enabled |

### Automation Rule

| Field | Value |
|-------|-------|
| Rule name | Auto-revoke on Jailbreak Alert |
| Trigger | Alert name contains "Jailbreak" |
| Action | Run playbook: `playbook-revoke-agent-token` |
| Status | ☐ Enabled |

### Enforcement Flow

```
T+0     Jailbreak alert fires (Sentinel analytics rule)
T+0:02  Automation rule triggers Logic App
T+0:05  Token revoked via Graph API (POST /revokeSignInSessions)
T+0:05  Incident comment added in Sentinel (automated)
T+0:05  Email sent to agent technical owner
T+0:30  SOC analyst reviews incident, confirms revocation, closes or escalates
```

### Structural False Negative Audit

Run this query monthly and document results:

```kql
SecurityIncident
| where TimeGenerated > ago(30d)
| where Title has_any ("agent", "copilot", "AI", "jailbreak")
| summarize Count = count(), StatusSet = make_set(Status) by Title
| where not(StatusSet has "Closed") or Count > 3
```

| Alert Title | Fire Count | Ever Closed | Action Required |
|-------------|-----------|-------------|-----------------|
| | | | |

---

## Playbook Summary

| Domain | Controls Deployed | Analytics Rules | Key Gap |
|--------|------------------|-----------------|---------|
| 01 Discover | Defender AI Agent Inventory, Purview DSPM | 1 | Local agents without endpoint connector |
| 02 Govern | Entra Agent ID, Copilot Studio approval, Power Platform DLP | 3 | Agent Builder bypass |
| 03 Secure Access | CA policy (risk-based, block), What If validated | 3 | grantControls: mfa misconfiguration risk |
| 04 Protect Data | Purview DLP for AI interactions, label audit | 4 | Oversharing pre-existing before label remediation |
| 05 Detect & Respond | 3 analytics rules + Logic App enforcement | 3 | Structural false negatives in detection-only posture |
| 06 Red Team | 5 ATLAS attack exercises, detection gap analysis | — | [From red team findings] |

**Total analytics rules deployed:** 14  
**Enforcement playbooks deployed:** 1  
**Red team attacks executed:** [COUNT of 5 completed]  
**Detection gaps identified:** [COUNT]  
**Known gaps documented:** [COUNT]  
**Recommended next review:** [DATE + 90 days]
