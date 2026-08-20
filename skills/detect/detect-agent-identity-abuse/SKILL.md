---
name: detect-agent-identity-abuse
version: "1.0"
pillar: detect
subdomain: ms-sentinel-aisoc
description: >-
  Detecta abuso de identidades de agentes AI en Entra ID, incluyendo token theft,
  escalada de privilegios no autorizada, uso de service principals de agentes
  from unexpected locations or IPs, and creation of new agents by
  de agentes existentes (agent spawning).
tags: [detect, sentinel, entra, identity-abuse, token-theft, privilege-escalation, agent-spawning]
atlas_techniques: [AML.T0046, AML.T0040, AML.T0056]
d3fend_techniques: [D3-UAP, D3-ANET, D3-JCA]
nist_ai_rmf: [MEASURE-2.6, MANAGE-3.2]
nist_csf: [DE.CM-03, DE.AE-02, RS.AN-03]
ms_license: [Microsoft Sentinel, Microsoft Entra ID P2]
ms_roles: [Microsoft Sentinel Contributor, Security Reader]
effort_hours: 5
---

## When to use

- Después de implementar CA policies (Pilar 2) — para detectar bypasses
- Cuando los logs `AADServicePrincipalSignInLogs` están activos en Sentinel
- To cover the compromised-agent vector that escalates privileges or spawns sub-agents

## Vectores de abuso cubiertos

1. **Token theft**: SP de agente autenticándose desde IP desconocida (token robado)
2. **Privilege escalation**: SP adquiriendo roles no asignados originalmente
3. **Agent spawning**: agente creando nuevos SPs o aplicaciones (sub-agentes)
4. **Impossible travel**: mismo SP autenticando desde dos países en < 1 hora
5. **CA policy bypass**: autenticación exitosa que debería haber sido bloqueada

## Workflow

### Step 1 — Crear regla: sign-in de SP desde IP no corporativa

```kql
// Ver queries/sentinel-identity-abuse.kql — Query 1
// Correlaciona AADServicePrincipalSignInLogs con Named Locations de CA
```

Configuración:
- **Nombre**: `AISEC-Agent-SignIn-Unknown-IP`
- **Frecuencia**: cada 5 minutos
- **Severidad**: High

### Step 2 — Crear regla: agent spawning (agente crea nuevas apps/SPs)

```kql
// Ver queries/sentinel-identity-abuse.kql — Query 2
// Detects when the principal initiating an SP creation is another SP (not a human)
```

Configuración:
- **Nombre**: `AISEC-Agent-Spawning-Detected`
- **Frecuencia**: cada 15 minutos
- **Severidad**: Critical — vector de máximo riesgo

### Step 3 — Crear regla: escalada de privilegios de agente

```kql
// Ver queries/sentinel-identity-abuse.kql — Query 3
```

Configuración:
- **Nombre**: `AISEC-Agent-Privilege-Escalation`
- **Frecuencia**: cada 15 minutos
- **Severidad**: Critical

### Step 4 — Crear regla: impossible travel para service principals

```kql
// Ver queries/sentinel-identity-abuse.kql — Query 4
// Dos autenticaciones exitosas del mismo SP desde países diferentes en < 60 min
```

Configuración:
- **Nombre**: `AISEC-Agent-Impossible-Travel`
- **Frecuencia**: cada hora
- **Severidad**: High

### Step 5 — Vincular con watchlist de SPs de agentes conocidos

Crear watchlist en Sentinel con los SPs de agentes registrados:

```
Sentinel → Watchlists → New → Upload CSV
Columnas: AgentName, ServicePrincipalId, AppId, RiskLevel, Owner
```

Usar la watchlist en las reglas para contextualizar los incidents con
información del risk register del Pilar 1.

## Verification

- [ ] `AADServicePrincipalSignInLogs` tiene datos en el workspace
- [ ] Las 4 reglas de analítica creadas y en estado Enabled
- [ ] Watchlist de SPs de agentes cargada
- [ ] Incident de prueba: autenticar SP desde IP externa y verificar alerta
- [ ] Agent spawning: crear SP manualmente desde contexto de SP y verificar detección

## Implementation notes

- `AADServicePrincipalSignInLogs` requiere Entra ID P2 o el data connector de Entra ID activo en Sentinel
- For impossible travel on service principals: agent SPs in Azure rarely have variable IPs — any IP geolocation change is suspicious
- Agent spawning is the highest-risk vector in multi-agent architectures: a compromised agent can create persistent sub-agents with inherited permissions
- Correlate with `AuditLogs` in Sentinel to detect new SP creation in the same interval as the compromised agent
