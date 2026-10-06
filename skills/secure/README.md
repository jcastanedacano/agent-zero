# Pillar 3 — Secure Access

Objective: secure how AI agents authenticate and what network surface they expose,
eliminating static credentials and restricting connectivity to the minimum necessary.

## Recommended sequence

```mermaid
flowchart TD
    IN[/"Agents under formal control (Pillar 2 output)"/] --> A["<b>1</b> secure-least-privilege-agent-identity<br/>reduce permissions to the real minimum"]
    A --> B["<b>2</b> secure-managed-identity-foundry<br/>eliminate API keys (Foundry)"]
    B --> C["<b>3</b> secure-secret-management-keyvault<br/>centralize residual secrets"]
    C --> D["<b>4</b> secure-network-isolation-agent<br/>isolate network traffic"]
    D --> OUT[/"Agents with a reduced attack surface"/]
    OUT --> P4["Pillar 4 Protect"]
    X1["secure-ca-policy-agents<br/>Conditional Access for agent identities"] -.-> A

    classDef skill fill:#0078D4,stroke:#333,color:#fff
    classDef side fill:#e6f2fb,stroke:#0078D4,color:#24292f
    classDef art fill:#FF8C00,stroke:#333,color:#24292f
    class A,B,C,D skill
    class X1 side
    class IN,OUT art
```

**How to read it.** The order goes from who the agent is (permissions, then credentials) to where it can connect. Least privilege comes first because every later control is easier to reason about once the permissions are small. `secure-ca-policy-agents` sits beside the sequence: the Conditional Access policy for agent identities comes right after an agent is registered with Entra Agent ID.


## Skills

| Skill | MS product | KQL available |
|---|---|---|
| `secure-least-privilege-agent-identity` | Entra ID, Graph API | sentinel-permission-usage.kql |
| `secure-managed-identity-foundry` | Microsoft Foundry, Entra ID, Azure CLI | sentinel-managed-identity.kql |
| `secure-secret-management-keyvault` | Azure Key Vault | sentinel-keyvault-audit.kql |
| `secure-network-isolation-agent` | Azure Networking, Microsoft Foundry, Power Platform | sentinel-network-isolation.kql |
| `secure-ca-policy-agents` | Entra ID Conditional Access, Graph API | No |

## Decision: managed identity vs Key Vault

```mermaid
flowchart TD
    Q1{"Is the resource Azure-native<br/>and does it support Entra authentication?"}
    Q1 -- "Yes" --> MI["Use a managed identity<br/>secure-managed-identity-foundry"]
    Q1 -- "No" --> KV["Use Key Vault<br/>secure-secret-management-keyvault"]
    KV --> Q2{"Does the external resource support<br/>automatic rotation?"}
    Q2 -- "Yes" --> R1["Automate rotation: Event Grid near-expiry event<br/>and a function (secrets have no native rotation policy)"]
    Q2 -- "No" --> R2["Rotate manually every 90 days<br/>and use the near-expiry event as the reminder"]

    classDef good fill:#107C10,stroke:#333,color:#fff
    classDef warn fill:#FF8C00,stroke:#333,color:#24292f
    class MI,R1 good
    class KV,R2 warn
```


## API versions validated against a live Sentinel workspace

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
| Copilot Studio network controls need a Managed Environment | Virtual Network support (outbound) and the IP firewall (inbound, preview) both require it; the IP firewall is not enforced on the Teams and Microsoft Copilot channels |
| Private Endpoint DNS: requires a private DNS zone | Without the DNS zone, the endpoint does not resolve from inside the VNet. A Foundry resource uses three zones: `privatelink.cognitiveservices.azure.com`, `privatelink.openai.azure.com` and `privatelink.services.ai.azure.com` |
| Foundry outbound isolation is decided when the resource is created | Network injection and the managed network cannot be added to an existing Foundry resource or changed later: redeploy |
| Foundry key access is the account property `disableLocalAuth` | The change can take up to several hours to be enforced: verify with an HTTP 401 on the old key |
