---
name: detect-data-exfiltration-agent
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Detects data exfiltration patterns through AI agents, including bulk file
  access by an application or agent identity, mail sent to external domains,
  outbound calls to unapproved destinations, DLP matches on agent-sent mail,
  and unusual response volume from Foundry deployments.
tags: [detect, sentinel, exfiltration, data-loss, sharepoint, exchange, aisoc]
atlas_techniques: [AML.T0086, AML.T0057]
d3fend_techniques: [D3-UDTA, D3-OTF, D3-FAPA]
nist_ai_rmf: [MEASURE-2.7, MANAGE-4.1]
nist_csf: [DE.CM-09, DE.AE-03, RS.AN-03]
ms_license: [Microsoft Sentinel, Microsoft Purview E3]
ms_roles: [Microsoft Sentinel Contributor, Security Reader]
effort_hours: 5
---

## When to use

- Agents with access to SharePoint, Exchange, or production databases
- When output DLP is active (Pillar 4) and correlation in Sentinel is needed
- To detect the agent-as-intermediary exfiltration vector:
  a user asks the agent to summarize/export data → the agent accesses a large
  volume → the data leaves via an unmonitored channel

## Exfiltration vectors covered

1. **Bulk access**: an application or agent identity accesses N files in a short time
2. **Summary as exfil**: a user asks for a summary of confidential documents → copies the text out (no query here: it is not visible in the audit record)
3. **Connector abuse**: an agent uses a generic HTTP tool to send data to an external URL
4. **Email relay**: an agent with `Mail.Send` permission sends data to an external account
5. **Cross-tenant**: an agent in a multi-tenant context shares data across tenants (no query here)

## Prerequisites

- The **Microsoft 365** data connector in Sentinel with Exchange and SharePoint enabled (table `OfficeActivity`)
- For Step 5: the Foundry or Azure OpenAI diagnostic setting with the `RequestResponse` category sent to the workspace
- For Step 3: Application Insights resources that are workspace-based, with your agents instrumented

An application or agent with application permissions shows up in `OfficeActivity` with `UserType` = `Application`: in SharePoint and OneDrive
`UserId` is `app@sharepoint` and `ApplicationId` holds the app; in Exchange `UserId` is the mailbox and `ClientAppId` holds the app.
What Copilot reads on behalf of a user is not distinguishable here: it is in `CopilotActivity` (KQL Library P04-Q6).

## Workflow

### Step 1 — Create rule: bulk file access by an app or agent

```kql
// See queries/sentinel-exfiltration.kql — Query 1
// Threshold: > 50 unique files in 30 minutes by the same app or user
```

Sentinel configuration:
- **Name**: `AISEC-Agent-Bulk-File-Access`
- **Frequency**: every 15 minutes
- **Lookback**: last 2 hours
- **Severity**: High

Fill `allowed_apps` with the app IDs you already trust: Microsoft sync and cache clients can cross the threshold.

### Step 2 — Create rule: app or agent sending email to external domains

```kql
// See queries/sentinel-exfiltration.kql — Query 2
```

Configuration:
- **Name**: `AISEC-Agent-Email-External-Domain`
- **Frequency**: every 5 minutes
- **Lookback**: last 24 hours
- **Severity**: High (Critical if it also matches Query 4)

Set `internal_domains` to your tenant's domains.

### Step 3 — Create rule: outbound HTTP calls from instrumented agents to unapproved domains

```kql
// See queries/sentinel-exfiltration.kql — Query 3
// NOT VERIFIED: depends on the agent emitting HTTP dependency telemetry to Application Insights
```

### Step 4 — Correlate with DLP matches

```kql
// See queries/sentinel-exfiltration.kql — Query 4
// Joins app-sent mail with the Exchange DLP rule match by message id
```

### Step 5 — Create rule: response volume from a Foundry account

```kql
// See queries/sentinel-exfiltration.kql — Query 5
```

### Step 6 — Add the Purview signals for AI

```
Microsoft Purview → Data Security Posture Management (DSPM) for AI → Recommendations
→ "Detect risky interactions in AI apps" (creates the Insider Risk Management policy DSPM for AI - Detect risky AI usage)
```

Insider Risk Management also has a policy template for agents hosted on Copilot Studio and Microsoft Foundry: it detects risky prompts, agents generating
sensitive responses, agents accessing sensitive or priority SharePoint files and risky websites, and agents sharing SharePoint files with people outside
the organization, and it tracks activity above the agent's baseline (Learn, "Insider Risk Management policy templates"; applied by default).

## Verification

- [ ] Bulk access rule created and tested with synthetic data
- [ ] External email rule created (if agents have Mail.Send)
- [ ] Correlation with DLP matches (Query 4) returns rows or "No results" without error
- [ ] Test incident generated with simulated bulk access
- [ ] Containment playbook linked to the rules (see next skill)

## Implementation notes

- Queries 1, 2 and 4 run on `OfficeActivity` and returned rows on the validation workspace. Query 1 flagged a third-party application (a Java HTTP client) with
  hundreds of files in 30 minutes; the DLP match key joins to sent mail (41 matches in 90 days across mail sent by users and by apps) and Query 4 returned mail sent by an app; Query 5 returned rows with a low threshold
- Query 5 reads the bytes in `properties_s` (`requestLength`, `responseLength`): the diagnostic records carry no tokens or content. The calls seen on the validation
  Foundry account are management operations of KB size, so the 10 MB threshold does not fire there. Adjust it to your normal use
- The DLP rule match event carries the user and the record type, not the policy name; the policy detail is in the Purview DLP alert
- To simulate exfiltration in a test tenant: create a SharePoint folder with 60+ test files and read them all in one run from a test app registration
  with `Sites.Read.All` (the events show `UserType` = `Application`)
- The email relay vector requires the agent SP to hold `Mail.Send` — verify with the `secure-least-privilege-agent-identity` skill
- If the agent has no HTTP dependency telemetry: use the egress logs you already collect. Virtual network flow logs are the supported source (NSG flow logs
  retire on September 30, 2027, and no new ones can be created)
- Removed in this version, because Microsoft Learn (Oct 2026) does not support them: the `PurviewAuditLog`, `MicrosoftDataLossPrevention` and
  `FoundryAgents_CL` tables (they do not exist in the validation workspace), the token-to-bytes estimate, and the Purview AI Hub "Data volume threshold"
  policy with an "Alert + Restrict" action (the product is now DSPM for AI, and Learn lists no policy of that type)
