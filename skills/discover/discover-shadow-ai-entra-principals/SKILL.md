---
name: discover-shadow-ai-entra-principals
version: "1.0"
pillar: discover
subdomain: ms-entra
description: >-
  Detects service principals in Entra ID created by undocumented AI agents
  or AI applications, identifying excessive OAuth consent grants and
  applications with sensitive Graph API permissions that lack a security
  review.
tags: [discover, entra, shadow-ai, service-principal, oauth, graph-permissions]
atlas_techniques: [AML.T0084, AML.T0040, AML.T0103]
d3fend_techniques: [D3-UAP, D3-SFA]
nist_ai_rmf: [MAP-1.1, GOVERN-2.1]
nist_csf: [ID.AM-02, PR.AA-01]
ms_license: [Microsoft Entra ID P1]
ms_roles: [Application Administrator, Security Reader]
effort_hours: 3
---

## When to use

- After the Copilot Studio and Foundry inventory — to detect surface not covered by it
- When there are reports of unrecognized OAuth applications in sign-in logs
- Periodic audit of Graph API permissions in the tenant

## Prerequisites

- Microsoft Graph API access (Lokka-Microsoft MCP or Graph Explorer)
- Application Administrator role or higher
- Entra ID P1 for access to full sign-in logs

## Workflow

### Step 1 — Recently created service principals

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals
  ?$filter=createdDateTime ge {30d-ago-date}
  &$select=displayName,appId,createdDateTime,tags,servicePrincipalType
  &$orderby=createdDateTime desc
```

Filter `servicePrincipalType != "ManagedIdentity"` to see external applications.

### Step 2 — OAuth2 permissions with sensitive access

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals/{id}/oauth2PermissionGrants
```

High-risk permissions to look for:
- `Mail.ReadWrite`, `Mail.Send` — email access
- `Files.ReadWrite.All` — SharePoint/OneDrive access
- `Calendars.ReadWrite` — calendar access
- `Directory.ReadWrite.All` — directory access

### Step 3 — App role assignments (application permissions, not delegated)

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals/{id}/appRoleAssignments
```

App roles (no user) are more dangerous than delegated — the agent acts on its own.

### Step 4 — Cross-reference with AuditLogs in Sentinel

```kql
// See queries/sentinel-shadow-principals.kql
```

### Step 5 — Classify by risk level

| Condition | Recommended action |
|---|---|
| SP with `Mail.ReadWrite` + created by a non-IT user | Revoke immediately |
| SP with `Files.ReadWrite.All` and no documented owner | Review and document |
| SP with no activity in 30 days and active permissions | Decommission candidate |

## Verification

- [ ] List of SPs created in the last 30/60/90 days
- [ ] Sensitive permissions identified per SP
- [ ] Application owners documented
- [ ] SPs with no recent activity flagged for review

## Implementation notes

- Use Graph Explorer (graph.microsoft.com) or an application with `Application.Read.All` to run the API calls in this workflow
- The Entra ID AuditLogs connector must be active in Sentinel to correlate service principal creation events
- SP sign-in logs are available in `AADServicePrincipalSignInLogs` in Sentinel — use it to detect anomalous activity post-inventory
