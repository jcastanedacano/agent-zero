---
name: protect-information-barriers-agents
version: "1.0"
pillar: protect
subdomain: ms-purview-ai
description: >-
  Implementa Information Barriers en Microsoft Purview para prevenir que agentes AI
  crucen límites de información entre segmentos organizacionales, evitando que un
  agente del área de finanzas acceda a datos del área legal o viceversa,
  cumpliendo requisitos regulatorios de separación de información.
tags: [protect, purview, information-barriers, segmentation, compliance, teams, sharepoint]
atlas_techniques: [AML.T0057, AML.T0048]
d3fend_techniques: [D3-NI, D3-EAC]
nist_ai_rmf: [GOVERN-6.2, MANAGE-2.2]
nist_csf: [PR.DS-05, PR.AC-05]
ms_license: [Microsoft Purview E5, M365 E5 Compliance]
ms_roles: [Compliance Administrator, IB Administrator]
effort_hours: 8
---

## Cuándo usar

- Organizaciones con requisitos regulatorios de separación de información
  (bancos: separación trading/research, firmas legales: conflictos de interés)
- Cuando un agente con acceso a datos de un segmento no debe poder
  procesar o transferir información a otro segmento
- Post-auditoría del Pilar 1 revela que agentes cruzan silos organizacionales

## Qué cubren Information Barriers

IB controla la comunicación y colaboración entre segmentos en:
- Microsoft Teams (chats, canales)
- SharePoint Online
- OneDrive
- Exchange Online

**Limitación**: IB no controla directamente las llamadas de Graph API de agentes.
Para agentes autónomos, complementar con Conditional Access y RBAC granular
(skills del Pilar 2 y 3).

## Workflow

### Paso 1 — Definir segmentos organizacionales

Identificar los grupos que deben estar separados:

```powershell
# Conectar a Security & Compliance PowerShell
Connect-IPPSSession

# Crear segmento para el área financiera
New-OrganizationSegment -Name "Finance" `
  -UserGroupFilter "Department -eq 'Finance'"

# Crear segmento para el área legal
New-OrganizationSegment -Name "Legal" `
  -UserGroupFilter "Department -eq 'Legal'"

# Crear segmento para agentes AI del área financiera
# Los SPs de agentes se mapean vía UserPrincipalName o DisplayName
New-OrganizationSegment -Name "AI-Finance-Agents" `
  -UserGroupFilter "DisplayName -like 'agent-finance-*'"
```

**Nota**: IB usa atributos de Entra ID para definir segmentos.
Los service principals de agentes deben tener atributos que permitan filtrarlos.

### Paso 2 — Definir políticas de IB

```powershell
# Política: Finance no puede comunicarse con Legal
New-InformationBarrierPolicy -Name "Finance-Legal-Block" `
  -AssignedSegment "Finance" `
  -SegmentsBlocked "Legal" `
  -State Active

# Política: AI-Finance-Agents solo puede acceder a datos de Finance
New-InformationBarrierPolicy -Name "AI-Finance-Agents-Restrict" `
  -AssignedSegment "AI-Finance-Agents" `
  -SegmentsAllowed "Finance" `
  -State Active
```

### Paso 3 — Aplicar las políticas

```powershell
# Aplicar todas las políticas activas
Start-InformationBarrierPoliciesApplication
```

La aplicación puede tardar varias horas dependiendo del tamaño del tenant.
Monitorear con:

```powershell
Get-InformationBarrierPoliciesApplicationStatus
```

### Paso 4 — Verificar en Teams y SharePoint

**Teams**: Intentar que un agente del segmento Finance inicie chat con alguien de Legal.
Debe ser bloqueado automáticamente.

**SharePoint**: Los sites asignados a segmentos deben respetar IB.
Verificar que el agente Finance no puede acceder a sites del segmento Legal.

### Paso 5 — Modo de compatibilidad IB para SharePoint

```powershell
# Habilitar IB en SharePoint/OneDrive
Set-SPOTenant -InformationBarriersSuspension $false
```

Esto aplica las políticas IB a SharePoint y OneDrive además de Teams.

### Paso 6 — Monitorear compliance con IB

```kql
// Ver queries/sentinel-information-barriers.kql
```

## Verificación

- [ ] Segmentos definidos con filtros correctos en Entra ID
- [ ] Políticas de IB en estado Active
- [ ] `Start-InformationBarrierPoliciesApplication` completado
- [ ] Test de comunicación bloqueada exitoso (Finance ↔ Legal bloqueado)
- [ ] IB habilitado en SharePoint/OneDrive
- [ ] Monitoreo activo en Sentinel

## Notas de implementación

- Information Barriers requiere licencia M365 E5 Compliance o Microsoft 365 E5 — verificar disponibilidad antes de comenzar la implementación
- IB en SharePoint puede tardar hasta 24 horas en propagarse completamente después de habilitar la policy — planificar la ventana de implementación con anticipación
- Los segmentos de agentes AI requieren que los SPs tengan atributos de Entra que permitan filtrarlos — usar convención de nombres en `DisplayName` o extensiones de directorio para identificarlos
- Information Barriers no se puede configurar via Graph API en todos los escenarios — usar Security & Compliance PowerShell para la configuración inicial
