---
name: protect-information-barriers-agents
version: "1.0"
pillar: protect
subdomain: ms-purview-ai
description: >-
  Implements Information Barriers in Microsoft Purview to prevent AI agents
  from crossing information boundaries between organizational segments,
  preventing an agent in the finance area from accessing legal area data or
  vice versa, meeting regulatory requirements for information separation.
tags: [protect, purview, information-barriers, segmentation, compliance, teams, sharepoint]
atlas_techniques: [AML.T0057, AML.T0048]
d3fend_techniques: [D3-NI, D3-EAC]
nist_ai_rmf: [GOVERN-6.2, MANAGE-2.2]
nist_csf: [PR.DS-05, PR.AC-05]
ms_license: [Microsoft Purview E5, M365 E5 Compliance]
ms_roles: [Compliance Administrator, IB Administrator]
effort_hours: 8
---

## When to use

- Organizations with regulatory requirements for information separation
  (banks: trading/research separation; law firms: conflicts of interest)
- When an agent with access to one segment's data must not be able to
  process or transfer information to another segment
- Post-Pillar-1 audit reveals agents crossing organizational silos

## What Information Barriers cover

IB controls communication and collaboration between segments in:
- Microsoft Teams (chats, channels)
- SharePoint Online
- OneDrive
- Exchange Online

**Limitation**: IB does not directly control agent Graph API calls.
For autonomous agents, complement with Conditional Access and granular RBAC
(Pillar 2 and 3 skills).

## Workflow

### Step 1 — Define organizational segments

Identify the groups that must be kept separate:

```powershell
# Connect to Security & Compliance PowerShell
Connect-IPPSSession

# Create a segment for the finance area
New-OrganizationSegment -Name "Finance" `
  -UserGroupFilter "Department -eq 'Finance'"

# Create a segment for the legal area
New-OrganizationSegment -Name "Legal" `
  -UserGroupFilter "Department -eq 'Legal'"

# Create a segment for finance-area AI agents
# Agent SPs are mapped via UserPrincipalName or DisplayName
New-OrganizationSegment -Name "AI-Finance-Agents" `
  -UserGroupFilter "DisplayName -like 'agent-finance-*'"
```

**Note**: IB uses Entra ID attributes to define segments.
Agent service principals must carry attributes that allow filtering them.

### Step 2 — Define IB policies

```powershell
# Policy: Finance cannot communicate with Legal
New-InformationBarrierPolicy -Name "Finance-Legal-Block" `
  -AssignedSegment "Finance" `
  -SegmentsBlocked "Legal" `
  -State Active

# Policy: AI-Finance-Agents can only access Finance data
New-InformationBarrierPolicy -Name "AI-Finance-Agents-Restrict" `
  -AssignedSegment "AI-Finance-Agents" `
  -SegmentsAllowed "Finance" `
  -State Active
```

### Step 3 — Apply the policies

```powershell
# Apply every active policy
Start-InformationBarrierPoliciesApplication
```

Application can take several hours depending on tenant size.
Monitor with:

```powershell
Get-InformationBarrierPoliciesApplicationStatus
```

### Step 4 — Verify in Teams and SharePoint

**Teams**: Attempt to have a Finance segment agent start a chat with someone in Legal.
It should be blocked automatically.

**SharePoint**: Sites assigned to segments must respect IB.
Verify the Finance agent cannot access Legal segment sites.

### Step 5 — IB compatibility mode for SharePoint

```powershell
# Enable IB in SharePoint/OneDrive
Set-SPOTenant -InformationBarriersSuspension $false
```

This applies IB policies to SharePoint and OneDrive in addition to Teams.

### Step 6 — Monitor IB compliance

```kql
// See queries/sentinel-information-barriers.kql
```

## Verification

- [ ] Segments defined with correct filters in Entra ID
- [ ] IB policies in Active state
- [ ] `Start-InformationBarrierPoliciesApplication` completed
- [ ] Blocked-communication test succeeds (Finance ↔ Legal blocked)
- [ ] IB enabled in SharePoint/OneDrive
- [ ] Active monitoring in Sentinel

## Implementation notes

- Information Barriers requires an M365 E5 Compliance or Microsoft 365 E5 license — verify availability before starting implementation
- IB in SharePoint can take up to 24 hours to fully propagate after enabling the policy — plan the implementation window accordingly
- AI agent segments require SPs to carry Entra attributes that allow filtering — use a naming convention in the display name
- Information Barriers cannot be configured via Graph API in every scenario — use Security & Compliance PowerShell for the configuration
