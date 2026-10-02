---
name: secure-network-isolation-agent
version: "1.0"
pillar: secure
subdomain: ms-foundry
description: >-
  Implements network isolation for Azure AI Foundry and Copilot Studio agents
  using Private Endpoints, VNet integration, and NSG rules, limiting the
  exposed network surface and preventing exfiltration via unauthorized
  network channels.
tags: [secure, network, private-endpoint, vnet, nsg, foundry, isolation]
atlas_techniques: [AML.T0025, AML.T0040]
d3fend_techniques: [D3-NI, D3-NTF, D3-ANCI]
nist_ai_rmf: [MANAGE-1.3, GOVERN-6.2]
nist_csf: [PR.AC-05, DE.CM-01]
ms_license: [Azure Subscription, Azure AI Foundry]
ms_roles: [Network Contributor, Azure AI Developer]
effort_hours: 8
---

## When to use

- Foundry agents that process confidential data
- When the risk register flags agents with generic HTTP connectors (unknown destination)
- A compliance requirement that AI traffic must not egress to the public internet

## Scope of this skill

Covers network isolation for:
1. Azure AI Foundry endpoints (Private Endpoint + VNet)
2. Copilot Studio (through Power Platform controls / egress via APIM)

For Copilot Studio, full isolation requires Power Platform environments
with Virtual Network support (premium license) — documented in Step 6.

## Workflow

### Step 1 — Assess the current network surface

```bash
# View the network configuration of the Foundry workspace
az ml workspace show \
  --name {foundry-workspace} \
  --resource-group {resource-group} \
  --query "{PublicAccess:publicNetworkAccess, ManagedNetwork:managedNetwork}"
```

`publicNetworkAccess: Enabled` = surface exposed to the internet — the target to change.

### Step 2 — Enable managed network isolation on the Foundry workspace

```bash
az ml workspace update \
  --name {foundry-workspace} \
  --resource-group {resource-group} \
  --managed-network allow_only_approved_outbound
```

Available modes:
- `disabled`: no isolation (default)
- `allow_internet_outbound`: allows internet egress (basic mode)
- `allow_only_approved_outbound`: only explicitly approved destinations (recommended)

### Step 3 — Create a Private Endpoint for the workspace

```bash
# Disable public access
az ml workspace update \
  --name {foundry-workspace} \
  --resource-group {resource-group} \
  --public-network-access Disabled

# Create the Private Endpoint
az network private-endpoint create \
  --name "pe-foundry-{agent-name}" \
  --resource-group {resource-group} \
  --vnet-name {vnet-name} \
  --subnet {subnet-name} \
  --private-connection-resource-id $(az ml workspace show \
    --name {foundry-workspace} \
    --resource-group {resource-group} \
    --query id -o tsv) \
  --group-id amlworkspace \
  --connection-name "foundry-private-conn"
```

### Step 4 — Configure outbound rules for approved destinations

For `allow_only_approved_outbound`, declare explicit destinations:

```bash
# Allow only the tenant's Azure OpenAI (not open internet)
az ml workspace outbound-rule set \
  --workspace-name {foundry-workspace} \
  --resource-group {resource-group} \
  --rule '{"type":"PrivateEndpoint","destination":{"serviceResourceId":"{openai-resource-id}","subresourceTarget":"account"}}'
```

### Step 5 — NSG for the agent subnet

```bash
# Create the NSG
az network nsg create \
  --name "nsg-agents-{env}" \
  --resource-group {resource-group} \
  --location centralus

# Rule: deny outbound traffic to the internet except Azure services
az network nsg rule create \
  --name "Deny-Internet-Outbound" \
  --nsg-name "nsg-agents-{env}" \
  --resource-group {resource-group} \
  --priority 1000 \
  --direction Outbound \
  --access Deny \
  --protocol "*" \
  --destination-address-prefixes Internet \
  --destination-port-ranges "*"

# Rule: allow Azure (evaluated before the deny rule)
az network nsg rule create \
  --name "Allow-AzureCloud-Outbound" \
  --nsg-name "nsg-agents-{env}" \
  --resource-group {resource-group} \
  --priority 900 \
  --direction Outbound \
  --access Allow \
  --protocol "*" \
  --destination-address-prefixes AzureCloud \
  --destination-port-ranges "*"
```

### Step 6 — Copilot Studio (Power Platform VNet)

Copilot Studio does not support native VNet on standard licenses.
Available mitigation options:

**Option A — APIM as gateway**: route Copilot Studio calls to backends
through Azure API Management deployed in a VNet. The agent calls APIM,
APIM calls the internal backend.

**Option B — Power Platform Managed Environment + VNet**: requires
Power Apps Premium and VNet support configuration on the environment.
Available for tenants with enterprise licenses.

**Option C — Connector restriction via DLP**: control which connectors
Copilot Studio can use (see the `govern-dlp-policy-copilot-prompts` skill).
Less network control, but more pragmatic without additional licenses.

## Verification

- [ ] `publicNetworkAccess: Disabled` on the Foundry workspace
- [ ] Private Endpoint created and connected (`provisioningState: Succeeded`)
- [ ] Private DNS resolving the workspace endpoint
- [ ] NSG applied to the subnet with an internet-deny rule
- [ ] Endpoint call test succeeds from inside the VNet
- [ ] Endpoint call test fails from the internet (expected)

## Implementation notes

- `allow_only_approved_outbound` in Azure AI Foundry can take up to 30 minutes to propagate — verify state before assuming the control is active
- Private Endpoint requires a private DNS zone to resolve correctly: `privatelink.api.azureml.ms` and `privatelink.notebooks.azure.net`
- In environments without a configured VNet: start with `publicNetworkAccess: Disabled` on Foundry resources as a first step, and plan the VNet and Private Endpoint afterward
