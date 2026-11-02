# Attack path schema v1.2

v1.2 adds the optional `lab` block (below): a hands-on exercise per path (objective, resources created, principals and permissions, setup, guided attack, cleanup, teardown, defend, recorded run) adapted to Azure, Entra, Agent 365 and demo tenants. Files without `lab` stay valid.

v1.1 adds `severity`, `surface`, `graph`, `workshop`, `frameworks.atlas` and `frameworks.owasp`, and widens `category`, so the 6 Track C red-team exercises and the Agent 365 identity-plane paths fit the same file. Files written for v1.0 stay valid.

One YAML file per privilege-escalation or excessive-agency path on the Microsoft stack: one structured file per path, with required and additional permissions, prerequisites, limitations and a recommendation. Every path here is Microsoft-specific.

This library is **defensive**. A path says what permission is abused, what must be true for the abuse to work, how to see it and how to remove it. It carries
no exploitation commands.

## File naming and ids

`{area}-{number}.yaml` in `paths/`, for example `agent-001.yaml`, `entra-001.yaml`, `rbac-001.yaml`. The id is the file name and is unique. A path's optional `iac` lab files live in `labs/<id>/`, matching the same id.

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
| `category` | enum | `excessive-agency`, `self-escalation`, `credential-access`, `principal-access`, `prompt-injection`, `model-extraction`, `capability-disclosure`, `goal-hijacking`, `ungoverned-deployment`, `agentic-ransomware`, `membership-inference`, `model-inversion`, `identity-laundering`, `privilege-escalation` or `identity-takeover` |
| `severity` | enum | `critical`, `high`, `medium` or `low` |
| `surface` | enum | Where the path lives: `agent-tool`, `agent-identity`, `agent-content`, `agent-conversation`, `agent-lifecycle`, `model-endpoint`, `directory`, `azure-resource`, `delegated-access` or `pim-activation` |
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

## `lab` (optional, v1.2)

The exercise that goes with a path: either a documented exercise in a demo tenant (`kind: tenant-exercise`) or reproducible infrastructure (`kind: iac`) deployed from files in this repository.

An `iac` lab's deployable files live under `labs/<id>/` (for example [`labs/rbac-001/`](./labs/rbac-001/)), next to `paths/<id>.yaml`, and are referenced from `architecture.resources` with `createdBy: iac`. `flow.setup` names the deploy command and `flow.teardown` the command that removes everything the files created; neither the YAML nor the deployable files perform the guided attack itself — that stays a human-run step in `flow.attack`, same as a `tenant-exercise` lab.

| Field | Meaning |
|---|---|
| `kind` | `tenant-exercise` (manual steps in a demo tenant) or `iac` (reproducible deployment) |
| `effects` | **Required.** `read-only`, `modifies-resources` or `potential-impact` (see below) |
| `title`, `objective` | What the exercise shows, in one sentence each |
| `scopeNote` | Optional. Only when this lab reproduces less than the path describes (a subset of a multi-stage chain, for example): what is in scope, what is deliberately left out, and why — so the gap reads as a stated boundary, not a discrepancy |
| `estimatedMinutes`, `costEstimate`, `licenses` | Time, cost (say when it was not measured) and what the tenant needs |
| `safety` | **Required.** `scope` (demo tenant only), `writes` (what it changes) and `revert` (how to undo it) |
| `architecture.summary` | The setup in a few lines |
| `architecture.resources` | What exists: `name`, `purpose`, `createdBy` (`manual`, `iac` or `existing`) |
| `architecture.principals` | Who acts, with `required` and `helpful` permissions |
| `flow.setup` | Preparation steps |
| `flow.attack` | The guided steps. **Each step has `step` and `evidence`**: what must be seen for that step to count, so an exercise can be checked, not just followed |
| `flow.cleanup`, `flow.teardown` | Undo what the attack changed; remove what the setup created |
| `defend.prevent` | Controls that stop it |
| `defend.detect` | `queries` (library ids such as `P03-Q12`), `files` (query files) and `events` (`source`, `operation`, `note`) |
| `transcript` | Optional. `summary` and `observations` of a real run, with identifiers removed |
| `validation` | **Required.** Same meaning as the path's `validation`, for the lab: what was and was not replayed |

A lab never reuses the path's evidence as its own: `lab.validation` says whether this exercise was run, and a path observed in a lab can still have a lab whose provisioning steps were only documented.

`effects` classifies what the guided attack actually does to the tenant, derived from `flow.attack` and `safety.writes` — never from the title:

- `read-only`: nothing is created or changed (same bar as `safety.writes: None.`).
- `modifies-resources`: creates or changes something contained to the demo tenant — a credential, a role or permission assignment, a resource — that `safety.revert` undoes.
- `potential-impact`: the guided attack itself does something with consequences beyond the directory, such as sending content to an external recipient or a bulk file operation, even when `safety.revert` can still clean it up afterwards.
