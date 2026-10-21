# Attack path schema v1.1

v1.1 adds `severity`, `surface`, `graph`, `workshop`, `frameworks.atlas` and `frameworks.owasp`, and widens `category`, so the 6 Track C red-team exercises and the Agent 365 identity-plane paths fit the same file. Files written for v1.0 stay valid.

One YAML file per privilege-escalation or excessive-agency path on the Microsoft stack. The structure is adapted from the
[pathfinding.cloud](https://pathfinding.cloud/) AWS IAM path library by Datadog ([Apache 2.0](https://github.com/DataDog/pathfinding.cloud/blob/main/LICENSE)):
the idea of one structured file per path, with required and additional permissions, prerequisites, limitations and a recommendation, is theirs.
The fields below are this repository's own. No pathfinding.cloud content was copied: every path here is Microsoft-specific.

This library is **defensive**. A path says what permission is abused, what must be true for the abuse to work, how to see it and how to remove it. It carries
no exploitation commands.

## File naming and ids

`{area}-{number}.yaml` in `paths/`, for example `agent-001.yaml`, `entra-001.yaml`, `rbac-001.yaml`. The id is the file name and is unique.

| Area | Covers |
|---|---|
| `agent` | An AI agent's identity and tools: excessive agency |
| `entra` | Microsoft Entra ID and Microsoft Graph application permissions and directory roles |
| `rbac` | Azure role-based access control on resources |

## Required fields

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Same as the file name |
| `name` | string | The permission abused, with ` + ` between several |
| `category` | enum | `excessive-agency`, `self-escalation`, `credential-access`, `principal-access`, `prompt-injection`, `model-extraction`, `capability-disclosure`, `goal-hijacking`, `ungoverned-deployment` or `agentic-ransomware` |
| `severity` | enum | `critical`, `high`, `medium` or `low` |
| `surface` | enum | Where the path lives: `agent-tool`, `agent-identity`, `agent-content`, `agent-conversation`, `agent-lifecycle`, `model-endpoint`, `directory` or `azure-resource` |
| `platform` | list | Microsoft services involved (`foundry`, `entra`, `graph`, `azure-rbac`, `sharepoint`) |
| `permissions.required` | list of `{permission, resourceConstraints}` | The minimum the abusing principal needs |
| `description` | string | How the abuse works and what it yields |
| `recommendation` | string (multi-line) | How to prevent it and how to detect it |
| `validation` | object | What has actually been verified (see below) |

## Optional fields

| Field | Meaning |
|---|---|
| `graph` | `nodes` (`id`, `label`, `sub`, `type`: `attacker`, `asset`, `agent` or `victim`, optional `x`, `y`) and `edges` (`from`, `to`, `label`): the attack as a flow |
| `workshop` | The hands-on exercise: `estimatedMinutes`, `steps`, `payload`, `verificationQuery`, `expected`, `ifItFails`, `documentationQuestions`, `source`. For demo tenants only, as in Track C |
| `permissions.additional` | Read or list permissions that help discovery and could come from a separate principal |
| `prerequisites` | What must exist in the tenant for the path to work |
| `limitations` | When the path yields full access, when only partial, and what blocks it |
| `detection` | Where to look: `library` (existing queries in this repository) and `gaps` (what has no query yet) |
| `references` | Primary documentation and research |
| `frameworks` | `attack` (MITRE ATT&CK), `atlas` (MITRE ATLAS) and `owasp` (Agentic Top 10 `ASI`, LLM Top 10 `LLM`) ids, checked against the source |

## `validation`

Honesty about evidence is mandatory, as in the KQL library.

```yaml
validation:
  status: observed-in-lab | documented | not-verified
  date: 2026-10-20          # when the status was last checked
  notes: What was seen, where, and what was NOT checked.
```

- `observed-in-lab`: reproduced end to end in a lab, with the evidence named.
- `documented`: described in Microsoft documentation or public research, not reproduced here.
- `not-verified`: written from knowledge of the platform; nothing was run.

A `detection.library` entry names an existing query: a file path, or a library query id such as `P03-Q6`. A path with no query says so under `detection.gaps` instead of inventing one.
