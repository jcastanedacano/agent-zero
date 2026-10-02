---
name: govern-entra-agent-id
version: "1.0"
pillar: govern
subdomain: ms-entra
description: >-
  Registers AI agents as first-class identities in Entra ID using
  Entra Agent ID, separating the agent identity from human users and
  generic service principals to enable CA policies and forensic traceability.
tags: [govern, entra, agent-id, identity, lifecycle, audit-trail]
atlas_techniques: [AML.T0040, AML.T0012]
d3fend_techniques: [D3-MAN, D3-SFA]
nist_ai_rmf: [GOVERN-2.1, GOVERN-4.1, MAP-1.5]
nist_csf: [PR.AA-01, PR.AA-05, ID.AM-02]
ms_license: [Microsoft Entra ID P1, Agent 365]
ms_roles: [Application Administrator, Cloud Application Administrator]
effort_hours: 2
---

## When to use

- When deploying any new agent in the tenant — before assigning permissions
- When agents are found operating under a delegated user identity (identity laundering)
- During governance audits, to validate that every agent has a dedicated identity
- As a prerequisite for applying agent-specific CA policies (`govern-ca-policy-workload-identity`)

## Prerequisites

- Entra ID P1 or higher (P2 for PIM)
- Application Administrator or Cloud Application Administrator role
- Access to Azure Portal → Entra ID → App registrations
- Access to the Agent 365 admin center (M365 Admin Center → Agents → Registry)

## Workflow

### Step 1 — Create the App Registration as an Entra Agent ID

```http
POST https://graph.microsoft.com/v1.0/applications
Content-Type: application/json

{
  "displayName": "{agent-name}",
  "signInAudience": "AzureADMyOrg",
  "tags": ["agent365", "EntraAgentID"],
  "notes": "TechnicalOwner:{owner-email} | AgentType:{copilot-studio|foundry|custom} | CreatedDate:{date}"
}
```

### Step 2 — Create the associated Service Principal

```http
POST https://graph.microsoft.com/v1.0/servicePrincipals
Content-Type: application/json

{
  "appId": "{appId-from-step-1}",
  "tags": ["agent365", "EntraAgentID", "WindowsAzureActiveDirectoryIntegratedApp"]
}
```

### Step 3 — Assign the technical owner

```http
POST https://graph.microsoft.com/v1.0/applications/{app-object-id}/owners/$ref
Content-Type: application/json

{
  "@odata.id": "https://graph.microsoft.com/v1.0/directoryObjects/{owner-user-id}"
}
```

### Step 4 — Verify registration in Agent 365

1. Go to **M365 Admin Center** → **Agents** → **Registry**
2. Search for the agent by name — it should appear with `EntraAgentID` populated
3. If it does not appear: verify that the `agent365` and `EntraAgentID` tags are in the manifest

### Step 5 — Assign minimal permissions (least privilege)

```http
POST https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/appRoleAssignments
Content-Type: application/json

{
  "principalId": "{sp-id}",
  "resourceId": "{sharepoint-sp-id}",
  "appRoleId": "{sites-selected-role-id}"
}
```

Use `Sites.Selected` instead of `Sites.Read.All` whenever possible.

### Step 6 — KQL: detect agents without Entra Agent ID

```kql
AgentsInfo
| where TimeGenerated > ago(30d)
| where isempty(EntraAgentID) or EntraAgentID == "Inherited"
| distinct AgentId, Name, Platform, LifecycleStatus, Owners
| extend RiskNote = "Agent operates under an inherited identity — no dedicated forensic traceability"
| sort by LifecycleStatus asc
```

## Verification

- [ ] App registration created with the `agent365` and `EntraAgentID` tags in the manifest
- [ ] Associated service principal visible in Entra ID → Enterprise Applications
- [ ] Technical owner assigned on the App registration
- [ ] Agent visible in the Agent 365 Registry with `EntraAgentID` populated
- [ ] Assigned permissions follow the least privilege principle
- [ ] The KQL query no longer returns this agent in the without-Entra-Agent-ID list

## Implementation notes

- The key difference between an Entra Agent ID and a generic service principal is the `agentType` field in the token — this enables specific targeting in CA policies
- Agents created via Agent Builder (M365 Copilot) do not go through this process — they appear in Agent 365 Registry but without an Entra Agent ID; document as a known gap
- The App Registration `notes` field is the recommended place for ownership metadata, since there is no dedicated structured field in the standard schema
- Combine with `govern-lifecycle-decommission-agent` for the complete lifecycle process
