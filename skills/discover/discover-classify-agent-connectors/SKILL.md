---
name: discover-classify-agent-connectors
version: "1.0"
pillar: discover
subdomain: ms-copilot-studio
description: >-
  Clasifica los conectores activos en agentes Copilot Studio y Power Platform
  por nivel de riesgo según tipo de datos accesibles, generando una matriz
  de exposición como input para controles de govern y protect.
tags: [discover, copilot-studio, connectors, data-classification, power-platform]
atlas_techniques: [AML.T0057, AML.T0048]
d3fend_techniques: [D3-AM, D3-NTA]
nist_ai_rmf: [MAP-2.2, MAP-5.1]
nist_csf: [ID.AM-05, ID.RA-01]
ms_license: [Power Platform, M365 E3]
ms_roles: [Power Platform Administrator]
effort_hours: 2
---

## Cuándo usar

- Después de `discover-inventory-agents-copilot-studio`
- Como input para `govern-dlp-policy-copilot-prompts` y `protect-purview-ai-hub`
- Cuando se requiere matriz de exposición de datos por agente

## Prerrequisitos

- Power Platform Admin Center accesible
- Lista de agentes del Paso 1 (skill anterior)
- Catálogo de tipos de datos del tenant (Purview si disponible)

## Workflow

### Paso 1 — Exportar conectores por agente desde PP Admin

```
Power Platform Admin Center → Analytics → Power Automate → Connectors
```

O via Power Platform Management connector en Power Automate:

```
List connectors → filter by environment → export to CSV
```

### Paso 2 — Clasificar conectores por categoría de datos

| Conector | Categoría | Riesgo base |
|---|---|---|
| SharePoint | Documentos corporativos | Alto |
| Exchange / Outlook | Email corporativo | Alto |
| Dataverse | Datos de negocio | Alto |
| Teams | Comunicaciones | Medio |
| Azure Blob Storage | Depende del contenido | Medio-Alto |
| Bing Search | Datos públicos | Bajo |
| HTTP genérico | Desconocido | Alto (sin validar) |
| ServiceNow / Jira | Tickets IT | Medio |
| SAP / Dynamics | ERP / CRM | Alto |

### Paso 3 — Cruzar conector × agente × propietario

Construir tabla:

| Agente | Conector | Categoría | Propietario | ¿Aprobado? | Riesgo |
|---|---|---|---|---|---|
| {nombre} | SharePoint | Documentos | {email} | Sí/No | Alto |

### Paso 4 — Priorizar para remediación

Orden de prioridad:
1. Agentes sin aprobación + conectores Alto
2. Agentes aprobados + conectores no documentados en el scope original
3. Conectores HTTP genéricos sin validación de destino

## Verificación

- [ ] Matriz conector × agente completada
- [ ] Riesgo asignado a cada combinación
- [ ] Conectores HTTP genéricos con URL destino documentada (o sin documentar = riesgo Alto)
- [ ] Input listo para skill de govern/protect

## Notas {workspace-name}

- En contoso.com los agentes de demo usan conectores limitados — tabla puede ser pequeña
- Para demo real: importar datos de cliente desde CSV y usar como lookup table en KQL
- Purview AI Hub (si habilitado) puede proveer clasificación automática de datos accedidos
