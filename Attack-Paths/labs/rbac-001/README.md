# rbac-001 lab infrastructure

Deploys the two role-assignment configurations the [`rbac-001`](../../paths/rbac-001.yaml) lab compares: a managed
identity that can delegate any role at its scope (including Owner), and one whose delegation is constrained by an
[Azure ABAC condition](https://learn.microsoft.com/azure/role-based-access-control/conditions-overview) so it cannot.
Each identity is attached to its own Azure Container Instance running the Azure CLI, so the guided steps have
somewhere to `exec` into and sign in as that identity.

**Deploy into a throwaway resource group in a test or demo subscription.** Never run this against a resource group
that holds anything you cannot afford to have escalated into.

## What gets deployed

- `lab-rbac001-vulnerable-<suffix>` — a user-assigned managed identity with **Role Based Access Control Administrator**
  on the resource group, no condition — and `lab-rbac001-vulnerable-cli-<suffix>`, an Azure Container Instance
  (`mcr.microsoft.com/azure-cli`) with that identity attached.
- `lab-rbac001-hardened-<suffix>` — the same role, on the same scope, with a condition that denies the assignment
  write when the role being granted is Owner, User Access Administrator or Role Based Access Control Administrator
  itself — and `lab-rbac001-hardened-cli-<suffix>`, its own container with that identity attached. The condition is
  Microsoft's own documented pattern for constraining delegation; see
  [Example: Constrain role assignments to specific role definitions](https://learn.microsoft.com/azure/role-based-access-control/conditions-role-assignments-methods#example-constrain-role-assignments-to-specific-role-definitions-and-roles).
  It uses `ForAnyOfAllValues:GuidNotEquals`, not `ForAnyOfAnyValues` — the single role being requested must be
  not-equal to *every* blocked role ID for the write to be allowed, so it is blocked the moment it matches *any one*
  of them.

Both containers idle (`sleep infinity`) until you exec into them. Nothing here performs the escalation itself. The
guided steps that do, with the evidence to expect, are in `rbac-001.yaml`'s `lab.flow.attack`.

## Deploy

```bash
az group create --name rbac-001-lab --location <region>
az deployment group create \
  --resource-group rbac-001-lab \
  --template-file main.bicep
```

Note the `vulnerableClientId`, `vulnerableContainerGroup`, `hardenedClientId` and `hardenedContainerGroup` outputs;
the guided attack steps use them. Stay signed in as the account that ran this deployment — the guided steps sign
into the containers *from* this session, and you return to it for teardown.

## Run as each identity

```bash
az container exec --resource-group rbac-001-lab --name <vulnerableContainerGroup> --exec-command "/bin/sh"
# inside the container:
az login --identity --client-id <vulnerableClientId>
```

Azure CLI's managed-identity sign-in needs `--client-id` (not `--username`) to pick one identity when more than one
*could* be attached; this template attaches only one per container, but passing it explicitly avoids relying on
that. Exit the container shell (`exit`) when done with that identity — it does not affect the deployment account's
own session on your machine, which stays signed in throughout.

## Teardown

Run this from your own session (the one that deployed the template), not from inside either container — neither
identity's role includes deleting a resource group:

```bash
az group delete --name rbac-001-lab --yes
```

Deleting the resource group removes both identities, both containers and both role assignments; nothing else was
created.
