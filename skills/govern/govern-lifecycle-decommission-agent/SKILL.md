---
name: govern-lifecycle-decommission-agent
version: "1.0"
pillar: govern
subdomain: ms-copilot-studio
description: >-
  Manages the full lifecycle of AI agents from approval through
  decommission, including detection of orphaned agents with active access,
  permission revocation, and deletion of service principals in Entra ID.
tags: [govern, copilot-studio, entra, lifecycle, decommission, agent-hygiene]
atlas_techniques: [AML.T0040]
d3fend_techniques: [D3-UAP, D3-AM]
nist_ai_rmf: [GOVERN-1.4, MANAGE-4.1]
nist_csf: [PR.AA-01, ID.AM-01]
ms_license: [M365 E3, Power Platform]
ms_roles: [Power Platform Administrator, Application Administrator]
effort_hours: 4
---

## When to use

- Periodic (monthly/quarterly) audit of active agents
- When an employee who created an agent leaves the organization
- Post-project: agents created for temporary use cases
- Detection of agents with no activity in 30+ days that still have active connectors

## Prerequisites

- Pillar 1 agent list (with owner and creation date)
- Power Platform Admin Center access
- Graph API to revoke permissions in Entra ID
- An offboarding process that includes reviewing the departing employee's agents

## Workflow

### Step 1 — Identify decommission candidates

Criteria:
- No activity in the last 30 days (cross-reference with the KQL in `queries/`)
- Owner/creator no longer with the organization (verify in Entra)
- Original use case completed (verify with the business owner)
- The project it was associated with has ended

```kql
// See queries/sentinel-inactive-agents.kql
```

### Step 2 — Notify the owner and confirm

Before decommissioning, confirm with:
- The agent's direct owner
- The owner manager if the owner is no longer with the organization
- The use case's business owner

Response window: 5 business days. No response = proceed with decommission.

### Step 3 — Disable the agent in Copilot Studio

```
Copilot Studio → [Agent] → Settings → General → Status → Disabled
```

Or via the Power Platform Admin Center:
```
Environments → [Env] → Copilot Studio → Agents → [Agent] → Disable
```

Keep it disabled for 7 days before deleting (rollback window).

### Step 4 — Revoke OAuth consent grants in Entra ID

```http
# Get the service principal's consent grants
GET https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/oauth2PermissionGrants

# Revoke each grant
DELETE https://graph.microsoft.com/v1.0/oauth2PermissionGrants/{grant-id}
```

### Step 5 — Revoke app role assignments

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/appRoleAssignments

# For each assignment:
DELETE https://graph.microsoft.com/v1.0/servicePrincipals/{resource-sp-id}/appRoleAssignedTo/{assignment-id}
```

### Step 6 — Delete the service principal and app registration

```http
# Delete the service principal
DELETE https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}

# Delete the app registration (if applicable — confirm no other instances exist)
DELETE https://graph.microsoft.com/v1.0/applications/{app-object-id}
```

### Step 7 — Document in the governance registry

Record in the log:
- Decommission date
- Owner notified
- Reason
- Resources revoked
- Executed by

## Verification

- [ ] Agent in Disabled state (not Deleted) for 7 days
- [ ] OAuth consent grants revoked (GET returns an empty array)
- [ ] App role assignments revoked
- [ ] Service principal deleted (GET returns 404)
- [ ] Governance log entry created

## Implementation notes

- Do not delete production SPs during testing — use dedicated test agents to validate the decommission process
- Verify the SP is not shared with other applications before deleting it: `GET /servicePrincipals/{id}/appRoleAssignedTo` to see all assignments
- Graph API `DELETE /servicePrincipals/{id}` deletes the SP immediately — the process is irreversible; document state before proceeding
