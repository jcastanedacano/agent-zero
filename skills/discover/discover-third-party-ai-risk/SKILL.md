---
name: discover-third-party-ai-risk
description: Evaluate and inventory third-party AI agents — ISV extensions, MCP servers, Copilot plugins, and marketplace agents — that operate in the tenant without the same governance controls applied to first-party agents.
pillar: 01-Discover
subdomain: third-party-inventory
tags:
  - third-party
  - supply-chain
  - copilot-plugins
  - mcp-servers
  - shadow-ai
frameworks:
  mitre_atlas:
    - AML.T0010  # ML Supply Chain Compromise
    - AML.T0016  # Obtain Capabilities
  d3fend:
    - D3-SFA    # Software Feature Analysis
    - D3-AC     # Application Configuration
  nist_ai_rmf:
    - GOVERN-1.2  # Organizational risk tolerance — third-party
    - MAP-3.5     # AI supply chain risks
  nist_csf_2:
    - ID.SC-2    # Suppliers and third-party partners assessed
    - ID.RA-6    # Risk responses are chosen and communicated
license_requirements:
  - Microsoft 365 E3 or E5 (Copilot admin center)
  - Microsoft Defender XDR (CloudAppEvents)
  - Entra ID P1 or P2 (App registrations audit)
role_requirements:
  - Global Reader
  - Security Reader
  - Compliance Administrator
---

## Objetivo

Identificar y evaluar todos los agentes de IA de terceros activos en el tenant — plugins de Copilot de ISVs, servidores MCP externos, extensiones de Agent 365, y agentes de Power Platform de proveedores externos — y asignarles un nivel de riesgo antes de que accedan a datos organizacionales.

## Por qué importa

Los agentes de primera parte (creados por el equipo interno) pasan por Entra Agent ID y Copilot Studio governance. Los agentes de terceros tipicamente se instalan desde el marketplace de M365 o se conectan como plugins de Copilot sin el mismo proceso de aprobación — y operan con los mismos permisos de usuario, accediendo a los mismos datos. Un MCP server comprometido o un plugin malicioso del marketplace es funcionalmente equivalente a un agente insider malicioso.

El marco de referencia es OWASP Agentic AI AG05 (Supply Chain Compromise) y MITRE ATLAS AML.T0010 (ML Supply Chain Compromise).

## Workflow

### Paso 1 — Inventariar plugins y extensiones de Copilot de terceros

```powershell
# PowerShell — Microsoft Graph API
# Lista todos los plugins de Copilot activos en el tenant
$graphUri = "https://graph.microsoft.com/v1.0/admin/microsoft365Apps/installations"
$response = Invoke-MgGraphRequest -Uri $graphUri -Method GET
$response.value | Where-Object { $_.publisher -ne "Microsoft" } |
    Select-Object displayName, publisher, appId, installationStatus |
    Sort-Object publisher
```

### Paso 2 — Auditar permisos de aplicaciones de terceros en Entra

```kql
// Entra App registrations de terceros con permisos de alto privilegio
AuditLogs
| where TimeGenerated > ago(30d)
| where OperationName == "Consent to application"
| extend AppName = tostring(TargetResources[0].displayName)
| extend Publisher = tostring(TargetResources[0].type)
| extend ScopesGranted = tostring(TargetResources[0].modifiedProperties[0].newValue)
| extend ConsentedBy = tostring(InitiatedBy.user.userPrincipalName)
| extend IsHighPrivilege = ScopesGranted has_any (
    "Files.ReadWrite.All",
    "Mail.ReadWrite",
    "Sites.ReadWrite.All",
    "Directory.ReadWrite.All",
    "User.ReadWrite.All",
    "Calendars.ReadWrite"
)
| where IsHighPrivilege == true
| project TimeGenerated, AppName, ScopesGranted, ConsentedBy, IsHighPrivilege
| sort by TimeGenerated desc
```

### Paso 3 — Detectar servidores MCP externos conectados a agentes

```kql
// CloudAppEvents — conexiones de agentes a endpoints externos (posibles MCP servers)
CloudAppEvents
| where TimeGenerated > ago(7d)
| where Application in ("Copilot Studio", "Azure AI Foundry", "Microsoft Power Platform")
    and ActionType in ("ConnectorActionExecuted", "ExternalToolInvoked", "MCPServerConnected")
| extend ToolEndpoint = tostring(RawEventData["ToolEndpointUrl"])
| extend ToolPublisher = tostring(RawEventData["ToolPublisher"])
| where isnotempty(ToolEndpoint)
    and ToolEndpoint !has "microsoft.com"
    and ToolEndpoint !has "azure.com"
| summarize
    InvocationCount = count(),
    AffectedAgents = make_set(tostring(RawEventData["AgentId"]), 10),
    LastSeen = max(TimeGenerated)
    by ToolEndpoint, ToolPublisher
| extend RiskNote = "External MCP server or tool — verify publisher and data access scope"
| sort by InvocationCount desc
```

### Paso 4 — Evaluar riesgo de cada agente de terceros

Para cada agente identificado, completar la siguiente tabla:

| Campo | Preguntas clave |
|-------|----------------|
| **Publisher verification** | ¿El publisher está en el marketplace oficial de Microsoft? ¿Tiene certificación? |
| **Data access scope** | ¿Qué permisos de Graph API tiene? ¿Accede a correo, calendario, SharePoint? |
| **Data residency** | ¿Los prompts y respuestas se procesan fuera del tenant de Microsoft? |
| **Audit trail** | ¿Las acciones del agente de terceros aparecen en Purview audit? |
| **Update mechanism** | ¿El código del agente se actualiza automáticamente sin re-aprobación? |
| **Supply chain** | ¿El agente depende de modelos de terceros (no Azure OpenAI)? |

### Paso 5 — Aplicar controles por nivel de riesgo

**Riesgo alto** (acceso a datos sensibles + publisher no verificado):
- Bloquear via Power Platform DLP o CA policy sobre el App ID
- Requerir revisión de seguridad antes de re-activar

**Riesgo medio** (acceso a datos de negocio + publisher verificado):
- Restringir scopes a Read-only donde sea posible
- Configurar alerta de Sentinel sobre volumen de acceso anómalo
- Revisar trimestralmente

**Riesgo bajo** (acceso limitado + publisher Microsoft o certificado):
- Documentar en inventario
- Incluir en ciclo anual de revisión de app registrations

## Verificación

- [ ] Inventario de plugins y extensiones de terceros completado con publisher, scopes y fecha de instalación
- [ ] Todos los agentes de terceros con acceso a datos de alta sensibilidad tienen CA policy o DLP activa
- [ ] Query Q3 de P03 ejecutada y permisos de alto privilegio revisados
- [ ] MCP servers externos identificados y evaluados contra política de allowlist
- [ ] Registros de terceros añadidos al Gap Assessment Template (Domain 1 — Discover)

## Notas de implementación

- Los plugins instalados desde el Microsoft 365 App Store pasan por el proceso de certificación de Microsoft, pero no son inmunes a compromiso post-certificación — el vector de supply chain ataca el código del publisher, no el marketplace.
- Los servidores MCP externos son el vector de mayor riesgo: un servidor MCP comprometido puede inyectar instrucciones maliciosas en cualquier agente que lo invoque, con acceso a todos los datos del usuario que autorizó la conexión.
- Power Platform DLP puede bloquear conectores externos a nivel de entorno, lo que es el control más efectivo para MCP servers no autorizados.
- La tabla `CloudAppEvents` con `ActionType == "ExternalToolInvoked"` puede no existir en todos los tenants según la configuración de Defender — validar disponibilidad antes del workshop.
