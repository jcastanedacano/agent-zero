# Attack paths

A small library of privilege-escalation and excessive-agency paths on the Microsoft stack, one YAML file per path, for people who defend AI agents and the
identities behind them. Each path names the permission abused, what must be true for the abuse to work, how to see it, and how to remove it.

It is **defensive**. The `workshop` block of the Track C paths carries the exercise prompts for a **demo tenant**, as in Module 06; no path carries exploitation commands for real environments. The structure is adapted from [pathfinding.cloud](https://pathfinding.cloud/) (Datadog, Apache 2.0), which does
this for AWS IAM; see [SCHEMA.md](./SCHEMA.md) for the fields and what was and was not borrowed.

| Path | What it is | Severity | Category | Validation |
|---|---|---|---|---|
| [xpia-001](./paths/xpia-001.yaml) | Indirect prompt injection (XPIA) via an unlabelled SharePoint document | critical | prompt-injection | documented |
| [builder-001](./paths/builder-001.yaml) | Agent Builder bypass: an ungoverned agent shared with the organization | high | ungoverned-deployment | documented |
| [extraction-001](./paths/extraction-001.yaml) | Model extraction via systematic inference | medium | model-extraction | documented |
| [disclosure-001](./paths/disclosure-001.yaml) | Capability and architecture disclosure | medium | capability-disclosure | documented |
| [hijack-001](./paths/hijack-001.yaml) | Goal hijacking by multi-step session manipulation | high | goal-hijacking | documented |
| [chain-001](./paths/chain-001.yaml) | JadePuffer: agentic ransomware chain | critical | agentic-ransomware | documented |
| [agent-001](./paths/agent-001.yaml) | Graph write permission on the agent identity + a write-capable tool | high | excessive-agency | **observed in lab** |
| [agent-002](./paths/agent-002.yaml) | Credential added to an agent identity blueprint | high | credential-access | documented |
| [agent-003](./paths/agent-003.yaml) | Inheritable permissions on an agent identity blueprint principal | high | principal-access | documented |
| [entra-001](./paths/entra-001.yaml) | `Application.ReadWrite.All` | high | credential-access | not verified |
| [entra-002](./paths/entra-002.yaml) | `AppRoleAssignment.ReadWrite.All` | critical | self-escalation | not verified |
| [entra-003](./paths/entra-003.yaml) | `RoleManagement.ReadWrite.Directory` | critical | self-escalation | not verified |
| [rbac-001](./paths/rbac-001.yaml) | `Microsoft.Authorization/roleAssignments/write` | high | self-escalation | not verified |

The first six are the Track C, Module 06 red-team exercises (the "Agentic Red-Team Map" session companion renders them from these files); `agent-001` to `agent-003` are the identity and tool paths of an Agent 365 agent; the last four are Entra and Azure paths with no Agent 365 specific behaviour.

## How to read the validation column

- **observed in lab**: reproduced end to end, with the evidence named in the file.
- **documented**: described in Microsoft documentation or public research, not reproduced here.
- **not verified**: written from knowledge of the platform; nothing was run. The audit operation names and tenant protections in these files must be checked in
  your tenant before you rely on them.

Detection entries point at queries that already exist in this repository. Where none exists, the file says so under `detection.gaps` instead of inventing one;
turning a gap into a validated query is the most useful contribution (see [CONTRIBUTING.md](./../CONTRIBUTING.md)).

`agent-001` was reproduced in the D3FEND Cyber Range, a companion lab for the same material.
