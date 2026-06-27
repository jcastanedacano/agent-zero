---
name: protect-data-loss-prevention-agent-outputs
version: "1.0"
pillar: protect
subdomain: ms-purview-ai
description: >-
  Configura políticas DLP en Purview específicamente para outputs de agentes AI
  en SharePoint, OneDrive y Exchange, bloqueando compartición de contenido
  generado por agentes que contenga datos sensibles hacia destinos no autorizados.
tags: [protect, purview, dlp, sharepoint, onedrive, exchange, agent-outputs, exfiltration]
atlas_techniques: [AML.T0048, AML.T0057]
d3fend_techniques: [D3-DLP, D3-EAC]
nist_ai_rmf: [MANAGE-2.2, GOVERN-6.1]
nist_csf: [PR.DS-05, DE.CM-01]
ms_license: [Microsoft Purview E3, M365 E3]
ms_roles: [Compliance Administrator, DLP Compliance Management]
effort_hours: 5
---

## Cuándo usar

- Agentes que depositan outputs en SharePoint o OneDrive
- Agentes que envían outputs vía email (Exchange)
- Cuando sensitivity labels están configurados (ver skill anterior) y se necesita
  bloquear acciones sobre contenido etiquetado
- Diferencia clave con `govern-dlp-policy-copilot-prompts`: esa skill protege
  los prompts de entrada; esta skill protege los outputs/archivos generados

## Escenarios de riesgo cubiertos

1. Agente genera reporte con datos de clientes y usuario lo comparte externamente
2. Agente exporta datos de CRM a CSV en OneDrive y usuario descarga sin restricción
3. Agente redacta email con información confidencial y lo envía a destinatario externo

## Workflow

### Paso 1 — Identificar ubicaciones de output de agentes

Del risk register del Pilar 1 y la skill `discover-classify-agent-connectors`:
- ¿Qué SharePoint sites usan los agentes como destino de output?
- ¿Qué OneDrive folders?
- ¿Los agentes tienen acceso a enviar email vía Exchange?

Construir lista de ubicaciones objetivo para la policy.

### Paso 2 — Crear DLP policy para outputs en SharePoint/OneDrive

```
Purview Compliance Portal → Data loss prevention → Policies → Create policy
→ Custom → Custom policy
```

**Locations:**
- SharePoint sites: seleccionar solo los sites donde operan agentes
- OneDrive accounts: todos o selección por grupo
- Exchange email: incluir si agentes tienen acceso a Mail.Send

**Rules:**

**Regla 1 — Bloquear compartición externa de contenido AI con datos sensibles:**
```
Condition: Content contains sensitivity label [Confidential / AI-Generated]
AND
Condition: Content is shared with [people outside the organization]
Action: Block access + Notify user + Generate alert
```

**Regla 2 — Restringir descarga de archivos AI en dispositivos no gestionados:**
```
Condition: Content contains sensitivity label [Confidential / AI-Generated]
AND
Condition: Device is not managed (Intune)
Action: Block download + Allow view only
```

**Regla 3 — Alertar en volumen alto de archivos AI accedidos en corto tiempo:**
```
Condition: Content contains sensitivity label [AI-Generated]
AND
Condition: Activity count > 50 in 30 minutes (mismo usuario)
Action: Generate alert + Restrict access
```

### Paso 3 — Modo simulación

Activar en **Test mode** durante 7 días.
Revisar:

```
DLP → Reports → DLP policy matches
→ Filtrar por política recién creada
```

Ajustar umbrales si hay falsos positivos en Regla 3.

### Paso 4 — Configurar endpoint DLP (si aplica)

Para controlar qué pasa cuando un usuario descarga un archivo AI a su dispositivo:

```
DLP → Endpoint DLP settings → Browser and app restrictions
→ Add unallowed apps: aplicaciones no corporativas
→ Clipboard restriction: restringir copy-paste de contenido HC AI-Generated
```

Requiere dispositivos con MDE onboarded y Endpoint DLP habilitado.

### Paso 5 — Activar y monitorear

```
DLP policy → Turn it on right away
```

Monitorear durante primera semana con queries en Sentinel.

```kql
// Ver queries/sentinel-dlp-outputs.kql
```

## Verificación

- [ ] Policy cubre todas las ubicaciones de output de agentes identificadas
- [ ] Test mode retorna matches esperados (no solo archivos sin datos sensibles)
- [ ] Regla de compartición externa bloquea correctamente en test
- [ ] Policy en enforcement activo
- [ ] Alertas de compliance configuradas para el equipo de seguridad
- [ ] Endpoint DLP activo si los agentes depositan en dispositivos locales

## Notas {workspace-name}

- Workbook Purview Compliance disponible para monitorear DLP matches
- Para demo: crear archivo con datos sintéticos de tarjeta de crédito en SharePoint
  y verificar que la policy bloquea compartición externa
- Endpoint DLP requiere MDE onboarded — verificar estado de dispositivos en {workspace-name}
- La Regla 3 (volumen alto) puede generar falsos positivos en usuarios que hacen
  búsquedas amplias — ajustar umbral según baseline del tenant
