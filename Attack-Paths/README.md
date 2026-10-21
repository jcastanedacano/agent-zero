# Attack paths

A small library of privilege-escalation and excessive-agency paths on the Microsoft stack, one YAML file per path, for people who defend AI agents and the
identities behind them. Each path names the permission abused, what must be true for the abuse to work, how to see it, and how to remove it.

It is **defensive**: no exploitation commands. The structure is adapted from [pathfinding.cloud](https://pathfinding.cloud/) (Datadog, Apache 2.0), which does
this for AWS IAM; see [SCHEMA.md](./SCHEMA.md) for the fields and what was and was not borrowed.

| Path | Permission abused | Category | Validation |
|---|---|---|---|
| [agent-001](./paths/agent-001.yaml) | Graph write permission on the agent identity + a write-capable tool | excessive-agency | **observed in lab** |
| [entra-001](./paths/entra-001.yaml) | `Application.ReadWrite.All` | credential-access | not verified |
| [entra-002](./paths/entra-002.yaml) | `AppRoleAssignment.ReadWrite.All` | self-escalation | not verified |
| [entra-003](./paths/entra-003.yaml) | `RoleManagement.ReadWrite.Directory` | self-escalation | not verified |
| [rbac-001](./paths/rbac-001.yaml) | `Microsoft.Authorization/roleAssignments/write` | self-escalation | not verified |

## How to read the validation column

- **observed in lab**: reproduced end to end, with the evidence named in the file.
- **documented**: described in Microsoft documentation or public research, not reproduced here.
- **not verified**: written from knowledge of the platform; nothing was run. The audit operation names and tenant protections in these files must be checked in
  your tenant before you rely on them.

Detection entries point at queries that already exist in this repository. Where none exists, the file says so under `detection.gaps` instead of inventing one;
turning a gap into a validated query is the most useful contribution (see [CONTRIBUTING.md](./../CONTRIBUTING.md)).

`agent-001` was reproduced in the D3FEND Cyber Range, a companion lab for the same material.
