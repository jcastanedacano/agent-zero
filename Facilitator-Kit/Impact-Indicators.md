# Impact Indicators

Signals that the workshop is working — per track. Use these during and after the session to gauge whether participants are getting the intended value.

These aren't attendance metrics. They're leading indicators of behavior change and production deployment likelihood.

---

## Track A — Executive Briefing

### During the session

- Participants ask about their **specific tenant** — "how many agents do we have today?" rather than generic questions
- Someone pulls out a phone to screenshot the risk framework slide
- A question about **budget or procurement** comes up (signals intent to act, not just learn)
- At least one participant mentions a specific AI deployment in their organization by name

### After the session (follow up within 2 weeks)

- [ ] Participant requests a Track B or C session for their technical team
- [ ] Participant shares the GitHub repo internally
- [ ] A meeting is scheduled with security or architecture team
- [ ] Executive sponsor identified for an agentic AI security review

### Red flags (session not landing)

- All questions are theoretical — no connection to their environment
- Participant is checking email during the session
- No one asks about next steps at the end

---

## Track B — Architect Workshop

### During the session

- Participants are filling in the Gap Assessment Template with **their own names**, not placeholder values
- Architecture whiteboard shows a specific agent topology from their organization, not a generic diagram
- Discussion of **existing agents already in production** — the conversation shifts from "if we deploy" to "we have deployed"
- Someone identifies a gap they hadn't seen before (especially the Agent Builder bypass pattern)
- A priority order for remediation emerges from the group organically

### After the session (follow up within 4 weeks)

- [ ] Gap Assessment Template completed and shared back
- [ ] At least one remediation item from the template has a named owner and target date
- [ ] Architecture decision record (ADR) or design doc started for agent identity management
- [ ] Track C session scheduled for the SOC team

### Red flags

- Gap Assessment Template left entirely blank — participants didn't engage with their own environment
- All findings are framed as "future state" with no current-state acknowledgment
- No one volunteers to own a remediation item

---

## Track C — SOC Engineer Workshop

### During the session — Module level

**Module 01:** Participants find at least one agent in `AgentsInfo` they didn't know existed. Surprise is a good signal.

**Module 02:** The Agent Builder bypass pattern triggers a "wait, that's already happening" reaction.

**Module 03:** The `grantControls: mfa` invalid-for-agents finding lands as a genuine discovery, not just content consumption.

**Module 04:** Participants immediately think of a SharePoint site in their environment that is probably misconfigured.

**Module 05:** The enforcement flow timeline (T+0 to T+30) prompts discussion about whether their current MTTR matches or beats it.

### Quantitative signals

| Indicator | Target |
|-----------|--------|
| Analytics rules created during labs | ≥ 5 per participant |
| Tables that returned actual data (not demo only) | ≥ 4 of 6 |
| Playbook template sections completed with real findings | ≥ 3 of 5 |
| Participants who ask to keep the Sentinel workspace running | ≥ 50% |

### After the session (follow up within 2 weeks)

- [ ] Incident response playbook submitted (even partially complete)
- [ ] At least one analytics rule deployed to a non-demo workspace
- [ ] KQL library queries saved to participant's Sentinel favorites or watchlist
- [ ] Logic App enforcement playbook deployed or scheduled for deployment

### Red flags

- Participants copy-paste queries without running them (no validation, no adaptation)
- Playbook template stays at the template state — no tenant-specific data filled in
- No one asks what happens after the 90-day Sentinel trial ends

---

## Aggregate — Multi-Track Event

If running Tracks A, B, and C across a multi-day event:

| Signal | What It Means |
|--------|---------------|
| Track A attendees register for Track B/C | Executive buy-in is converting to technical action |
| Track B architects attend Track C wrap-up | Architecture and operations are aligned |
| GitHub repo starred or forked by participants | Content is valuable enough to keep |
| KQL queries adapted (not just copied) | Participants understand the underlying logic |
| Someone reports finding a real, previously-unknown agent | The workshop had production security impact |

The last signal is the one that matters most. Everything else is a leading indicator pointing toward it.
