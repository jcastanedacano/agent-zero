---
name: secure-least-privilege-agent-identity
version: "1.0"
pillar: secure
subdomain: ms-entra
description: >-
  Audits and reduces AI agent service principal permissions to the minimum
  necessary, removing excessive OAuth2 permission grants and unused app role
  assignments, applying the least privilege principle to non-human identities.
tags: [secure, entra, least-privilege, service-principal, oauth, app-roles]
atlas_techniques: [AML.T0012, AML.T0040]
d3fend_techniques: [D3-UAP, D3-MAN]
nist_ai_rmf: [MANAGE-1.3, GOVERN-2.2]
nist_csf: [PR.AA-05, PR.AC-04]
ms_license: [Microsoft Entra ID P1]
ms_roles: [Application Administrator, Privileged Role Administrator]
effort_hours: 6
---

## When to use

- Post connector classification (Pillar 1): agents with excessive permissions identified
- Before moving agents to production
- Periodic quarterly audit of agent permissions

## Core principle

An AI agent should only hold the permissions it needs to execute
its declared use case, nothing more. Permissions such as `Files.ReadWrite.All`
when the use case only requires reading a specific SharePoint site
are an unnecessary attack surface.

## Workflow

### Step 1 — Audit the service principal's current permissions

```http
# OAuth2 delegated permissions (act on behalf of a user)
GET https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/oauth2PermissionGrants
  ?$select=scope,consentType,principalId

# App role assignments (act as the application, no user)
GET https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/appRoleAssignments
  ?$select=appRoleId,resourceDisplayName,principalDisplayName
```

### Step 2 — Map permissions to the actual use case

For each permission, answer:
- Does the agent actively use this permission? (verify in usage logs)
- Does the documented use case require it?
- Is there a lower-privilege permission that covers the same need?

**Common substitution table:**

| Current permission (excessive) | Replace with |
|---|---|
| `Files.ReadWrite.All` | `Sites.Selected` (specific SharePoint) |
| `Mail.ReadWrite` | `Mail.Read` (if read-only) |
| `Directory.ReadWrite.All` | `Directory.Read.All` or a specific scope |
| `User.ReadWrite.All` | `User.Read` (if it only reads its own profile) |
| `Group.ReadWrite.All` | `GroupMember.Read.All` |

### Step 3 — Revoke excessive permissions

```http
# Revoke a specific OAuth2 grant
DELETE https://graph.microsoft.com/v1.0/oauth2PermissionGrants/{grant-id}

# Revoke an app role assignment
DELETE https://graph.microsoft.com/v1.0/servicePrincipals/{resource-sp-id}/appRoleAssignedTo/{assignment-id}
```

### Step 4 — Assign granular replacement permissions

Example — `Sites.Selected` for access to a specific SharePoint site:

```http
# Step 4a: Assign the Sites.Selected app role to the SP
POST https://graph.microsoft.com/v1.0/servicePrincipals/{sharepoint-sp-id}/appRoleAssignedTo
{
  "principalId": "{agent-sp-object-id}",
  "resourceId": "{sharepoint-sp-id}",
  "appRoleId": "{sites-selected-role-id}"
}

# Step 4b: Grant access to the specific site via the Sites API
POST https://graph.microsoft.com/v1.0/sites/{site-id}/permissions
{
  "roles": ["read"],
  "grantedToIdentities": [{
    "application": {
      "id": "{agent-app-id}",
      "displayName": "{agent-name}"
    }
  }]
}
```

### Step 5 — Verify functionality after the reduction

Run the agent use case and confirm it works with the reduced permissions.
Monitor authorization errors for the first 3-5 days.

### Step 6 — Monitor usage of remaining permissions

```kql
// See queries/sentinel-permission-usage.kql
```

## Verification

- [ ] Pre- and post-reduction permission inventory documented
- [ ] Excessive permissions revoked (GET returns a reduced array)
- [ ] Granular replacement permissions assigned
- [ ] Agent functionality verified
- [ ] Authorization error monitoring active (3-5 days post-change)

## Implementation notes

- `Sites.Selected` is the least privilege alternative to `Sites.ReadWrite.All` for agents that only need access to specific sites
- To get the `appRoleId` for `Sites.Selected`, query the SharePoint service principal appRoles via Graph
- Graph API permission changes can take up to 60 minutes to propagate — do not assume immediate effect in CI/CD pipelines
- Use Graph Explorer (graph.microsoft.com) to validate the minimum required scope before assigning permissions in production
