---
name: protect-information-barriers-agents
version: "1.0"
pillar: protect
subdomain: ms-purview-ai
description: >-
  Implements Information Barriers in Microsoft Purview to keep users and the SharePoint,
  OneDrive and Teams content they reach apart between organizational segments (finance
  and legal, for example), and monitors the cases it does not cover: applications and
  agent identities that reach sites of more than one segment.
tags: [protect, purview, information-barriers, segmentation, compliance, teams, sharepoint]
atlas_techniques: [AML.T0057, AML.T0036]
d3fend_techniques: [D3-UGPH, D3-AMED]
nist_ai_rmf: [MEASURE-2.10, MANAGE-1.3]
nist_csf: [PR.DS-10, PR.AA-05]
ms_license: [Microsoft Purview E5, M365 E5 Compliance]
ms_roles: [Compliance Administrator, IB Administrator]
effort_hours: 8
---

## When to use

- Organizations with regulatory requirements for information separation
  (banks: trading/research separation; law firms: conflicts of interest)
- When the people who work with an agent must not be able to reach another segment's
  sites or files through collaboration
- Post-Pillar-1 audit reveals applications or agents crossing organizational silos

## What Information Barriers cover (Microsoft Learn)

IB restricts two-way communication and collaboration between segments in:
- Microsoft Teams (search for a user, chat, calls, meetings, sharing a file)
- SharePoint Online and OneDrive (adding a member to a site, accessing or sharing site content, searching a site)
- Microsoft Planner (people picker)

**Limitations that matter for agents:**
- IB does not restrict email, Exchange Online included. Use Exchange mail flow rules for email
- IB only supports two-way restrictions: a policy for one direction needs its mirror policy
- Segments are defined with user and group attributes from Microsoft Entra ID or Exchange Online. Learn does not document a segment for a service principal or an agent identity, so
  IB does not separate an application that holds its own SharePoint permissions. Use Query 3 to find those, and control them with Entra permissions and Conditional Access
  (Pillar 2 and 3 skills). The audit log has an `AppBypassInformationBarrier` operation, "changed apps access for SharePoint sites": review that tenant setting with your SharePoint administrator

## Workflow

### Step 1 — Define organizational segments

Segments use user account attributes. Use one attribute for all your segments and keep them from overlapping (a user is in exactly one segment unless you enable multi-segment mode).
`DisplayName` is not in the list of supported attributes, and `-like` is not an operator: use `-eq` or `-ne` on a supported attribute such as `Department`, `MemberOf` or `ExtensionAttribute1`.

```powershell
# Connect to Security & Compliance PowerShell
Connect-IPPSSession

New-OrganizationSegment -Name "Finance" `
  -UserGroupFilter "ExtensionAttribute1 -eq 'Finance'"

New-OrganizationSegment -Name "Legal" `
  -UserGroupFilter "ExtensionAttribute1 -eq 'Legal'"

# If an agent has a user account, give it the attribute and a segment of its own (Learn documents
# segments of users and groups; it does not document agent users specifically)
New-OrganizationSegment -Name "AI-Finance-Agents" `
  -UserGroupFilter "ExtensionAttribute1 -eq 'FinanceAgent'"
```

**Note**: set the attribute on every user account first. A service principal is not a user account, so it cannot be a member of a segment.

### Step 2 — Define IB policies

```powershell
# Finance and Legal cannot communicate: one policy per direction
New-InformationBarrierPolicy -Name "Finance-Legal-Block" `
  -AssignedSegment "Finance" -SegmentsBlocked "Legal" -State Active
New-InformationBarrierPolicy -Name "Legal-Finance-Block" `
  -AssignedSegment "Legal" -SegmentsBlocked "Finance" -State Active

# Finance agent users can only communicate with Finance, and Finance with them
New-InformationBarrierPolicy -Name "AI-Finance-Agents-Allow" `
  -AssignedSegment "AI-Finance-Agents" -SegmentsAllowed "Finance" -State Active
New-InformationBarrierPolicy -Name "Finance-AI-Finance-Agents-Allow" `
  -AssignedSegment "Finance" -SegmentsAllowed "AI-Finance-Agents" -State Active
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

**Teams**: Attempt to have a Finance segment user start a chat with someone in Legal.
It should be blocked automatically.

**SharePoint**: Sites assigned to segments must respect IB.
Verify a Finance user cannot access Legal segment sites.

### Step 5 — Enable IB for SharePoint and OneDrive

```powershell
# Requires the SharePoint administrator or Global administrator role
Set-SPOTenant -InformationBarriersSuspension $false
```

This turns IB on for SharePoint and OneDrive; Learn says to wait about 1 hour for the change to take effect. With Multi-Geo, run it for each geo-location.

### Step 6 — Monitor IB

```kql
// See queries/sentinel-information-barriers.kql
```

## Verification

- [ ] Segments defined with the same supported attribute, and every user account carries it
- [ ] IB policies in Active state, one per direction
- [ ] `Start-InformationBarrierPoliciesApplication` completed
- [ ] Blocked-communication test succeeds (Finance ↔ Legal blocked)
- [ ] IB enabled in SharePoint/OneDrive
- [ ] Active monitoring in Sentinel (administrative changes, cross-segment access, apps across segments)

## Implementation notes

- Information Barriers requires an M365 E5 Compliance or Microsoft 365 E5 license — verify availability before starting implementation
- Segments and policies are not a Graph API configuration in the pages reviewed: use Security & Compliance PowerShell or the Microsoft Purview portal
- After a user's segment changes, the user's OneDrive segment and IB mode update within 24 hours (Learn)
- Query 1 lists the documented administrative operations (`SPOIBIsEnabled`, `SPOIBIsDisabled`, `SiteIBSegmentsSet`, `AppBypassInformationBarrier`, and the others). It returned no rows on the validation tenant (NOT VERIFIED).
  Learn documents no event for a blocked access, so Queries 2 and 3 cross `OfficeActivity` with your own map of users, sites and segments; they ran with an example map
- Removed in this version, because Microsoft Learn (Oct 2026) does not support them: Exchange Online as a workload covered by IB, a segment filter on `DisplayName` with `-like` for agent
  service principals, a one-direction allow policy, the `PurviewAuditLog` table (it does not exist in the validation workspace), and violation operations such as `InformationBarrierPolicyViolation`
