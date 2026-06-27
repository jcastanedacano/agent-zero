---
name: detect-security-copilot-triage
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Configura Microsoft Security Copilot como agente de triage para incidentes
  de seguridad generados por agentes de IA, acelerando MTTD con prompts
  estructurados y correlación automática de entidades de Sentinel y Defender.
tags: [detect, security-copilot, triage, aisoc, incident-response, mttd]
atlas_techniques: [AML.T0054, AML.T0051]
d3fend_techniques: [D3-SBV, D3-NTA]
nist_ai_rmf: [MANAGE-3.2, MANAGE-4.1]
nist_csf: [DE.AE-02, RS.AN-01, RS.AN-03]
ms_license: [Microsoft Security Copilot, Microsoft Sentinel]
ms_roles: [Security Operator, Microsoft Sentinel Reader]
effort_hours: 2
---

## Cuándo usar

- Cuando el volumen de alertas de agentes supera la capacidad de triage manual del SOC
- Para estandarizar el proceso de triage de incidentes agentic entre analistas con diferente nivel de experiencia
- Como primer nivel de respuesta ante alertas de jailbreak o anomalía de agente
- Para generar resúmenes ejecutivos de incidentes agentic para escalada a CISO

## Prerrequisitos

- Microsoft Security Copilot activo en el tenant
- Conexión a Microsoft Sentinel configurada en Security Copilot Sources
- Conexión a Microsoft Defender XDR configurada en Security Copilot Sources
- Rol Security Operator mínimo para el analista

## Workflow

### Paso 1 — Configurar las fuentes de datos en Security Copilot

En **Security Copilot** → **Sources** → verificar que están activas:
- ✅ Microsoft Sentinel (workspace de seguridad de agentes)
- ✅ Microsoft Defender XDR
- ✅ Microsoft Entra (para contexto de identidad de agentes)
- ✅ Microsoft Purview (para contexto de datos sensibles)

### Paso 2 — Prompt de triage de jailbreak

```
Analiza el incidente de Sentinel con ID {INCIDENT_ID}.

1. ¿Cuál es la severidad y el título del incidente?
2. ¿Qué agente de IA está involucrado? (nombre, tipo, plataforma, dueño técnico)
3. ¿Cuáles son los indicadores de compromiso del incidente?
4. Busca en Defender XDR si hay actividad relacionada del mismo usuario o IP en las últimas 4 horas
5. Evalúa: ¿es esto un intento de jailbreak real (confianza alta), probable (media) o un falso positivo (baja)?
6. Si confianza alta o media: ¿qué permisos tiene el agente que podrían ser explotados?
7. Recomienda: contener ahora (revocar token) o monitorear 30 minutos más
```

### Paso 3 — Prompt de resumen ejecutivo para escalada

```
Basándote en el incidente {INCIDENT_ID} de Sentinel y tu análisis previo:

Genera un resumen ejecutivo de máximo 150 palabras que incluya:
- Qué ocurrió (en lenguaje de negocio, sin jerga técnica)
- Qué agente estuvo involucrado y qué función tiene en la organización
- Qué datos o sistemas estuvieron en riesgo
- Qué acción tomó el equipo SOC y cuándo
- Si hay exposición de datos confirmada o solo riesgo potencial
- Recomendación de próximo paso para la dirección

Audiencia: CISO y Director de Operaciones. No usar acronimos sin explicación.
```

### Paso 4 — Prompt de análisis de patrón histórico

```
En Microsoft Sentinel, busca todos los incidentes de los últimos 90 días que:
- Involucren agentes de IA (busca en título: "agent", "copilot", "AI", "jailbreak")
- Tengan severidad High o Critical

Para cada grupo de incidentes similares, determina:
1. ¿Cuántos incidentes del mismo tipo hay?
2. ¿Hay algún agente que aparezca en múltiples incidentes?
3. ¿Hay un patrón horario o de usuario?
4. ¿Cuántos se cerraron como falsos positivos vs. confirmados?

Identifica el top 3 de patrones de ataque más frecuentes y el top 3 de agentes más involucrados.
```

### Paso 5 — Medir impacto del triage agentic

```kql
// Comparar MTTD antes y después de habilitar Security Copilot para triage
SecurityIncident
| where TimeGenerated > ago(180d)
| where Title has_any ("Agentic AI", "jailbreak", "agent")
| extend CopilotEnabled = TimeGenerated > datetime(2024-06-01) // ajustar a fecha de activación
| extend TimeToTriage_hours = datetime_diff('hour', TimeGenerated, CreatedTime)
| summarize
    AvgTimeToTriage = avg(TimeToTriage_hours),
    P90TimeToTriage = percentile(TimeToTriage_hours, 90),
    IncidentCount = count()
    by CopilotEnabled
```

## Verificación

- [ ] Security Copilot conectado a Sentinel, Defender, Entra y Purview
- [ ] Prompt de triage de jailbreak ejecutado contra un incidente real o de prueba
- [ ] Resumen ejecutivo generado y validado por un analista senior
- [ ] Prompt de patrón histórico retorna resultados coherentes con los incidentes del tenant
- [ ] Baseline de MTTD establecido para medir impacto del triage agentic

## Notas de implementación

- Security Copilot accede a los datos de las fuentes conectadas en tiempo real — la calidad del triage depende de que las conexiones estén activas y con datos recientes
- Los prompts de triage deben ser revisados periódicamente: los patrones de jailbreak evolucionan y los prompts genéricos generan más falsos positivos con el tiempo
- Security Copilot no puede ejecutar acciones de contención directamente (revocar tokens, bloquear SP) — siempre requiere un humano o un Logic App para el enforcement; el agente informa, el humano o el playbook actúa
- Combinar con `detect-sentinel-mcp-server` para el flujo completo: Security Copilot consulta Sentinel via MCP y actualiza el incidente con los hallazgos del triage
