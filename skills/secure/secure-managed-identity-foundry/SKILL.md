---
name: secure-managed-identity-foundry
version: "1.0"
pillar: secure
subdomain: ms-foundry
description: >-
  Reemplaza credenciales estáticas (API keys) en agentes Azure AI Foundry por
  managed identities, eliminando secretos en código y configuración, y aplicando
  RBAC granular sobre recursos Azure que el agente necesita acceder.
tags: [secure, foundry, managed-identity, azure-rbac, no-secrets, workload-identity]
atlas_techniques: [AML.T0046, AML.T0040]
d3fend_techniques: [D3-CH, D3-UAP]
nist_ai_rmf: [MANAGE-1.3, GOVERN-2.2]
nist_csf: [PR.AA-02, PR.AC-01]
ms_license: [Azure AI Foundry, Azure Subscription]
ms_roles: [Owner o User Access Administrator (para role assignments), Azure AI Developer]
effort_hours: 5
---

## When to use

- Pilar 1 detectó endpoints Foundry con `auth_mode: key`
- Agentes que acceden a Storage, Key Vault, Cognitive Services via API key
- Antes de mover cualquier agente Foundry a producción

## Por qué managed identity sobre API keys

Las API keys son secretos estáticos: no rotan automáticamente, pueden filtrarse
en logs, variables de entorno o repositorios, y no tienen scope granular.
Managed Identity elimina el secreto completamente — Entra ID provee tokens
efímeros automáticamente.

## Tipos de managed identity para agentes Foundry

- **System-assigned**: tied to the resource lifecycle (deleted with the resource). Recommended for single-purpose agents.
- **User-assigned**: independent of the resource, reusable. Recommended when multiple agents share the same permission set.

## Workflow

### Step 1 — Identificar agentes con API key activos

```bash
az ml online-endpoint list \
  --workspace-name {foundry-workspace} \
  --resource-group {resource-group} \
  --query "[?auth_mode=='key'].{Name:name, AuthMode:auth_mode}" \
  --output table
```

### Step 2 — Habilitar system-assigned managed identity en el endpoint

```bash
az ml online-endpoint update \
  --name {endpoint-name} \
  --workspace-name {foundry-workspace} \
  --resource-group {resource-group} \
  --set identity.type=SystemAssigned
```

O crear user-assigned managed identity primero:

```bash
# Crear user-assigned identity
az identity create \
  --name "mi-agent-{agent-name}" \
  --resource-group {resource-group} \
  --location centralus

# Asignar al endpoint
az ml online-endpoint update \
  --name {endpoint-name} \
  --workspace-name {foundry-workspace} \
  --resource-group {resource-group} \
  --set "identity.type=UserAssigned" \
  --set "identity.user_assigned_identities[0].resource_id={managed-identity-resource-id}"
```

### Step 3 — Cambiar auth_mode de key a aad_token

```bash
az ml online-endpoint update \
  --name {endpoint-name} \
  --workspace-name {foundry-workspace} \
  --resource-group {resource-group} \
  --auth-mode aad_token
```

### Step 4 — Asignar RBAC mínimo a la managed identity

Roles por recurso accedido:

```bash
# Storage — solo lectura si el agente solo lee datos
az role assignment create \
  --assignee {managed-identity-principal-id} \
  --role "Storage Blob Data Reader" \
  --scope "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Storage/storageAccounts/{storage-account}"

# Key Vault — solo secrets get si necesita leer secretos
az role assignment create \
  --assignee {managed-identity-principal-id} \
  --role "Key Vault Secrets User" \
  --scope "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.KeyVault/vaults/{kv-name}"

# Cognitive Services — solo usuario si llama a OpenAI / Azure AI
az role assignment create \
  --assignee {managed-identity-principal-id} \
  --role "Cognitive Services User" \
  --scope "/subscriptions/{subscription-id}/resourceGroups/{resource-group}"
```

### Step 5 — Actualizar código del agente para usar DefaultAzureCredential

```python
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Sin secretos — DefaultAzureCredential usa managed identity automáticamente
credential = DefaultAzureCredential()
blob_client = BlobServiceClient(
    account_url="https://{storage}.blob.core.windows.net",
    credential=credential
)
```

### Step 6 — Revocar API keys previas

```bash
# Regenerar keys para invalidar las anteriores
az ml online-endpoint regenerate-keys \
  --name {endpoint-name} \
  --workspace-name {foundry-workspace} \
  --resource-group {resource-group} \
  --key-type primary
```

Verify no external system is still using the keys before revoking them.

## Verification

- [ ] `auth_mode` del endpoint es `aad_token` (no `key`)
- [ ] Managed identity visible en el endpoint: `az ml online-endpoint show --query identity`
- [ ] Role assignments assigned to the managed identity (not to the app SP)
- [ ] Código del agente usa `DefaultAzureCredential` sin secrets hardcoded
- [ ] API keys anteriores invalidadas
- [ ] Test de llamada exitoso con nuevo auth mode

## Implementation notes

- Creating managed identities requires Azure CLI or Bicep/ARM — Graph API does not support direct creation of user-assigned managed identities
- To migrate from client secret to managed identity: create the MI, assign equivalent roles, update the agent configuration, verify function, then revoke the secret
- `sp-*` (service principals with a secret) should be replaced progressively; prioritize those with write permissions over `Mail`, `Files`, or `Sites`
