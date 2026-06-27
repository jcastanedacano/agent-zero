---
name: detect-anomalous-agent-behavior
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Detecta desviaciones estadísticas en el comportamiento de agentes AI respecto
  a su baseline, incluyendo volumen inusual de API calls, acceso a recursos
  fuera del patrón normal, horarios de operación anómalos y cambios súbitos
  en tipos de datos procesados.
tags: [detect, sentinel, behavioral-analytics, anomaly, baseline, aisoc, ueba]
atlas_techniques: [AML.T0040, AML.T0056, AML.T0048]
d3fend_techniques: [D3-NTA, D3-PA, D3-ANET]
nist_ai_rmf: [MEASURE-2.6, MEASURE-2.5]
nist_csf: [DE.AE-01, DE.CM-06]
ms_license: [Microsoft Sentinel, Microsoft Sentinel UEBA]
ms_roles: [Microsoft Sentinel Contributor]
effort_hours: 6
---

## Cuándo usar

- Post-deployment de reglas básicas (prompt injection) — añade detección comportamental
- Cuando los agentes tienen suficiente historial (mínimo 14 días) para establecer baseline
- Para detectar agentes comprometidos que no usan técnicas conocidas de injection

## Lógica de detección

Un agente comprometido o mal configurado se manifiesta como:
- Volumen de llamadas 3x+ sobre su baseline diario
- Acceso a recursos que nunca había tocado antes
- Operación fuera del horario en que normalmente es invocado
- Cambio en el tipo de datos accedidos (de solo lectura a escritura)
- Latencia inusualmente baja (automatización) o alta (procesamiento masivo)

## Workflow

### Paso 1 — Establecer baseline por agente (mínimo 14 días)

```kql
// Ver queries/sentinel-agent-baseline.kql — Query 1
// Ejecutar primero para verificar que hay suficiente historial
```

Si hay menos de 7 días de datos: documentar y esperar antes de activar
las reglas de anomalía basadas en baseline.

### Paso 2 — Crear regla: volumen anómalo de llamadas

```kql
// Ver queries/sentinel-agent-baseline.kql — Query 2
// Umbral: > 3x baseline diario
```

Configuración de la regla Sentinel:
- **Nombre**: `AISEC-Agent-Anomalous-Volume`
- **Frecuencia**: cada hora
- **Lookback**: últimas 24 horas
- **Severidad**: Medium (escalar a High si el agente tiene conectores de riesgo Alto)

### Paso 3 — Crear regla: acceso a recursos nuevos

```kql
// Ver queries/sentinel-agent-baseline.kql — Query 3
// Detectar recursos accedidos por primera vez en los últimos 7 días
```

Configuración:
- **Nombre**: `AISEC-Agent-New-Resource-Access`
- **Frecuencia**: cada 15 minutos
- **Lookback**: últimas 24 horas
- **Severidad**: High (si el recurso es SharePoint o Exchange)

### Paso 4 — Crear regla: operación fuera de horario

```kql
// Ver queries/sentinel-agent-baseline.kql — Query 4
```

Configuración:
- **Nombre**: `AISEC-Agent-Off-Hours-Operation`
- **Frecuencia**: cada hora
- **Lookback**: últimas 8 horas
- **Severidad**: Medium

### Paso 5 — Habilitar UEBA para agentes

```
Sentinel → Settings → UEBA
→ Enable entity behavior analytics
→ Entities: Accounts (incluye service principals si están en scope)
```

UEBA genera `BehaviorAnalytics` table con scores de anomalía por entidad.

### Paso 6 — Correlacionar con UEBA scores

```kql
// Ver queries/sentinel-agent-baseline.kql — Query 5
```

## Verificación

- [ ] Baseline calculado con mínimo 7 días de datos (14 recomendado)
- [ ] Las tres reglas de analítica creadas y en estado Enabled
- [ ] UEBA habilitado y `BehaviorAnalytics` table tiene datos
- [ ] Test: modificar artificialmente el volumen de llamadas de un agente de prueba
  y verificar que genera incident

## Notas {workspace-name}

- `BehaviorAnalytics` table requiere UEBA habilitado en Sentinel — verificar configuración
- Para agentes con poco historial: usar lookback de 7 días en lugar de 14
- Las reglas de anomalía tienen tasa de falsos positivos más alta que las de firma —
  ajustar umbrales según el comportamiento real del tenant
- Si Foundry Agents no tiene suficientes datos: aplicar solo a CopilotStudio_CL inicialmente
