---
name: govern-ca-policy-workload-identity
version: "1.0"
pillar: govern
subdomain: ms-entra
description: >-
  Implements Conditional Access policies in Entra ID for agents that run as
  workload identities (single-tenant service principals): block token requests
  from outside known public IP ranges or at a chosen service principal risk, and
  validate in report-only mode first. Block is the only grant control. Agents
  registered with Entra Agent ID use a separate policy type.
tags: [govern, entra, conditional-access, workload-identity, agent-identity]
atlas_techniques: [AML.T0012, AML.T0091.000]
d3fend_techniques: [D3-AMED, D3-NAM]
nist_ai_rmf: [MANAGE-1.3, MEASURE-2.7]
nist_csf: [PR.AA-03, PR.AA-05]
ms_license: [Microsoft Entra ID P1, Microsoft Entra Workload ID Premium]
ms_roles: [Conditional Access Administrator, Security Administrator]
effort_hours: 8
---

## When to use

- Post Pillar 1: agents classified as High risk require access controls
- The agent runs as a plain single-tenant service principal (an app registration with a secret or certificate), outside Entra Agent ID
- The customer has Entra ID P1 (a hard prerequisite for CA)
- Workload Identities Premium licenses are required to create or modify a Conditional Access policy scoped to service principals. Existing policies keep working without the license but cannot be modified (Learn)

An agent registered with Entra Agent ID is a different object with its own policy type, its own risk condition and its own license plan: use `secure-ca-policy-agents` for it.

## Critical implementation constraints

**Block is the only grant control for workload identities.** Learn: under Grant, "Block access" is the only available option, because a workload identity cannot perform multifactor authentication. A policy that requires MFA for users does not reach a service principal either. This skill does not claim what the Graph API does when it is sent a different control: Learn does not document it.

**What the policy covers (Learn).**

- Single-tenant service principals registered in your tenant. Microsoft and third-party SaaS applications, including multitenant apps, are not covered
- Managed identities are not covered. Review them with an access review instead
- The service principal must be assigned directly to the policy: a Conditional Access policy assigned to a group that contains a service principal is not enforced for it
- Target resources: All resources. The policy applies only when the service principal requests a token
- Conditions: location (Any location, excluding the allowed ones) and service principal risk (from ID Protection)

**Continuous access evaluation.** CAE for workload identities enforces these location and risk policies in near real time, with limits (Learn): only access requests to Microsoft Graph, only clients that declare the `cp1` capability, and only single-tenant service principals. Other resources, multitenant apps and managed identities are not covered, so the policy is still evaluated at token issuance for them.

Always start in `enabledForReportingButNotEnforced`, review the sign-in logs for at least 7 days, then enable.

## Prerequisites

- Agent service principals identified (Pillar 1 output)
- Workload Identities Premium licenses in the tenant (needed to create or modify the policy)
- Named Locations with the **public** egress IP ranges of the networks the agents run from. A private range such as 10.0.0.0/8 never appears as the source of a token request, so it would match nothing

## Workflow

### Step 1 — Get the service principal's object ID and check that it is in scope

```http
GET https://graph.microsoft.com/v1.0/servicePrincipals
  ?$filter=displayName eq '{AgentDisplayName}'
  &$select=id,appId,displayName,servicePrincipalType,signInAudience
```

Record the `id` (object ID), not the `appId`: Conditional Access finds the calling app by the service principal's object ID. Check the scope: `signInAudience` must be `AzureADMyOrg` (single tenant) and `servicePrincipalType` must be `Application`. A multitenant app or a `ManagedIdentity` is not covered by the policy.

### Step 2 — Create a Named Location (if it does not exist)

```http
POST https://graph.microsoft.com/v1.0/identity/conditionalAccess/namedLocations
Content-Type: application/json

{
  "@odata.type": "#microsoft.graph.ipNamedLocation",
  "displayName": "Agent egress - {TenantName}",
  "isTrusted": true,
  "ipRanges": [
    {
      "@odata.type": "#microsoft.graph.iPv4CidrRange",
      "cidrAddress": "203.0.113.0/24"
    }
  ]
}
```

`203.0.113.0/24` is a documentation range: replace it with the public egress addresses of the network or service the agent runs from. Record the created Named Location's `id`.

### Step 3 — Create the CA policy in report-only

Learn publishes this sample for the Microsoft Graph beta endpoint:

```http
POST https://graph.microsoft.com/beta/identity/conditionalAccess/policies
Content-Type: application/json

{
  "displayName": "AISEC-Block-Agents-Outside-CorpNetwork",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "applications": {
      "includeApplications": ["All"]
    },
    "clientApplications": {
      "includeServicePrincipals": ["{service-principal-object-id}"]
    },
    "locations": {
      "includeLocations": ["All"],
      "excludeLocations": ["{named-location-id}"]
    }
  },
  "grantControls": {
    "operator": "and",
    "builtInControls": ["block"]
  }
}
```

For a risk-based policy replace the `locations` condition with the service principal risk condition (portal: Conditions > Service principal risk).

### Step 4 — Monitor in the sign-in logs (at least 7 days)

```
Entra ID > Monitoring & health > Sign-in logs > Service principal sign-ins
> open an entry > Conditional Access tab and Report-only tab
```

Or run Query 2 in `queries/sentinel-ca-monitoring.kql`: a policy that would have blocked the sign-in shows `reportOnlyFailure` (Learn: "Report-only: Failure" is a policy that applies where a block control is configured). Confirm there are no false positives (legitimate access that would be blocked). Query 4 lists the successful sign-ins from outside the trusted ranges, which is how you validate the Named Location before enforcing.

### Step 5 — Activate enforcement

```http
PATCH https://graph.microsoft.com/beta/identity/conditionalAccess/policies/{policy-id}
Content-Type: application/json

{
  "state": "enabled"
}
```

## Verification

- [ ] The service principal is single tenant, of type `Application`, and assigned directly to the policy (not through a group)
- [ ] Named Location created with the correct public IP ranges
- [ ] Policy in report-only with no false positives after at least 7 days
- [ ] Policy activated (`state: enabled`)
- [ ] Query 3 shows blocks from external IPs (result code 53003, "Access has been blocked due to Conditional Access policies.")
- [ ] No impact on legitimate agent access

## Implementation notes

- Known error `AADSTS500011`: the resource principal does not exist in the tenant. Verify the agent SP exists with `GET /servicePrincipals/`
- Keep agent CA policies in report-only mode for at least 7 days to identify false positives before enforcing
- The Agents assignment (`clientApplications.includeAgentIdServicePrincipals` in Graph beta) belongs to Entra Agent ID and to `secure-ca-policy-agents`. It is not a way to group classic service principals
- Removed in this version, because it does not match Microsoft Learn: `grantControls: mfa` described as "invalid" for agent identities, `sessionControls` as an alternative to Block, the claim that `continuousAccessEvaluation` cannot be in report-only, the private-range Named Location, the "Report-only: Would be blocked" label, and the v1.0 sample without `conditions.applications`
