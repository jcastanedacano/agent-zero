---
name: govern-pim-agent-roles
version: "1.0"
pillar: govern
subdomain: ms-entra
description: >-
  Implementa Privileged Identity Management (PIM) para managed identities y
  service principals de agentes AI, eliminando privilegio permanente y
  requiriendo activación just-in-time con justificación auditada.
tags: [govern, entra, pim, privileged-identity, just-in-time, agent-identity]
atlas_techniques: [AML.T0046, AML.T0040]
d3fend_techniques: [D3-UAP, D3-JIT]
nist_ai_rmf: [GOVERN-2.2, MANAGE-1.3]
nist_csf: [PR.AA-05, PR.AC-04]
ms_license: [Microsoft Entra ID P2, Microsoft Entra Workload ID Premium]
effort_hours: 8
---

## Cuándo usar

- Agentes con roles Azure RBAC de alto privilegio (Contributor, Owner, User Access Administrator)
- Agentes con Graph API permissions sensibles que no necesitan acceso continuo
- Cuando el risk register del Pilar 1 identifica agentes con acceso excesivo permanente

## Restricción de licencia

PIM para workload identities (service principals) requiere **Entra Workload ID Premium**.
PIM para usuarios y grupos: Entra ID P2.
Verificar licencias antes de iniciar.

## Workflow

### Paso 1 — Identificar roles permanentes de agentes

```http
GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignments
  ?$filter=principalId eq '{service-principal-object-id}'
  &$expand=roleDefinition
```

Buscar assignments con `directoryScopeId: "/"` (scope global) — mayor riesgo.

También revisar Azure RBAC:
```bash
az role assignment list \
  --assignee {service-principal-app-id} \
  --include-inherited \
  --query "[].{Role:roleDefinitionName, Scope:scope}"
```

### Paso 2 — Configurar PIM para Azure resources (agentes con roles RBAC)

```
Entra ID → Privileged Identity Management → Azure resources
→ [Suscripción / RG objetivo]
→ Roles → [Rol del agente]
→ Settings → Edit
```

Configuración recomendada para agentes AI:
- **Activation maximum duration**: 1-4 horas (no 8h)
- **Require justification on activation**: Yes
- **Require approval**: Yes (para roles Contributor+)
- **Approvers**: Security team group
- **On activation require**: MFA (para el humano que aprueba, no el agente)

### Paso 3 — Convertir assignment permanente a eligible

```
PIM → Azure resources → Assignments → [Rol] → Add assignments
→ Assignment type: Eligible (no Active)
→ Principal: [Service Principal del agente]
→ Duration: Sin expiración (o 6-12 meses con renovación)
```

Remover el assignment permanente existente después de crear el eligible.

### Paso 4 — Para Entra ID roles (Graph API permissions)

PIM para Entra roles con service principals:
```
PIM → Entra roles → Settings → [Rol]
→ Habilitar "Allow permanent eligible assignments" = No
→ Require justification: Yes
```

**Nota**: PIM para app roles de Graph API (OAuth permissions) tiene soporte limitado.
Para permisos Graph críticos, considerar revocación y re-consent bajo demanda
como alternativa a PIM nativo.

### Paso 5 — Monitorear activaciones en Sentinel

```kql
// Ver queries/sentinel-pim-activations.kql
```

## Verificación

- [ ] Roles permanentes de agentes convertidos a eligible
- [ ] Settings de PIM configurados (duración, justificación, aprobación)
- [ ] Assignment permanente original removido
- [ ] Alerta en Sentinel para activaciones fuera de horario configurada
- [ ] Test de activación realizado exitosamente

## Notas {workspace-name}

- Entra ID P2 disponible en contoso.com MVP sponsorship — PIM habilitado
- Para Workload ID Premium: verificar si está incluido en el sponsorship
- Lokka-Microsoft MCP: puede gestionar role assignments pero PIM eligible
  assignments requieren endpoint específico (`/roleManagement/directory/roleEligibilityScheduleRequests`)
- Para demo: mostrar diferencia entre assignment permanente y activación JIT
