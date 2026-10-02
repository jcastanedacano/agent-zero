---
name: secure-managed-identity-foundry
version: "1.0"
pillar: secure
subdomain: ms-foundry
description: >-
  Replaces static credentials (API keys) in Azure AI Foundry agents with
  managed identities, eliminating secrets in code and configuration, and
  applying granular RBAC over the Azure resources the agent needs to access.
tags: [secure, foundry, managed-identity, azure-rbac, no-secrets, workload-identity]
atlas_techniques: [AML.T0055, AML.T0040]
d3fend_techniques: [D3-CH, D3-UAP]
nist_ai_rmf: [MANAGE-1.3, GOVERN-2.2]
nist_csf: [PR.AA-02, PR.AC-01]
ms_license: [Azure AI Foundry, Azure Subscription]
ms_roles: [Owner or User Access Administrator (for role assignments), Azure AI Developer]
effort_hours: 5
---

## When to use

- Pillar 1 detected Foundry endpoints with `auth_mode: key`
- Agents that access Storage, Key Vault, or Cognitive Services via API key
- Before moving any Foundry agent to production

## Why managed identity over API keys

API keys are static secrets: they do not rotate automatically, they can leak
into logs, environment variables, or repositories, and they have no granular
scope. Managed Identity eliminates the secret entirely — Entra ID provides
ephemeral tokens automatically.

## Managed identity types for Foundry agents

- **System-assigned**: tied to the resource lifecycle (deleted with the resource). Recommended for single-purpose agents.
- **User-assigned**: independent of the resource, reusable. Recommended when multiple agents share the same permission set.

## Workflow

### Step 1 — Identify agents with active API keys

```bash
az ml online-endpoint list \
  --workspace-name {foundry-workspace} \
  --resource-group {resource-group} \
  --query "[?auth_mode=='key'].{Name:name, AuthMode:auth_mode}" \
  --output table
```

### Step 2 — Enable system-assigned managed identity on the endpoint

```bash
az ml online-endpoint update \
  --name {endpoint-name} \
  --workspace-name {foundry-workspace} \
  --resource-group {resource-group} \
  --set identity.type=SystemAssigned
```

Or create the user-assigned managed identity first:

```bash
# Create the user-assigned identity
az identity create \
  --name "mi-agent-{agent-name}" \
  --resource-group {resource-group} \
  --location centralus

# Assign it to the endpoint
az ml online-endpoint update \
  --name {endpoint-name} \
  --workspace-name {foundry-workspace} \
  --resource-group {resource-group} \
  --set "identity.type=UserAssigned" \
  --set "identity.user_assigned_identities[0].resource_id={managed-identity-resource-id}"
```

### Step 3 — Change auth_mode from key to aad_token

```bash
az ml online-endpoint update \
  --name {endpoint-name} \
  --workspace-name {foundry-workspace} \
  --resource-group {resource-group} \
  --auth-mode aad_token
```

### Step 4 — Assign minimal RBAC to the managed identity

Roles by accessed resource:

```bash
# Storage — read-only if the agent only reads data
az role assignment create \
  --assignee {managed-identity-principal-id} \
  --role "Storage Blob Data Reader" \
  --scope "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Storage/storageAccounts/{storage-account}"

# Key Vault — secrets-get only if it needs to read secrets
az role assignment create \
  --assignee {managed-identity-principal-id} \
  --role "Key Vault Secrets User" \
  --scope "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.KeyVault/vaults/{kv-name}"

# Cognitive Services — user role only if calling OpenAI / Azure AI
az role assignment create \
  --assignee {managed-identity-principal-id} \
  --role "Cognitive Services User" \
  --scope "/subscriptions/{subscription-id}/resourceGroups/{resource-group}"
```

### Step 5 — Update the agent's code to use DefaultAzureCredential

```python
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# No secrets — DefaultAzureCredential uses the managed identity automatically
credential = DefaultAzureCredential()
blob_client = BlobServiceClient(
    account_url="https://{storage}.blob.core.windows.net",
    credential=credential
)
```

### Step 6 — Revoke previous API keys

```bash
# Regenerate keys to invalidate the old ones
az ml online-endpoint regenerate-keys \
  --name {endpoint-name} \
  --workspace-name {foundry-workspace} \
  --resource-group {resource-group} \
  --key-type primary
```

Verify no external system is still using the keys before revoking them.

## Verification

- [ ] The endpoint's `auth_mode` is `aad_token` (not `key`)
- [ ] Managed identity visible on the endpoint: `az ml online-endpoint show --query identity`
- [ ] Role assignments assigned to the managed identity (not to the app SP)
- [ ] Agent code uses `DefaultAzureCredential` with no hardcoded secrets
- [ ] Previous API keys invalidated
- [ ] Call test succeeds with the new auth mode

## Implementation notes

- Creating managed identities requires Azure CLI or Bicep/ARM — Graph API does not support direct creation of user-assigned managed identities
- To migrate from client secret to managed identity: create the MI, assign equivalent roles, update the agent configuration, verify function, then revoke the secret
- `sp-*` (service principals with a secret) should be replaced progressively; prioritize those with write permissions over `Mail`, `Files`, or `Sites`
