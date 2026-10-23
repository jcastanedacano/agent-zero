# Attack paths

A small library of privilege-escalation and excessive-agency paths on the Microsoft stack, one YAML file per path, for people who defend AI agents and the
identities behind them. Each path names the permission abused, what must be true for the abuse to work, how to see it, and how to remove it.

It is **defensive**. The `workshop` block of the Track C paths carries the exercise prompts for a **demo tenant**, as in Module 06; no path carries exploitation commands for real environments. See [SCHEMA.md](./SCHEMA.md) for the fields.

| Path | What it is | Severity | Category | Validation | Lab |
|---|---|---|---|---|---|
| [xpia-001](./paths/xpia-001.yaml) | Indirect prompt injection (XPIA) via an unlabelled SharePoint document | critical | prompt-injection | documented | exercise |
| [builder-001](./paths/builder-001.yaml) | Agent Builder bypass: an ungoverned agent shared with the organization | high | ungoverned-deployment | documented | exercise |
| [extraction-001](./paths/extraction-001.yaml) | Model extraction via systematic inference | medium | model-extraction | documented | exercise (read-only) |
| [disclosure-001](./paths/disclosure-001.yaml) | Capability and architecture disclosure | medium | capability-disclosure | documented | exercise (read-only) |
| [hijack-001](./paths/hijack-001.yaml) | Goal hijacking by multi-step session manipulation | high | goal-hijacking | documented | exercise |
| [chain-001](./paths/chain-001.yaml) | JadePuffer: agentic ransomware chain | critical | agentic-ransomware | documented | exercise |
| [agent-001](./paths/agent-001.yaml) | Graph write permission on the agent identity + a write-capable tool | high | excessive-agency | **observed in lab** | exercise |
| [agent-002](./paths/agent-002.yaml) | Credential added to an agent identity blueprint | high | credential-access | documented | exercise (read-only) |
| [agent-003](./paths/agent-003.yaml) | Inheritable permissions on an agent identity blueprint principal | high | principal-access | documented | exercise |
| [entra-001](./paths/entra-001.yaml) | `Application.ReadWrite.All` | high | credential-access | not verified | exercise |
| [entra-002](./paths/entra-002.yaml) | `AppRoleAssignment.ReadWrite.All` | critical | self-escalation | not verified | exercise |
| [entra-003](./paths/entra-003.yaml) | `RoleManagement.ReadWrite.Directory` | critical | self-escalation | not verified | exercise |
| [rbac-001](./paths/rbac-001.yaml) | `Microsoft.Authorization/roleAssignments/write` | high | self-escalation | not verified | exercise (IaC) |
| [jailbreak-001](./paths/jailbreak-001.yaml) | Platform-detected jailbreak signal left unactioned | high | goal-hijacking | not verified | exercise (read-only) |
| [memory-001](./paths/memory-001.yaml) | Memory poisoning via a flagged interaction | high | prompt-injection | not verified | exercise |
| [supply-001](./paths/supply-001.yaml) | Ungoverned third-party agent with anomalous behavior | high | ungoverned-deployment | not verified | exercise (read-only) |
| [lateral-001](./paths/lateral-001.yaml) | Multi-agent lateral movement via unauthorized `InvokeAgent` | high | principal-access | not verified | exercise (read-only) |
| [exfil-001](./paths/exfil-001.yaml) | Mass exfiltration via agent-as-intermediary | high | excessive-agency | not verified | exercise |
| [lpci-001](./paths/lpci-001.yaml) | LPCI — logic-layer prompt control injection via tool response | high | prompt-injection | not verified | exercise (read-only) |
| [decomposition-001](./paths/decomposition-001.yaml) | Algorithmic payload decomposition across multiple turns | medium | prompt-injection | not verified | exercise (read-only) |

The first six are the Track C, Module 06 red-team exercises (the "Agentic Red-Team Map" session companion renders them from these files); `agent-001` to `agent-003` are the identity and tool paths of an Agent 365 agent; `entra-001` to `rbac-001` are Entra and Azure paths with no Agent 365 specific behaviour. The seven paths from `jailbreak-001` to `decomposition-001` close part of a gap identified against the KQL library and the skills catalog: each wraps a detection query (or pair of queries) that already existed in [KQL-Library/](../KQL-Library/) — P03 (Access Anomalies), P04 (Exfiltration Detection) or P05 (Jailbreak Detection) — but had no attack-path file of its own, plus the two orphaned skills `discover-third-party-ai-risk` and `detect-data-exfiltration-agent`, which likewise had no path. None of them was reproduced in a lab for this addition: every one is `not verified`, and each file carries forward the specific telemetry gaps (undocumented fields, fields not surfaced in advanced hunting, empty validation runs) that the underlying KQL query already documented, rather than asserting a detection that has not actually been seen to work. The remaining part of that gap (membership inference, model inversion, identity laundering, PIM activation abuse, orphaned identity takeover) overlaps with PR #19, open at the time of this addition; those path files were held back here rather than filed under colliding names.

The **Lab** column says which paths have a hands-on exercise (`lab` block): objective, resources, setup, a guided attack with the evidence each step must show, cleanup, and what to prevent and detect. Every path now has one. Most are manual exercises for a **demo tenant** (`kind: tenant-exercise`); `rbac-001` is the only one with reproducible infrastructure so far (`kind: iac`) — a Bicep template under [`labs/rbac-001/`](./labs/rbac-001/) that deploys the vulnerable and hardened configurations, so the guided steps compare two real resources instead of describing them. None of the paths added after `xpia-001`, `agent-001`, `agent-002` and `rbac-001` was run against a tenant for this file: each one's own `lab.validation` says so, same as the path it belongs to.

## How to read the validation column

- **observed in lab**: reproduced end to end, with the evidence named in the file.
- **documented**: described in Microsoft documentation or public research, not reproduced here.
- **not verified**: written from knowledge of the platform; nothing was run. The audit operation names and tenant protections in these files must be checked in
  your tenant before you rely on them.

Detection entries point at queries that already exist in this repository. Where none exists, the file says so under `detection.gaps` instead of inventing one;
turning a gap into a validated query is the most useful contribution (see [CONTRIBUTING.md](./../CONTRIBUTING.md)).

`agent-001` was reproduced in the D3FEND Cyber Range, a companion lab for the same material.
