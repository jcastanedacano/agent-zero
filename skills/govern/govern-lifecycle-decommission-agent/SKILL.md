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
ms_roles: [AI Administrator, Power Platform Administrator, Application Administrator]
effort_hours: 4
---

## When to use

- Periodic (monthly/quarterly) audit of active agents
- When an employee who created an agent leaves the organization
- Post-project: agents created for temporary use cases
- Detection of agents with no activity in 30+ days that still have active connectors

## Prerequisites

- Pillar 1 agent list (with owner and creation date)
- Microsoft 365 admin center (AI Administrator) and Power Platform admin center access
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

If the owner has left and the agent is still needed, reassign it instead: **Assign a new owner** in the Microsoft 365 admin center (Agents → All agents, for ownerless agents), or the
Power Platform API operation to reassign ownership of orphaned agents (Microsoft Learn).

### Step 3 — Block the agent (reversible)

Choose the control that matches the platform; all of them can be undone:

```
Microsoft 365 admin center → Agents → All agents → [Agent] → Block
```

Blocking an agent built with Agent Builder or Copilot Studio stops it in Microsoft Copilot and in other host products such as Outlook and Teams. Blocking a SharePoint or Foundry agent only
affects its availability in Microsoft Copilot Chat.

```
Power Platform admin center → Manage → Inventory (or Manage → Copilot Studio) → [Agent] → Block
```

Applies only to published agents; makers can still see and test the agent in Copilot Studio, but it cannot be used in any other channel. The same action through the Power Platform API:

```http
POST https://api.powerplatform.com/copilotstudio/environments/{environment-id}/bots/{bot-id}/api/botQuarantine/SetAsQuarantined?api-version=1
```

It takes a user token (Global, AI or Power Platform administrator, scope `CopilotStudio.AdminActions.Invoke`) and does not support classic chatbots (405). `SetAsUnquarantined` reverses it.

For a Microsoft Foundry agent, use **Stop** in the Microsoft 365 admin center (the **Azure AI Owner** role is required; it deallocates the Azure compute of the deployment) or **Block** in the Foundry Control Plane.

Keep it blocked or stopped for 7 days before deleting (rollback window). A delete in the Microsoft 365 admin center is also reversible: it is a soft delete with a 30-day recovery window.

### Step 4 — Revoke OAuth consent grants in Entra ID

Applies to agents that run on a service principal or an app registration. For an agent that has a Microsoft Entra Agent ID, deleting the agent also deletes its agent identity (Microsoft Learn,
Power Platform API agent deletion): capture the grants and role assignments (Steps 4 and 5) before the delete.

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

## Agent ID objects (blueprint, agent identities, agent users)

For agents that use Microsoft Entra Agent ID the objects form a chain: blueprint (an application), blueprint principal (a service principal),
agent identity (a service principal) and the agent's user account, paired 1:1 with an agent identity. From Microsoft Learn, *Agent identity deletion*:

- Disable before deleting. Disabling a blueprint principal or its agent identities stops authentication and leaves every object in place.
- Deleting a blueprint or its principal soft-deletes the child agent identities and agent users through an asynchronous cascade that can take hours or days.
  If you restore the blueprint principal before the cascade runs, the children are not affected; afterwards each child has to be restored one by one.
- Soft-deleted objects can be restored for 30 days, cannot authenticate, and keep counting toward directory quota. With app-only permissions a blueprint
  is limited to 250 agent identities, and deleting one frees a slot only when it is permanently deleted.
- In the audit log each cascade deletion appears as *Delete service principal*, initiated by the application "Delete Agent Identities Task" with no app ID.
  Exclude that actor from detections that watch deletions, and do not read it as an attacker.

## Verification

- [ ] Agent blocked, quarantined or stopped (not deleted) for 7 days
- [ ] OAuth consent grants revoked (GET returns an empty array)
- [ ] App role assignments revoked
- [ ] Service principal deleted (GET returns 404; restorable from the recycle bin for 30 days)
- [ ] Governance log entry created

## Implementation notes

- Do not delete production SPs during testing — use dedicated test agents to validate the decommission process
- The Power Platform API delete operation supports only Agent Builder agents; agents built in Copilot Studio need Power Platform environment admin permissions to delete (Microsoft Learn)
- Queries 1 and 3 returned no rows on the validation workspace (no inactive agent or account), Query 4 returned an agent identity, and Query 5 returned agents with a null owner id and no disabled owner account
- Removed in this version, because Microsoft Learn (Oct 2026) does not support them: the Copilot Studio path "Settings → General → Status → Disabled" and the Power Platform admin center path
  "Environments → [Env] → Copilot Studio → Agents → Disable", and the `CopilotStudio_CL` and `FoundryAgents_CL` tables (they do not exist in the validation workspace)
- Verify the SP is not shared with other applications before deleting it: `GET /servicePrincipals/{id}/appRoleAssignedTo` to see all assignments
- Graph API `DELETE /servicePrincipals/{id}` removes the SP at once, but Entra keeps deleted service principals and app registrations in the recycle bin and they can be restored for 30 days (Microsoft Learn); after that the deletion is permanent. Document the state before proceeding anyway
