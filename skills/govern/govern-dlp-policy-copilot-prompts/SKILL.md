---
name: govern-dlp-policy-copilot-prompts
version: "1.0"
pillar: govern
subdomain: ms-purview-ai
description: >-
  Configura políticas DLP en Microsoft Purview para detectar y bloquear
  transmisión de datos sensibles en prompts y respuestas de agentes Copilot
  Studio, cubriendo PII, datos financieros y secretos corporativos.
tags: [govern, purview, dlp, copilot-studio, data-protection, prompt-security]
atlas_techniques: [AML.T0057, AML.T0048]
d3fend_techniques: [D3-DLP, D3-PA]
nist_ai_rmf: [MANAGE-2.2, GOVERN-6.1]
nist_csf: [PR.DS-01, PR.DS-05]
ms_license: [Microsoft Purview E3, M365 E3]
ms_roles: [Compliance Administrator, DLP Compliance Management]
effort_hours: 6
---

## Cuándo usar

- Agentes con acceso a datos de clientes (PII), financieros o estratégicos
- Antes de habilitar agentes en entornos de producción con datos reales
- Requisito de compliance (regulaciones de datos en sectores financiero/salud)

## Restricción conocida

Purview auto-labeling policy creation no está disponible via Lokka-Microsoft MCP
ni ARM directo para todas las capacidades. Configuración via Compliance Portal
(UI) es el camino confiable para políticas complejas.

## Prerrequisitos

- Microsoft Purview E3 o superior
- Sensitivity labels configurados en el tenant
- Rol Compliance Administrator
- Acceso a Microsoft Purview Compliance Portal (`compliance.microsoft.com`)

## Workflow

### Paso 1 — Verificar sensitive information types relevantes

```
Purview Compliance Portal → Data classification → Sensitive info types
```

Tipos prioritarios para agentes AI:
- **Credit Card Number** — transacciones financieras
- **National ID** — PII de usuarios
- **SWIFT Code** — datos bancarios
- **Generic Password** / **API Key** — secretos que podrían exfiltrarse via prompt
- Tipos personalizados: crear si el sector lo requiere

### Paso 2 — Crear DLP policy para Copilot

```
Purview Compliance Portal → Data loss prevention → Policies → Create policy
→ Custom policy
→ Locations: Microsoft Copilot (preview si disponible), Teams, SharePoint
```

**Regla 1 — Bloquear PII en prompts salientes:**
- Condition: content contains [Credit Card Number, National ID, SWIFT Code]
- Action: Block + notify user + generate alert
- User notification: "Este prompt contiene información sensible y no puede enviarse al agente"

**Regla 2 — Alertar en respuestas con datos confidenciales:**
- Condition: content contains sensitivity label [Confidential, Highly Confidential]
- Action: Alert compliance team + audit log

### Paso 3 — Modo simulación primero

Activar política en **Test mode** (sin enforcement) durante 7 días.
Revisar DLP reports para identificar falsos positivos antes de enforcement.

```
Purview → Data loss prevention → Reports → DLP policy matches
```

### Paso 4 — Activar enforcement

Cambiar a **Turn it on right away** tras validar en test mode.
Configurar alertas para el equipo de compliance.

### Paso 5 — Configurar Purview AI Hub (si disponible)

```
Purview → AI Hub → Settings
```

AI Hub proporciona visibilidad específica de interacciones con agentes AI.
Habilitar auditoría de prompts para correlación con Sentinel.

## Verificación

- [ ] Sensitivity information types configurados
- [ ] Policy en test mode retorna matches en DLP reports
- [ ] Falsos positivos revisados y ajustados
- [ ] Policy en enforcement activo
- [ ] Alertas de compliance configuradas
- [ ] AI Hub habilitado (si licencia disponible)

## Notas de implementación

- El conector de Purview en Sentinel debe estar activo para que los eventos DLP sean visibles en las queries KQL
- La creación de auto-labeling policies vía API tiene limitaciones en preview — usar el Compliance Portal para la configuración inicial y luego gestionar via API para actualizaciones
- Para validar la policy DLP sin datos reales: usar datos sintéticos en formato de tarjeta de crédito en un prompt de prueba — confirmar que la policy genera el evento en DLP Alerts antes de pasar a producción
