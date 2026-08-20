---
name: govern-entra-agent-id
version: "1.0"
pillar: govern
subdomain: ms-entra
description: >-
  Registra agentes de IA como identidades de primer nivel en Entra ID usando
  Entra Agent ID, separating the agent identity from human users and
  service principals genéricos para habilitar CA policies y trazabilidad forense.
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

- Al desplegar cualquier agente nuevo en el tenant — antes de asignar permisos
- Cuando se detectan agentes operando bajo identidad delegada de usuario (lavado de identidad)
- During governance audits, to validate that every agent has a dedicated identity
- As a prerequisite for applying agent-specific CA policies (`govern-ca-policy-workload-identity`)

## Prerequisites

- Entra ID P1 o superior (P2 para PIM)
- Rol Application Administrator o Cloud Application Administrator
- Acceso a Azure Portal → Entra ID → App registrations
- Acceso a Agent 365 admin center (M365 Admin Center → Agents → Registry)

## Workflow

### Step 1 — Crear el App Registration como Entra Agent ID

```http
POST https://graph.microsoft.com/v1.0/applications
Content-Type: application/json

{
  "displayName": "{nombre-del-agente}",
  "signInAudience": "AzureADMyOrg",
  "tags": ["agent365", "EntraAgentID"],
  "notes": "TechnicalOwner:{email-del-dueno} | AgentType:{copilot-studio|foundry|custom} | CreatedDate:{fecha}"
}
```

### Step 2 — Crear el Service Principal asociado

```http
POST https://graph.microsoft.com/v1.0/servicePrincipals
Content-Type: application/json

{
  "appId": "{appId-del-paso-1}",
  "tags": ["agent365", "EntraAgentID", "WindowsAzureActiveDirectoryIntegratedApp"]
}
```

### Step 3 — Asignar owner técnico

```http
POST https://graph.microsoft.com/v1.0/applications/{app-object-id}/owners/$ref
Content-Type: application/json

{
  "@odata.id": "https://graph.microsoft.com/v1.0/directoryObjects/{owner-user-id}"
}
```

### Step 4 — Verificar registro en Agent 365

1. Ir a **M365 Admin Center** → **Agents** → **Registry**
2. Buscar el agente por nombre — debe aparecer con `EntraAgentId` populated
3. If it does not appear: verify that the `agent365` and `EntraAgentID` tags are in the manifest

### Step 5 — Asignar permisos mínimos (least privilege)

```http
POST https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/appRoleAssignments
Content-Type: application/json

{
  "principalId": "{sp-id}",
  "resourceId": "{sharepoint-sp-id}",
  "appRoleId": "{sites-selected-role-id}"
}
```

Usar `Sites.Selected` en lugar de `Sites.Read.All` siempre que sea posible.

### Step 6 — KQL: Detectar agentes sin Entra Agent ID

```kql
AIAgentsInfo
| where TimeGenerated > ago(30d)
| where isempty(EntraAgentId) or EntraAgentId == "Inherited"
| distinct AgentId, AgentName, AgentType, Platform, TechnicalOwner, ManagementStatus
| extend RiskNote = "Agente opera bajo identidad heredada — sin trazabilidad forense dedicada"
| sort by AgentType asc
```

## Verification

- [ ] App registration creado con tags `agent365` y `EntraAgentID` en manifest
- [ ] Service principal asociado visible en Entra ID → Enterprise Applications
- [ ] Owner técnico asignado en App registration
- [ ] Agente visible en Agent 365 Registry con `EntraAgentId` populated
- [ ] Permisos asignados siguen principio de least privilege
- [ ] The KQL query no longer returns this agent in the without-Entra-Agent-ID list

## Implementation notes

- The key difference between an Entra Agent ID and a generic service principal is the `agentType` field in the token — this enables specific targeting in CA policies
- Agents created via Agent Builder (M365 Copilot) do not go through this process — they appear in Agent 365 Registry but without an Entra Agent ID; document as a known gap
- The App Registration `notes` field is the recommended place for ownership metadata, since there is no dedicated structured field in the standard schema
- Combine with `govern-lifecycle-decommission-agent` for the complete lifecycle process
