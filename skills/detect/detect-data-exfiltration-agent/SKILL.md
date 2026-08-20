---
name: detect-data-exfiltration-agent
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Detecta patrones de exfiltración de datos a través de agentes AI, incluyendo
  descarga masiva de archivos vía agente, transferencia de datos sensibles a
  conectores externos, y uso de agentes como proxy para extraer información
  corporativa hacia destinos no autorizados.
tags: [detect, sentinel, exfiltration, data-loss, sharepoint, exchange, aisoc]
atlas_techniques: [AML.T0048, AML.T0057]
d3fend_techniques: [D3-NTA, D3-DLP, D3-EAC]
nist_ai_rmf: [MEASURE-2.6, MANAGE-3.2]
nist_csf: [DE.CM-01, DE.AE-03, RS.AN-03]
ms_license: [Microsoft Sentinel, Microsoft Purview E3]
ms_roles: [Microsoft Sentinel Contributor, Security Reader]
effort_hours: 5
---

## When to use

- Agentes con acceso a SharePoint, Exchange o bases de datos de producción
- Cuando DLP de outputs está activo (Pilar 4) y se necesita correlación en Sentinel
- Para detectar el vector de agente como intermediario de exfiltración:
  usuario solicita al agente que resuma/exporte datos → agente accede a volumen
  grande → datos salen vía canal no monitoreado

## Vectores de exfiltración cubiertos

1. **Bulk access**: agente accede a N archivos en corto tiempo por solicitud de usuario
2. **Summary as exfil**: usuario pide resumen de documentos confidenciales → copia texto
3. **Connector abuse**: agente usa conector HTTP genérico para enviar datos a URL externa
4. **Email relay**: agente con permisos Mail.Send envía datos a cuenta externa
5. **Cross-tenant**: agente en multi-tenant comparte datos entre tenants

## Workflow

### Step 1 — Crear regla: acceso masivo a archivos via agente

```kql
// Ver queries/sentinel-exfiltration.kql — Query 1
// Umbral: > 50 archivos únicos en 30 minutos por el mismo usuario via agente
```

Configuración Sentinel:
- **Nombre**: `AISEC-Agent-Bulk-File-Access`
- **Frecuencia**: cada 15 minutos
- **Lookback**: últimas 2 horas
- **Severidad**: High

### Step 2 — Crear regla: agente enviando email a dominios externos

```kql
// Ver queries/sentinel-exfiltration.kql — Query 2
```

Configuración:
- **Nombre**: `AISEC-Agent-Email-External-Domain`
- **Frecuencia**: cada 5 minutos
- **Lookback**: últimas 24 horas
- **Severidad**: High (si contiene datos sensibles: Critical)

### Step 3 — Create rule: outbound HTTP calls from agents to unapproved URLs

```kql
// Ver queries/sentinel-exfiltration.kql — Query 3
// Requiere que los agentes Foundry tengan network logging activo
```

### Step 4 — Correlacionar con DLP events de Purview

```kql
// Ver queries/sentinel-exfiltration.kql — Query 4
// Join agent events with DLP matches to prioritize by sensitivity
```

### Step 5 — Configurar alerta de alto volumen en Purview AI Hub

```
Purview AI Hub → Policies → Create policy
→ Tipo: Data volume threshold
→ Umbral: > 100 interacciones en 1 hora por usuario
→ Action: Alert + Restrict
```

## Verification

- [ ] Regla bulk access creada y probada con datos sintéticos
- [ ] Regla email externo creada (si agentes tienen Mail.Send)
- [ ] Correlación con Purview DLP activa
- [ ] Incident de prueba generado con acceso masivo simulado
- [ ] Playbook de contención vinculado a las reglas (ver skill siguiente)

## Implementation notes

- Activate the Purview Audit connector in Sentinel to enable DLP correlation in the exfiltration queries
- To simulate exfiltration in a test tenant: create a SharePoint folder with 60+ test files and access them all in one session
- The email relay vector requires the agent SP to hold `Mail.Send` — verify with the `secure-least-privilege-agent-identity` skill
- If the agent HTTP connector has no logging enabled: use NSG flow logs as a proxy to detect egress
