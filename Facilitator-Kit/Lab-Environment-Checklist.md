# Lab Environment Checklist

Run this checklist **24 hours before the session**. If any item is red, you have time to recover. On lab day you don't.

---

## Track A — Executive Briefing

- [ ] Presentation slides loaded and screen-share tested
- [ ] Demo tenant accessible (if using live demo)
- [ ] At least one Copilot Studio agent visible in Copilot Studio → Agents list
- [ ] Backup: screenshots of all live demo steps ready in case tenant access fails

---

## Track B — Architect Workshop

- [ ] M365 E5 CDX tenant active and accessible with facilitator account
- [ ] Azure subscription accessible — Contributor role confirmed
- [ ] ARM template deployed (or ready to deploy at session start)
  - Sentinel workspace name: `agentic-security-lab`
  - Region: [NOTE YOUR REGION]
- [ ] Gap Assessment Template distributed to participants: `Track-B-Architect/Templates/Gap-Assessment-Template.md`
- [ ] Miro board or whiteboard tool ready for architecture design sessions

---

## Track C — SOC Engineer Workshop

### Tenant and Access

- [ ] CDX tenant active — log in with facilitator account at [portal.microsoft.com](https://portal.microsoft.com)
- [ ] All participant accounts created and MFA configured
- [ ] Security Admin role assigned to participant accounts in Entra
- [ ] Sentinel Contributor role assigned in the Sentinel workspace
- [ ] Compliance Administrator role assigned in Purview

### Sentinel Workspace

- [ ] ARM template deployed successfully — no errors in deployment log
- [ ] Sentinel workspace open: Azure Portal → Microsoft Sentinel → [workspace name]
- [ ] Data connectors showing as **Connected:**
  - [ ] Microsoft 365
  - [ ] Microsoft Defender XDR
  - [ ] Microsoft Purview

### Table Validation — Run in Sentinel → Logs

```kql
// Run each — all must return > 0 rows
AgentsInfo | take 5
CloudAppEvents | where TimeGenerated > ago(7d) | take 5
OfficeActivity | where TimeGenerated > ago(7d) | take 5
MicrosoftPurviewInformationProtection | where TimeGenerated > ago(7d) | take 5
AADServicePrincipalSignInLogs | where TimeGenerated > ago(7d) | take 5
AuditLogs | where TimeGenerated > ago(7d) | take 5
```

- [ ] All 6 tables return results

### Lab-Specific Checks

**Module 01 (Discover):**
- [ ] At least 3 agents visible in `AgentsInfo` with different `LifecycleStatus` values

**Module 02 (Govern):**
- [ ] Copilot Studio accessible: [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)
- [ ] At least one Copilot Studio agent deployed in the tenant

**Module 03 (Secure Access):**
- [ ] At least one service principal visible in Entra → Enterprise Applications
- [ ] Entra CA policy list and Sign-in logs → Service principal sign-ins (Conditional Access and Report-only tabs) accessible

**Module 04 (Protect Data):**
- [ ] Microsoft Purview compliance portal accessible: [purview.microsoft.com](https://purview.microsoft.com)
- [ ] DLP policies section visible (requires Compliance Admin role)
- [ ] At least one SharePoint site accessible for label audit

**Module 05 (Detect & Respond):**
- [ ] Sentinel Analytics rules page accessible and no quota errors
- [ ] Logic Apps accessible in the Azure subscription
- [ ] At least one existing analytics rule visible in Sentinel for reference

---

## Common — All Tracks

- [ ] Workshop materials distributed (or link shared): GitHub repo URL confirmed accessible
- [ ] KQL Library link tested: all 5 `.kql` files open in browser
- [ ] Communication channel set up for participant questions (Teams channel or chat)
- [ ] Backup internet connection available (hotspot) in case venue WiFi blocks Azure Portal
- [ ] Time zone confirmed with all remote participants

---

## If Something Is Broken

| Issue | Recovery |
|-------|----------|
| `AgentsInfo` empty | The ARM template deploys no connectors and no data. Check the Agent 365 onboarding and the Microsoft 365 connector in Defender (see Prerequisites), allow 2 to 4 hours, and confirm the Defender XDR connector streams the table to the workspace. Advanced Hunting is the other place to run the query |
| Sentinel workspace missing | Deploy via ARM template → takes ~10 minutes |
| Participant missing role | Entra admin center → Users → [user] → Assigned roles → Add assignment |
| CDX tenant expired | Request new CDX tenant (48h lead time) or use M365 Developer Program sandbox |
| Azure subscription over quota | Check subscription limits in Azure Portal → Quotas; request increase or use a different subscription |
| Logic Apps not accessible | Confirm Contributor role on the resource group, not just the Sentinel workspace |
