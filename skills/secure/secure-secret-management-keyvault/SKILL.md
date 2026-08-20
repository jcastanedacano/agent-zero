---
name: secure-secret-management-keyvault
version: "1.0"
pillar: secure
subdomain: ms-entra
description: >-
  Centraliza y controla secretos, connection strings y API keys de agentes AI
  en Azure Key Vault, aplicando RBAC granular por agente, habilitando rotación
  automática y auditando todo acceso via Sentinel.
tags: [secure, keyvault, secrets, rotation, agent-credentials, azure-rbac]
atlas_techniques: [AML.T0046]
d3fend_techniques: [D3-CH, D3-SCL]
nist_ai_rmf: [MANAGE-1.3, GOVERN-6.2]
nist_csf: [PR.DS-01, PR.AC-01]
ms_license: [Azure Key Vault (incluido en Azure subscription)]
ms_roles: [Key Vault Administrator, User Access Administrator]
effort_hours: 4
---

## When to use

- Agentes que aún requieren secretos estáticos (no migrables a managed identity)
- Connection strings a bases de datos externas, APIs de terceros
- Cuando se detectan secretos hardcoded en código o variables de entorno de agentes
- Como control transitorio mientras se migra a managed identity

## Cuándo NO usar esta skill (preferir managed identity)

If the target resource is in Azure and supports Entra auth, use managed identity
instead of Key Vault. Key Vault is for secrets belonging to external resources
o casos donde managed identity no es viable.

## Workflow

### Step 1 — Auditar secretos actuales del agente

Buscar secretos en:
- Variables de entorno del endpoint / deployment
- Archivos de configuración en el repositorio
- Connection strings en Copilot Studio connectors
- Azure App Configuration si se usa

### Step 2 — Crear o usar Key Vault existente

{workspace-name} has `{kv-name}` available. For new agents, create a dedicated KV:

```bash
az keyvault create \
  --name "kv-agent-{agent-name}" \
  --resource-group {resource-group} \
  --location centralus \
  --enable-rbac-authorization true \
  --sku standard
```

`--enable-rbac-authorization true` — usar RBAC en lugar de access policies (modelo moderno).

### Step 3 — Migrar secretos al Key Vault

```bash
# Por cada secreto del agente
az keyvault secret set \
  --vault-name "kv-agent-{agent-name}" \
  --name "{secret-name}" \
  --value "{secret-value}" \
  --expires "$(date -u -d '+90 days' '+%Y-%m-%dT%H:%M:%SZ')"
```

Usar `--expires` para forzar rotación. 90 días para API keys externas.

### Step 4 — Asignar RBAC por agente (principio de least privilege)

```bash
# Solo el SP del agente puede leer sus propios secretos
az role assignment create \
  --assignee {agent-sp-or-managed-identity-principal-id} \
  --role "Key Vault Secrets User" \
  --scope "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.KeyVault/vaults/kv-agent-{agent-name}"
```

`Key Vault Secrets User` = read secrets only. No listing, no writing, no administration.

### Step 5 — Actualizar agente para leer desde Key Vault

**Python con managed identity:**
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

**Copilot Studio:** usar Azure Key Vault connector (disponible en Power Platform).

### Step 6 — Habilitar diagnósticos y envío a Sentinel

```bash
az monitor diagnostic-settings create \
  --name "kv-to-sentinel" \
  --resource "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.KeyVault/vaults/kv-agent-{agent-name}" \
  --logs '[{"category":"AuditEvent","enabled":true}]' \
  --workspace "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.OperationalInsights/workspaces/{workspace-name}"
```

### Step 7 — Configurar alertas de rotación

```bash
# Alertar 15 días antes de expiración del secreto
az keyvault create-notification \
  --vault-name "kv-agent-{agent-name}" \
  --secret-name "{secret-name}" \
  --days-before-expiry 15
```

O via Event Grid + Logic App para notificación al equipo de seguridad.

## Verification

- [ ] Secretos migrados al Key Vault (no en variables de entorno ni código)
- [ ] RBAC asignado solo al SP/managed identity del agente
- [ ] Agente lee secretos desde KV sin credenciales hardcoded
- [ ] Diagnósticos enviando AuditEvent a Sentinel
- [ ] Fechas de expiración configuradas en todos los secretos
- [ ] Alerta de rotación configurada

## Implementation notes

- API version Key Vault ARM recomendada: `2023-07-01`
- `enable-rbac-authorization` must be `true` to use role assignments on the Key Vault; if the KV uses access policies (legacy model), migrate first
- Automatic secret rotation requires the agent to use the version-neutral URL so Key Vault resolves the current version
- Use the naming convention agent-environment-type for secrets, for example `sales-agent-prod-graph-secret`
