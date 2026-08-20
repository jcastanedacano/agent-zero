---
name: detect-alert-prompt-injection-sentinel
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Regla de analítica en Sentinel para detectar prompt injection y jailbreak
  en conversaciones de agentes Copilot Studio y Azure AI Foundry, con
  correlación de Purview para priorizar por sensibilidad de datos involucrados.
tags: [detect, sentinel, prompt-injection, jailbreak, copilot-studio, foundry, aisoc]
atlas_techniques: [AML.T0051, AML.T0054]
d3fend_techniques: [D3-PA, D3-SBV]
nist_ai_rmf: [MEASURE-2.6, MANAGE-3.2]
nist_csf: [DE.CM-01, RS.AN-03]
ms_license: [Microsoft Sentinel, M365 Copilot]
ms_roles: [Microsoft Sentinel Contributor]
effort_hours: 4
---

## When to use

- Conectores CopilotStudio_CL y/o FoundryAgents_CL activos con datos en {workspace-name}
- Como primera regla de analítica del AISOC — mayor ROI de detección
- Cubre MITRE ATLAS AML.T0051 (LLM Prompt Injection)

## Restricción crítica

Sentinel rechaza reglas que referencian tablas `_CL` inexistentes o sin datos.
Verificar antes de crear la regla:

```kql
union CopilotStudio_CL, FoundryAgents_CL
| summarize LastEvent = max(TimeGenerated), Count = count() by Type
| where LastEvent > ago(24h)
```

Si no retorna filas — resolver ingestion antes de continuar.

## Patrones de prompt injection cubiertos

Categoría 1 — Instrucción directa: `ignore previous instructions`, `forget your instructions`
Categoría 2 — Suplantación de rol: `you are now`, `act as`, `pretend you are`, `DAN mode`
Categoría 3 — Bypass de sistema: `bypass your`, `jailbreak`, `override your constraints`
Categoría 4 — Indirect injection: contenido malicioso en documentos que el agente lee

## Workflow

### Step 1 — Verificar existencia de tablas (obligatorio)

```kql
union CopilotStudio_CL, FoundryAgents_CL
| summarize LastEvent = max(TimeGenerated), Count = count() by Type
| where LastEvent > ago(24h)
```

### Step 2 — Validar query base en Log Analytics antes de crear la regla

```kql
// Ver queries/sentinel-prompt-injection.kql — Query 1
// Run manually and verify it returns results or No results without error
```

### Step 3 — Crear Scheduled Analytics Rule en Sentinel

Parámetros:
- **Nombre**: `AISEC-Prompt-Injection-Detection`
- **Frecuencia**: cada 5 minutos
- **Lookback**: últimas 24 horas
- **Umbral**: >= 1 resultado
- **Severidad**: dinámica desde KQL (High/Medium/Low)
- **Tácticas MITRE**: Initial Access + AML.T0051 (ATLAS)
- **Incident grouping**: por `UserId` + `AgentName`, ventana 24h

Via ARM (`2022-12-01-preview`):

```json
{
  "kind": "Scheduled",
  "properties": {
    "displayName": "AISEC-Prompt-Injection-Detection",
    "enabled": true,
    "query": "<KQL de queries/sentinel-prompt-injection.kql>",
    "queryFrequency": "PT5M",
    "queryPeriod": "P1D",
    "triggerOperator": "GreaterThan",
    "triggerThreshold": 0,
    "severity": "Medium",
    "tactics": ["InitialAccess", "Execution"],
    "incidentConfiguration": {
      "createIncident": true,
      "groupingConfiguration": {
        "enabled": true,
        "groupByEntities": ["Account"],
        "lookbackDuration": "PT24H",
        "matchingMethod": "Selected"
      }
    }
  }
}
```

### Step 4 — Crear playbook de enriquecimiento (Logic App)

Al crear incident:
1. Enriquecer `UserId` → perfil Entra ID (GET /users/{id})
2. Consultar actividad reciente del usuario en AuditLogs (últimas 8h)
3. Si `AttemptCount >= 10`: suspender sesión activa del agente
4. Notificar canal Teams AISOC con resumen

### Step 5 — Validar con datos sintéticos en {workspace-name}

Si no hay tráfico real, inyectar evento de prueba via DCR:
```bash
# Usar Data Collection Rule para enviar evento sintético a CopilotStudio_CL
```

## Verification

- [ ] Validation query returns rows or No results without a table error
- [ ] Regla en estado Enabled en Sentinel Analytics
- [ ] Incident de prueba generado con datos sintéticos
- [ ] Playbook ejecuta sin errores en modo test
- [ ] Tiempo de detección < 10 minutos desde evento

## Implementation notes

- Verify the `CopilotStudio_CL` and `FoundryAgents_CL` tables exist and hold data before creating the analytics rule
- Sentinel API version recomendada: `2022-12-01-preview` para recursos SecurityInsights
- Incident grouping by `UserId` plus `AgentName` reduces noise significantly in environments with multiple users testing
- In production: tune the minimum `JailbreakScore` against the false positive rate observed in the first 30 days
