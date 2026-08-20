---
name: detect-respond-playbook-agent-containment
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Incident response playbook to contain a compromised AI agent, including
  immediate agent suspension, revocation of active tokens, preservation of
  forensic evidence, and notification to the security team, orchestrated
  via a Logic App linked to Sentinel analytics rules.
tags: [detect, respond, sentinel, playbook, logic-app, containment, incident-response, aisoc]
atlas_techniques: [AML.T0051, AML.T0048, AML.T0046]
d3fend_techniques: [D3-OTA, D3-RTA, D3-ANET]
nist_ai_rmf: [MANAGE-3.2, MANAGE-4.1]
nist_csf: [RS.RP-01, RS.CO-02, RS.MI-01]
ms_license: [Microsoft Sentinel, Azure Logic Apps]
ms_roles: [Microsoft Sentinel Contributor, Logic Apps Contributor]
effort_hours: 8
---

## When to use

- As a playbook attached to any Pillar 5 analytics rule
- Trigger manually when a compromised agent is confirmed
- Automate for High and Critical severity incidents

## Playbook phases

```
Detection → Triage → Containment → Preservation → Notification → Remediation
```

This skill covers the first four phases (automatable).
Remediation requires human review.

## Containment actions by severity

| Severity | Automatic action | Requires approval |
|---|---|---|
| Low | Enrich incident + notify | No |
| Medium | Suspend agent + notify + open ticket | No |
| High | Suspend agent + revoke tokens + notify | Yes (for steps 3+) |
| Critical | Block SP + revoke tokens + notify + escalate | Yes |

## Workflow

### Step 1 — Create the Logic App in Azure

```bash
# Create the Logic App in {workspace-name}
az logic workflow create \
  --resource-group {resource-group} \
  --location centralus \
  --name "la-aisoc-agent-containment" \
  --definition @containment-definition.json
```

### Step 2 — Trigger: Sentinel incident creation

The trigger is `When a Microsoft Sentinel incident is created or updated`
filtered on `Tactics contains AML.T0051 OR AML.T0046` or on the rule name.

### Step 3 — Action 1: Enrich the incident with agent data

```http
# Get the involved agent's SP details
GET https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}
  ?$select=displayName,appId,createdDateTime,tags,owners

# Get recent activity (last 8h)
GET https://graph.microsoft.com/v1.0/auditLogs/signIns
  ?$filter=appId eq '{app-id}' and createdDateTime ge {8h-ago}
  &$top=50
```

Add the result as a comment on the Sentinel incident.

### Step 4 — Action 2: Suspend the agent in Copilot Studio (if applicable)

Via Power Platform API:
```http
POST https://api.powerplatform.com/appmanagement/environments/{env-id}/bots/{bot-id}/disable
Authorization: Bearer {token}
```

Or via Graph if it is an M365 Copilot app:
```http
PATCH https://graph.microsoft.com/v1.0/applications/{app-object-id}
{
  "disabledByMicrosoftStatus": "DisabledDueToViolation"
}
```

### Step 5 — Action 3: Revoke all of the SP's active tokens

```http
POST https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/revokeSignInSessions
```

This invalidates every current access token and refresh token.

### Step 6 — Action 4: Block the SP in Entra ID (Critical only)

```http
PATCH https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}
{
  "accountEnabled": false
}
```

### Step 7 — Action 5: Preserve forensic evidence

Export to a Storage Account before the logs expire:

```kql
// Run and export via Sentinel → Logs → Export
union CopilotStudio_CL, FoundryAgents_CL, AADServicePrincipalSignInLogs, AuditLogs
| where TimeGenerated > ago(72h)
| where ServicePrincipalName == "{agent-sp-name}"
    or AgentName_s == "{agent-name}"
| extend ForensicCase = "AISOC-{incident-id}"
```

### Step 8 — Action 6: Notification

```
Teams webhook → AISOC-Alerts channel:
"🚨 COMPROMISED AGENT CONTAINED
Agent: {agent-name}
Incident: {incident-id} | Severity: {severity}
Actions taken: Suspended, tokens revoked
Requires human review: [link]"
```

### Step 9 — Configure human approval for Critical

For Critical incidents, insert an approval action before `accountEnabled: false`:

```
Logic App → Add action → Approvals → Start and wait for an approval
→ Approvers: security-team@{tenant}
→ Timeout: 4 hours
→ On reject: notify only, do not block the SP
```

## Verification

- [ ] Logic App deployed and in Running state
- [ ] Trigger correctly connected to Sentinel
- [ ] Test: create a manual incident and verify the Logic App runs
- [ ] Enrichment appears as a comment on the Sentinel incident
- [ ] `revokeSignInSessions` runs with no errors (verify in the Graph API response)
- [ ] Notification reaches the Teams AISOC-Alerts channel
- [ ] Containment action log available in the Logic App run history

## Implementation notes

- The Logic App needs a managed identity with the following roles assigned: `Application.ReadWrite.All` on Graph API
- The Power Platform Admin API requires a separate service token to disable Copilot Studio agents — it cannot be reused
- For the notification channel: create a dedicated Teams channel for AISOC alerts before deploying the playbook
- Preserve forensic evidence in a storage account with a minimum 90-day retention before revoking tokens — revocation removes the ability to audit active sessions
