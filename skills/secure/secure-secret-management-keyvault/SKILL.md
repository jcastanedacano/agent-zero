---
name: secure-secret-management-keyvault
version: "1.0"
pillar: secure
subdomain: ms-entra
description: >-
  Centralizes and controls AI agent secrets, connection strings, and API
  keys in Azure Key Vault, applying granular per-agent RBAC, enabling
  automatic rotation, and auditing every access via Sentinel.
tags: [secure, keyvault, secrets, rotation, agent-credentials, azure-rbac]
atlas_techniques: [AML.T0055, AML.T0083]
d3fend_techniques: [D3-CH, D3-SCL]
nist_ai_rmf: [MANAGE-1.3, GOVERN-6.2]
nist_csf: [PR.DS-01, PR.AC-01]
ms_license: [Azure Key Vault (included in Azure subscription)]
ms_roles: [Key Vault Administrator, User Access Administrator]
effort_hours: 4
---

## When to use

- Agents that still require static secrets (not migratable to managed identity)
- Connection strings to external databases, third-party APIs
- When hardcoded secrets are found in agent code or environment variables
- As a transitional control while migrating to managed identity

## When NOT to use this skill (prefer managed identity)

If the target resource is in Azure and supports Entra auth, use managed identity
instead of Key Vault. Key Vault is for secrets belonging to external resources
or cases where managed identity is not viable.

## Workflow

### Step 1 — Audit the agent's current secrets

Look for secrets in:
- Endpoint / deployment environment variables
- Configuration files in the repository
- Connection strings in Copilot Studio connectors
- Azure App Configuration, if used

### Step 2 — Create or reuse an existing Key Vault

Reuse an existing Key Vault if your environment already has one. For new agents, create a dedicated KV:

```bash
az keyvault create \
  --name "kv-agent-{agent-name}" \
  --resource-group {resource-group} \
  --location centralus \
  --enable-rbac-authorization true \
  --sku standard
```

`--enable-rbac-authorization true` — use RBAC instead of access policies (the modern model).

### Step 3 — Migrate secrets into the Key Vault

```bash
# For each of the agent's secrets
az keyvault secret set \
  --vault-name "kv-agent-{agent-name}" \
  --name "{secret-name}" \
  --value "{secret-value}" \
  --expires "$(date -u -d '+90 days' '+%Y-%m-%dT%H:%M:%SZ')"
```

Use `--expires` to force rotation. 90 days for external API keys.

### Step 4 — Assign per-agent RBAC (least privilege principle)

```bash
# Only the agent's SP can read its own secrets
az role assignment create \
  --assignee {agent-sp-or-managed-identity-principal-id} \
  --role "Key Vault Secrets User" \
  --scope "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.KeyVault/vaults/kv-agent-{agent-name}"
```

`Key Vault Secrets User` = read secrets only. No listing, no writing, no administration.

### Step 5 — Update the agent to read from Key Vault

**Python with managed identity:**
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://kv-agent-{agent-name}.vault.azure.net",
    credential=credential
)
secret = client.get_secret("{secret-name}")
api_key = secret.value
```

**Copilot Studio:** use the Azure Key Vault connector (available in Power Platform).

### Step 6 — Enable diagnostics and forward to Sentinel

```bash
az monitor diagnostic-settings create \
  --name "kv-to-sentinel" \
  --resource "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.KeyVault/vaults/kv-agent-{agent-name}" \
  --logs '[{"category":"AuditEvent","enabled":true}]' \
  --workspace "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.OperationalInsights/workspaces/{workspace-name}"
```

### Step 7 — Configure rotation alerts

```bash
# Alert 15 days before secret expiry
az keyvault create-notification \
  --vault-name "kv-agent-{agent-name}" \
  --secret-name "{secret-name}" \
  --days-before-expiry 15
```

Or via Event Grid + Logic App for notification to the security team.

## Verification

- [ ] Secrets migrated to Key Vault (not in environment variables or code)
- [ ] RBAC assigned only to the agent's SP/managed identity
- [ ] Agent reads secrets from KV with no hardcoded credentials
- [ ] Diagnostics sending AuditEvent to Sentinel
- [ ] Expiry dates configured on every secret
- [ ] Rotation alert configured

## Implementation notes

- Recommended Key Vault ARM API version: `2023-07-01`
- `enable-rbac-authorization` must be `true` to use role assignments on the Key Vault; if the KV uses access policies (legacy model), migrate first
- Automatic secret rotation requires the agent to use the version-neutral URL so Key Vault resolves the current version
- Use the naming convention agent-environment-type for secrets, for example `sales-agent-prod-graph-secret`
