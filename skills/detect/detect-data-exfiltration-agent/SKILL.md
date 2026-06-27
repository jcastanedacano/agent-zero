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

## Cuándo usar

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

### Paso 1 — Crear regla: acceso masivo a archivos via agente

```kql
// Ver queries/sentinel-exfiltration.kql — Query 1
// Umbral: > 50 archivos únicos en 30 minutos por el mismo usuario via agente
```

Configuración Sentinel:
- **Nombre**: `AISEC-Agent-Bulk-File-Access`
- **Frecuencia**: cada 15 minutos
- **Lookback**: últimas 2 horas
- **Severidad**: High

### Paso 2 — Crear regla: agente enviando email a dominios externos

```kql
// Ver queries/sentinel-exfiltration.kql — Query 2
```

Configuración:
- **Nombre**: `AISEC-Agent-Email-External-Domain`
- **Frecuencia**: cada 5 minutos
- **Lookback**: últimas 24 horas
- **Severidad**: High (si contiene datos sensibles: Critical)

### Paso 3 — Crear regla: llamadas HTTP salientes desde agentes a URLs no aprobadas

```kql
// Ver queries/sentinel-exfiltration.kql — Query 3
// Requiere que los agentes Foundry tengan network logging activo
```

### Paso 4 — Correlacionar con DLP events de Purview

```kql
// Ver queries/sentinel-exfiltration.kql — Query 4
// Join de events de agente con DLP matches para priorizar por sensibilidad
```

### Paso 5 — Configurar alerta de alto volumen en Purview AI Hub

```
Purview AI Hub → Policies → Create policy
→ Tipo: Data volume threshold
→ Umbral: > 100 interacciones en 1 hora por usuario
→ Action: Alert + Restrict
```

## Verificación

- [ ] Regla bulk access creada y probada con datos sintéticos
- [ ] Regla email externo creada (si agentes tienen Mail.Send)
- [ ] Correlación con Purview DLP activa
- [ ] Incident de prueba generado con acceso masivo simulado
- [ ] Playbook de contención vinculado a las reglas (ver skill siguiente)

## Notas de implementación

- Activar el conector de Purview Audit en Sentinel para habilitar la correlación DLP en las queries de exfiltración
- Para simular exfiltración en un tenant de prueba: crear una carpeta en SharePoint con 60+ archivos de prueba y accederlos todos en < 30 minutos para disparar la regla de volumen
- El vector de email relay requiere que el SP del agente tenga `Mail.Send` asignado — verificar con la skill `secure-least-privilege-agent-identity` que ese permiso esté revocado si no es necesario
- Si el conector HTTP del agente no tiene logging habilitado: usar NSG flow logs como proxy para detectar egress (ver skill `secure-network-isolation-agent`)
