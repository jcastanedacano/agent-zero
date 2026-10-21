# rbac-001 lab infrastructure

Deploys the two role-assignment configurations the [`rbac-001`](../../paths/rbac-001.yaml) lab compares: a managed
identity that can delegate any role at its scope (including Owner), and one whose delegation is constrained by an
[Azure ABAC condition](https://learn.microsoft.com/azure/role-based-access-control/conditions-overview) so it cannot.

**Deploy into a throwaway resource group in a test or demo subscription.** Never run this against a resource group
that holds anything you cannot afford to have escalated into.

## What gets deployed

- `lab-rbac001-vulnerable-<suffix>` — a user-assigned managed identity with **Role Based Access Control Administrator**
  on the resource group, no condition.
- `lab-rbac001-hardened-<suffix>` — the same role, on the same scope, with a condition that denies the assignment
  write when the role being granted is Owner, User Access Administrator or Role Based Access Control Administrator
  itself. The condition is Microsoft's own documented pattern for constraining delegation; see
  [Example: Constrain role assignments to specific role definitions](https://learn.microsoft.com/azure/role-based-access-control/conditions-role-assignments-methods#example-constrain-role-assignments-to-specific-role-definitions-and-roles).

Nothing here performs the escalation. The guided steps that do, with the evidence to expect, are in `rbac-001.yaml`'s
`lab.flow.attack`.

## Deploy

```bash
az group create --name rbac-001-lab --location <region>
az deployment group create \
  --resource-group rbac-001-lab \
  --template-file main.bicep
```

Note the two `clientId` outputs; the guided attack steps use them.

## Teardown

```bash
az group delete --name rbac-001-lab --yes
```

Deleting the resource group removes both identities and both role assignments; nothing else was created.
