# Pilar 3 — Secure Access

Objetivo: asegurar cómo los agentes AI se autentican y qué superficie de red exponen,
eliminando credenciales estáticas y restringiendo conectividad al mínimo necesario.

## Secuencia recomendada

```
INPUT: Agentes bajo control formal (output Pilar 2)
        ↓
[1] secure-least-privilege-agent-identity   ← reducir permisos al mínimo real
        ↓
[2] secure-managed-identity-foundry         ← eliminar API keys (Foundry)
        ↓
[3] secure-secret-management-keyvault       ← centralizar secretos residuales
        ↓
[4] secure-network-isolation-agent          ← aislar tráfico de red
        ↓
OUTPUT: Agentes con superficie de ataque reducida → input para Pilar 4 (Protect)
```

## Skills

| Skill | Producto MS | KQL disponible |
|---|---|---|
| `secure-least-privilege-agent-identity` | Entra ID, Graph API | sentinel-permission-usage.kql |
| `secure-managed-identity-foundry` | Azure AI Foundry, Azure CLI | sentinel-managed-identity.kql |
| `secure-secret-management-keyvault` | Azure Key Vault | sentinel-keyvault-audit.kql |
| `secure-network-isolation-agent` | Azure Networking, Foundry | sentinel-network-isolation.kql |

## Decisión: managed identity vs Key Vault

```
¿El recurso es Azure-native y soporta Entra auth?
    ├── Sí → usar Managed Identity (skill: secure-managed-identity-foundry)
    └── No → usar Key Vault (skill: secure-secret-management-keyvault)
             ↓
         ¿El recurso externo soporta rotación automática?
             ├── Sí → configurar Key Vault rotation policy
             └── No → rotar manualmente cada 90 días con alerta
```

## API versions validadas para {workspace-name}

| Recurso | API Version |
|---|---|
| Role Assignments (ARM) | `2022-04-01` |
| Key Vault (ARM) | `2023-07-01` |
| Storage (ARM) | `2023-01-01` |
| SecurityInsights (Sentinel) | `2022-12-01-preview` |

## Restricciones conocidas

| Restricción | Impacto |
|---|---|
| `Sites.Selected` requiere grant explícito al site | No basta con asignar el app role — paso adicional necesario |
| Managed Identity creation: no disponible via Lokka-Microsoft MCP | Usar Azure CLI |
| Copilot Studio sin VNet nativo (licencia estándar) | Usar APIM como proxy o DLP como control alternativo |
| Private Endpoint DNS: requiere zona DNS privada | Sin zona DNS, el endpoint no resuelve desde dentro de VNet |
| `allow_only_approved_outbound` propagación: hasta 30 min | No verificar inmediatamente después del cambio |
