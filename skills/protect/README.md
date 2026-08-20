# Pillar 4 — Protect Data

Objective: ensure that the data AI agents access, process, and generate
is classified, protected, and cannot be exfiltrated to unauthorized destinations.

## Recommended sequence

```
INPUT: Agents with a reduced surface (Pillar 3 output)
        ↓
[1] protect-purview-ai-hub-monitoring       ← baseline visibility into interactions
        ↓
[2] protect-sensitivity-labels-ai-outputs   ← classify outputs automatically
        ↓
[3] protect-data-loss-prevention-agent-outputs ← block exfiltration of outputs
        ↓
[4] protect-information-barriers-agents     ← isolate organizational segments
        ↓
OUTPUT: Protected data with active visibility and controls → input for Pillar 5 (Detect)
```

## Skills

| Skill | MS product | Minimum license | KQL available |
|---|---|---|---|
| `protect-purview-ai-hub-monitoring` | Purview AI Hub | Purview E3 | sentinel-ai-hub-activity.kql |
| `protect-sensitivity-labels-ai-outputs` | Purview, AIP | Purview E3 + AIP P2 | sentinel-label-coverage.kql |
| `protect-data-loss-prevention-agent-outputs` | Purview DLP | Purview E3 | sentinel-dlp-outputs.kql |
| `protect-information-barriers-agents` | Purview IB | M365 E5 Compliance | sentinel-information-barriers.kql |

## Distinction: DLP on prompts vs. DLP on outputs

| Skill | What it protects | Where the control sits |
|---|---|---|
| `govern-dlp-policy-copilot-prompts` (P2) | Sensitive data the user sends to the agent | In the input prompt, in real time |
| `protect-data-loss-prevention-agent-outputs` (P4) | Files and content the agent generates | In SharePoint / OneDrive / Exchange, post-generation |

Both skills are complementary — they cover different vectors.

## Known constraints

| Constraint | Impact | Workaround |
|---|---|---|
| Purview auto-labeling via API: limited support | Some configurations are unavailable via Graph | Use the Compliance Portal for initial configuration |
| Graph labels endpoint: `/beta` only | Not production-ready for automation | Accept and document, monitor for GA |
| IB: requires Security & Compliance PowerShell | Not accessible via Lokka-Microsoft MCP | Run PowerShell directly |
| IB SharePoint: propagation takes up to 24h | The control is not immediate | Plan the implementation window |
| AI Hub: preview feature | May change without notice | Validate against MS Learn before documenting |
| IB for agent SPs: requires Entra attributes | Without attributes, SPs are not filterable | Establish a naming convention for agent SPs |
