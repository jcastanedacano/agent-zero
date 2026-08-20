---
name: govern-agent365-approval-flow
version: "1.0"
pillar: govern
subdomain: ms-copilot-studio
description: >-
  Configura y opera el flujo de aprobación de agentes AI en Agent 365 (M365 Admin
  Center), estableciendo políticas para que nuevos agentes pasen por Requests antes
  before activation, closing the Agent Builder gap that activates agents without approval.
tags: [govern, copilot-studio, agent365, approval-flow, shadow-ai-prevention]
atlas_techniques: [AML.T0054]
d3fend_techniques: [D3-UAP, D3-SFA]
nist_ai_rmf: [GOVERN-1.2, GOVERN-2.1]
nist_csf: [GV-PO-01, PR.AA-05]
ms_license: [M365 Copilot, M365 E3]
ms_roles: [Microsoft 365 Administrator, Teams Administrator]
effort_hours: 6
---

## When to use

- Después de identificar shadow AI en Pilar 1 (gap Registry vs Requests)
- Cuando el tenant no tiene proceso formal de aprobación de agentes
- As a preventive control before Agent Builder usage proliferates

## Gap crítico a cerrar

Agentes creados desde **Agent Builder** (dentro de M365 Copilot) se activan
immediately without generating a Request in Agent 365. This is the primary vector
de shadow AI en organizaciones con M365 Copilot.

El flujo de Requests aplica a agentes creados en Copilot Studio directamente,
no a los de Agent Builder. Ambos canales requieren controles diferentes.

## Prerequisites

- M365 Admin Center con rol de administrador
- Agent 365 habilitado en el tenant
- Decisión organizacional: ¿política de aprobación obligatoria o revisión post-hoc?

## Workflow

### Step 1 — Configurar política de agentes en Agent 365

```
M365 Admin Center → Settings → Agent 365 → Policies
```

Opciones disponibles:
- **Allow all agents**: sin control (default)
- **Block all agents**: bloqueo total
- **Allow specific agents**: lista de permitidos
- **Require admin approval**: habilita flujo Requests

Seleccionar **Require admin approval** para control efectivo.

### Step 2 — Configurar Requests workflow

```
Agent 365 → Requests → Settings
```

Definir:
- **Approvers**: grupo de seguridad del equipo de IT/Security
- **Auto-approve criteria**: agentes sin conectores externos (bajo riesgo)
- **Notification settings**: email a approvers al recibir Request

### Step 3 — Cerrar el gap de Agent Builder

Agent Builder bypass no puede cerrarse desde Agent 365. Controles alternativos:

**Opción A — Power Platform DLP Policy** (recomendado):
```
Power Platform Admin Center → Policies → Data policies
→ Crear política que restrinja conectores en entornos de producción
→ Asignar a entornos donde opera M365 Copilot
```

**Opción B — Conditional Access en M365 Copilot**:
Block Agent Builder for users not in the approved AI Builders group:
```
CA policy → Cloud apps: Microsoft Copilot → 
  Exclude: AI-Builders-Approved-Group
  Grant: block
```

**Opción C — Restricción de licencia**:
Asignar licencia M365 Copilot solo a usuarios en proceso de aprobación formal.

### Step 4 — Proceso operacional de aprobación

Flujo para cada Request recibido:

1. Revisar nombre y descripción del agente
2. Verificar creador (departamento, rol)
3. Revisar conectores solicitados (cruzar con skill `discover-classify-agent-connectors`)
4. Evaluar datos accesibles por categoría de sensibilidad
5. Aprobar con condiciones o rechazar con justificación documentada
6. Registrar decisión en log de governance (SharePoint list o tabla custom)

### Step 5 — Auditoría mensual

Revisar tab **Registry** vs **Requests** mensualmente para detectar agentes que
hayan eludido el proceso. Cualquier discrepancia = incidente de shadow AI.

## Verification

- [ ] Política "Require admin approval" habilitada en Agent 365
- [ ] Grupo de approvers definido y notificaciones activas
- [ ] At least one control for the Agent Builder gap implemented (A, B, or C)
- [ ] Proceso operacional documentado en runbook
- [ ] Auditoría mensual calendarizada

## Implementation notes

- Verify Agent 365 is configured in the tenant before enabling the approval flow — the central registry is not active by default
- To demonstrate the Agent Builder bypass gap: create an agent via Agent Builder and compare its state in Agent 365 Registry vs. Copilot Studio Requests
- Power Platform DLP is the most effective compensating control for mitigating the Agent Builder bypass in enterprise environments where you cannot restrict it directly
