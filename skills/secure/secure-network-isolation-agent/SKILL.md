---
name: secure-network-isolation-agent
version: "1.0"
pillar: secure
subdomain: ms-foundry
description: >-
  Implementa aislamiento de red para agentes Azure AI Foundry y Copilot Studio
  usando Private Endpoints, VNet integration y NSG rules, limitando la superficie
  de red expuesta y previniendo exfiltración via canales de red no autorizados.
tags: [secure, network, private-endpoint, vnet, nsg, foundry, isolation]
atlas_techniques: [AML.T0048, AML.T0040]
d3fend_techniques: [D3-NI, D3-NTF, D3-ANCI]
nist_ai_rmf: [MANAGE-1.3, GOVERN-6.2]
nist_csf: [PR.AC-05, DE.CM-01]
ms_license: [Azure Subscription, Azure AI Foundry]
ms_roles: [Network Contributor, Azure AI Developer]
effort_hours: 8
---

## When to use

- Agentes Foundry que procesan datos confidenciales
- When the risk register flags agents with generic HTTP connectors (unknown destination)
- A compliance requirement that AI traffic must not egress to the public internet

## Alcance de esta skill

Cubre aislamiento de red para:
1. Azure AI Foundry endpoints (Private Endpoint + VNet)
2. Copilot Studio (a través de controles en Power Platform / salida vía APIM)

Para Copilot Studio el aislamiento completo requiere Power Platform environments
con Virtual Network support (licencia premium) — documentado en Paso 4.

## Workflow

### Step 1 — Evaluar superficie de red actual

```bash
# Ver configuración de red del workspace Foundry
az ml workspace show \
  --name {foundry-workspace} \
  --resource-group {resource-group} \
  --query "{PublicAccess:publicNetworkAccess, ManagedNetwork:managedNetwork}"
```

`publicNetworkAccess: Enabled` = superficie expuesta a internet — objetivo a cambiar.

### Step 2 — Habilitar managed network isolation en Foundry workspace

```bash
az ml workspace update \
  --name {foundry-workspace} \
  --resource-group {resource-group} \
  --managed-network allow_only_approved_outbound
```

Modos disponibles:
- `disabled`: sin aislamiento (default)
- `allow_internet_outbound`: permite salida a internet (modo básico)
- `allow_only_approved_outbound`: solo destinos explícitamente aprobados (recomendado)

### Step 3 — Crear Private Endpoint para el workspace

```bash
# Deshabilitar acceso público
az ml workspace update \
  --name {foundry-workspace} \
  --resource-group {resource-group} \
  --public-network-access Disabled

# Crear Private Endpoint
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

### Step 4 — Configurar outbound rules para destinos aprobados

Para `allow_only_approved_outbound`, declarar destinos explícitos:

```bash
# Permitir solo Azure OpenAI del tenant (no internet abierto)
az ml workspace outbound-rule set \
  --workspace-name {foundry-workspace} \
  --resource-group {resource-group} \
  --rule '{"type":"PrivateEndpoint","destination":{"serviceResourceId":"{openai-resource-id}","subresourceTarget":"account"}}'
```

### Step 5 — NSG para la subnet del agente

```bash
# Crear NSG
az network nsg create \
  --name "nsg-agents-{env}" \
  --resource-group {resource-group} \
  --location centralus

# Regla: denegar tráfico saliente a internet excepto Azure services
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

# Regla: permitir Azure (antes de la de denegación)
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

Copilot Studio no soporta VNet nativo en licencias estándar.
Opciones de mitigación disponibles:

**Opción A — APIM como gateway**: enrutar llamadas de Copilot Studio a backends
a través de Azure API Management desplegado en VNet. El agente llama a APIM,
APIM llama al backend interno.

**Opción B — Power Platform Managed Environment + VNet**: requiere
Power Apps Premium y configuración de VNet support en el environment.
Disponible para tenants con licencias enterprise.

**Opción C — Restricción de conectores por DLP**: controlar qué conectores
puede usar Copilot Studio (ver skill `govern-dlp-policy-copilot-prompts`).
Menos control de red pero más pragmático sin licencias adicionales.

## Verification

- [ ] `publicNetworkAccess: Disabled` en workspace Foundry
- [ ] Private Endpoint creado y conectado (`provisioningState: Succeeded`)
- [ ] DNS privado resolviendo el workspace endpoint
- [ ] NSG aplicado a subnet con regla de denegación de internet
- [ ] Test de llamada al endpoint exitoso desde dentro de VNet
- [ ] Test de llamada desde internet falla (expected)

## Implementation notes

- `allow_only_approved_outbound` in Azure AI Foundry can take up to 30 minutes to propagate — verify state before assuming the control is active
- Private Endpoint requiere zona DNS privada para resolver correctamente: `privatelink.api.azureml.ms` y `privatelink.notebooks.azure.net`
- In environments without a configured VNet: start with `publicNetworkAccess: Disabled` on Foundry resources as a first step, and plan the VNet and Private Endpoint afterward
