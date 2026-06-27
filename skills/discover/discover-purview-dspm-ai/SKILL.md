---
name: discover-purview-dspm-ai
version: "1.0"
pillar: discover
subdomain: ms-purview
description: >-
  Activa y configura Purview DSPM for AI para mapear interacciones de agentes
  con datos sensibles en Microsoft 365, generando visibilidad de qué datos
  acceden los agentes y qué riesgos de exposición existen antes de escalar.
tags: [discover, purview, dspm, ai-hub, data-classification, oversharing]
atlas_techniques: [AML.T0056, AML.T0037]
d3fend_techniques: [D3-DAM, D3-SFA]
nist_ai_rmf: [MAP-1.1, MAP-2.1, GOVERN-1.1]
nist_csf: [ID.AM-05, ID.RA-01]
ms_license: [Microsoft 365 E5, Microsoft 365 E5 Compliance]
ms_roles: [Compliance Administrator, Security Reader]
effort_hours: 2
---

## Cuándo usar

- Como primer paso antes de habilitar retrieval de SharePoint en cualquier agente
- Cuando hay sospecha de oversharing en fuentes de conocimiento de agentes existentes
- En auditorías periódicas de exposición de datos accedidos por agentes
- Post-deploy de un agente nuevo para validar que no indexa datos sensibles no previstos

## Prerrequisitos

- Licencia M365 E5 o M365 E5 Compliance activa en el tenant
- Rol Compliance Administrator
- Al menos un agente de Copilot Studio o Azure AI Foundry activo en el tenant
- Acceso al portal de Microsoft Purview: purview.microsoft.com

## Workflow

### Paso 1 — Activar DSPM for AI en Purview

1. Ir a **Microsoft Purview** → **Data Security Posture Management** → **AI**
2. Habilitar el escaneo de interacciones de IA (requiere que el tenant tenga datos de M365 Copilot o Copilot Studio)
3. Esperar la ingesta inicial (puede tardar hasta 24h para tenants con historial extenso)

### Paso 2 — Revisar el dashboard de exposición

En el dashboard de DSPM for AI, identificar:

| Métrica | Qué indica |
|---------|------------|
| Sensitive data accessed by AI | Volumen de datos sensibles que los agentes han recuperado |
| Overshared content | Archivos accesibles a agentes que deberían estar restringidos |
| Unlabeled files in AI scope | Archivos sin sensitivity label en el corpus del agente |
| Users interacting with sensitive data via AI | Personas que acceden a datos sensibles a través de prompts |

### Paso 3 — Exportar inventario de sitios en riesgo

```kql
MicrosoftPurviewInformationProtection
| where TimeGenerated > ago(30d)
| where Activity in ("FileAccessed", "FileDownloaded")
| where Workload == "SharePoint"
| extend IsAIAccess = UserAgent has_any ("copilot", "agent", "assistant", "bot")
| where IsAIAccess == true
| extend HasLabel = isnotempty(LabelId)
| summarize
    TotalAccesses = count(),
    UnlabeledAccesses = countif(HasLabel == false),
    LastAccess = max(TimeGenerated)
    by SiteUrl, ObjectId
| extend RiskScore = round(toreal(UnlabeledAccesses) / TotalAccesses * 100, 1)
| sort by RiskScore desc
| project SiteUrl, TotalAccesses, UnlabeledAccesses, RiskScore, LastAccess
```

### Paso 4 — Identificar tipos de datos sensibles más frecuentes

```kql
MicrosoftPurviewInformationProtection
| where TimeGenerated > ago(30d)
| where Activity == "DLPRuleMatch"
    and Workload == "AIInteractions"
| extend SensitiveType = tostring(SensitiveInfoTypeData[0].SensitiveInfoTypeName)
| summarize
    Matches = count(),
    AffectedUsers = dcount(UserId),
    AffectedAgents = dcount(tostring(ApplicationId))
    by SensitiveType
| sort by Matches desc
```

### Paso 5 — Correlacionar con inventario de agentes

```kql
AIAgentsInfo
| where TimeGenerated > ago(30d)
| join kind=leftouter (
    MicrosoftPurviewInformationProtection
    | where TimeGenerated > ago(30d)
    | where Activity == "FileAccessed"
    | where isempty(LabelId)
    | summarize UnlabeledAccessCount = count() by AgentId = tostring(ApplicationId)
) on AgentId
| project AgentName, AgentType, Platform, ManagementStatus, UnlabeledAccessCount
| extend DataRisk = case(
    UnlabeledAccessCount > 1000, "Critical",
    UnlabeledAccessCount > 100, "High",
    UnlabeledAccessCount > 0, "Medium",
    "Low"
)
| sort by UnlabeledAccessCount desc
```

## Verificación

- [ ] DSPM for AI habilitado y mostrando datos en el dashboard
- [ ] Lista de sitios SharePoint con riesgo > 50% (RiskScore) documentada
- [ ] Top 5 tipos de datos sensibles accedidos por agentes identificados
- [ ] Agentes con `DataRisk == "Critical"` o "High" escalados para remediación
- [ ] Resultado incorporado al inventario de agentes del pilar Discover

## Notas de implementación

- DSPM for AI requiere que las interacciones de Copilot o agentes hayan ocurrido — no genera datos retroactivos; los primeros resultados aparecen 24-48h después de la activación
- El dashboard de DSPM está en preview — funcionalidades pueden variar entre tenants según la fase de rollout
- Combinar con `discover-inventory-agents-copilot-studio` para correlacionar exposición de datos con el inventario de agentes
- Priorizar la remediación de sitios con `RiskScore > 70` antes de habilitar retrieval en agentes nuevos
