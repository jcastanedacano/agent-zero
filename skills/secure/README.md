# Pillar 3 — Secure Access

Objective: secure how AI agents authenticate and what network surface they expose,
eliminating static credentials and restricting connectivity to the minimum necessary.

## Recommended sequence

```
INPUT: Agents under formal control (Pillar 2 output)
        ↓
[1] secure-least-privilege-agent-identity   ← reduce permissions to the real minimum
        ↓
[2] secure-managed-identity-foundry         ← eliminate API keys (Foundry)
        ↓
[3] secure-secret-management-keyvault       ← centralize residual secrets
        ↓
[4] secure-network-isolation-agent          ← isolate network traffic
        ↓
OUTPUT: Agents with a reduced attack surface → input for Pillar 4 (Protect)
```

## Skills

| Skill | MS product | KQL available |
|---|---|---|
| `secure-least-privilege-agent-identity` | Entra ID, Graph API | sentinel-permission-usage.kql |
| `secure-managed-identity-foundry` | Azure AI Foundry, Azure CLI | sentinel-managed-identity.kql |
| `secure-secret-management-keyvault` | Azure Key Vault | sentinel-keyvault-audit.kql |
| `secure-network-isolation-agent` | Azure Networking, Foundry | sentinel-network-isolation.kql |

## Decision: managed identity vs Key Vault

```
Is the resource Azure-native and does it support Entra auth?
    ├── Yes → use Managed Identity (skill: secure-managed-identity-foundry)
    └── No → use Key Vault (skill: secure-secret-management-keyvault)
             ↓
         Does the external resource support automatic rotation?
             ├── Yes → configure a Key Vault rotation policy
             └── No → rotate manually every 90 days with an alert
```

## API versions validated for {workspace-name}

| Resource | API Version |
|---|---|
| Role Assignments (ARM) | `2022-04-01` |
| Key Vault (ARM) | `2023-07-01` |
| Storage (ARM) | `2023-01-01` |
| SecurityInsights (Sentinel) | `2022-12-01-preview` |

## Known constraints

| Constraint | Impact |
|---|---|
| `Sites.Selected` requires an explicit site grant | Assigning the app role is not enough — an extra step is required |
| Managed Identity creation: not available via Lokka-Microsoft MCP | Use Azure CLI |
| Copilot Studio without native VNet (standard license) | Use APIM as a proxy, or DLP as an alternative control |
| Private Endpoint DNS: requires a private DNS zone | Without the DNS zone, the endpoint does not resolve from inside the VNet |
| `allow_only_approved_outbound` propagation: up to 30 min | Do not verify immediately after the change |
