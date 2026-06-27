---
name: protect-sensitivity-labels-ai-outputs
version: "1.0"
pillar: protect
subdomain: ms-purview-ai
description: >-
  Configura auto-labeling en Purview para que documentos y archivos generados
  o procesados por agentes AI hereden sensitivity labels apropiados, garantizando
  que outputs de agentes con datos sensibles sean clasificados y protegidos
  con cifrado y restricciones de acceso automáticamente.
tags: [protect, purview, sensitivity-labels, auto-labeling, classification, ai-outputs]
atlas_techniques: [AML.T0048, AML.T0057]
d3fend_techniques: [D3-DLP, D3-EAC]
nist_ai_rmf: [MANAGE-2.2, GOVERN-6.1]
nist_csf: [PR.DS-01, PR.DS-02]
ms_license: [Microsoft Purview E3, Azure Information Protection P2]
ms_roles: [Compliance Administrator, Information Protection Administrator]
effort_hours: 6
---

## Cuándo usar

- Agentes que generan documentos, reportes o archivos como output
- Agentes con acceso a datos ya clasificados que podrían copiar/transformar contenido
- Cuando los outputs de agentes necesitan heredar la clasificación de los datos fuente

## Restricción de implementación

La creación de sensitivity labels y auto-labeling policies tiene soporte
limitado vía ARM/API. Configurar via **Microsoft Purview Compliance Portal**
es el camino confiable para la configuración inicial.
La activación y ajustes menores pueden hacerse vía Graph API
(`/beta/informationProtection/policy/labels`).

## Jerarquía recomendada de labels para outputs de AI

```
Public
  └── Internal Use Only
        └── Confidential
              ├── Confidential \ AI-Generated        ← outputs de agentes
              └── Confidential \ Customer Data
                    └── Highly Confidential
                          └── Highly Confidential \ AI-Generated
```

El sub-label `AI-Generated` permite identificar qué contenido fue producido
o procesado por un agente, independientemente del nivel de sensibilidad.

## Workflow

### Paso 1 — Auditar sensitivity labels existentes en el tenant

```
Purview Compliance Portal → Information protection → Labels
```

Si no hay estructura de labels: crear jerarquía base antes de continuar.
Si ya existe: evaluar si necesita sub-labels para AI-Generated content.

### Paso 2 — Crear sub-label AI-Generated

```
Information protection → Labels → [Confidential] → Add sub-label
```

Configuración del sub-label:
- **Name**: `AI-Generated`
- **Display name**: `Confidential / AI-Generated`
- **Description**: "Contenido generado o procesado por un agente AI"
- **Encryption**: heredar del label padre o configurar específico
- **Content marking**: agregar watermark "AI Generated - Review before sharing"
- **Auto-labeling**: No (se configura en política separada)

### Paso 3 — Crear política de auto-labeling para outputs de agentes

```
Information protection → Auto-labeling policies → Create policy
```

Configuración:
- **Name**: `AutoLabel-AI-Agent-Outputs`
- **Locations**: SharePoint sites donde agentes depositan outputs,
  OneDrive de usuarios que usan agentes, Exchange si aplica
- **Rules**:
  - Content contains sensitive info types: [tipos relevantes del tenant]
  - OR content was created/modified by: [service principals de agentes conocidos]
- **Label to apply**: `Confidential / AI-Generated`
- **Mode**: Simulation first (7 días), luego enforcement

### Paso 4 — Configurar herencia de label en Copilot Studio

Para agentes que acceden a documentos ya clasificados:

```
Purview → Information protection → Settings → Inheritance
→ Enable label inheritance from email attachments and documents
```

Cuando un agente extrae contenido de un documento `Confidential`,
el output debe heredar al menos ese nivel de clasificación.

### Paso 5 — Validar en simulation mode

```
Auto-labeling policies → [PolicyName] → Simulation results
```

Revisar qué archivos serían etiquetados. Ajustar reglas para eliminar
falsos positivos antes de activar enforcement.

### Paso 6 — Activar y monitorear

```
Auto-labeling policies → [PolicyName] → Turn on policy
```

Monitorear en Sentinel con queries de `MicrosoftDataLossPrevention`
y `PurviewAuditLog`.

```kql
// Ver queries/sentinel-label-coverage.kql
```

## Verificación

- [ ] Sub-label `AI-Generated` creado bajo `Confidential`
- [ ] Auto-labeling policy en simulation mode retorna matches esperados
- [ ] Falsos positivos revisados y reglas ajustadas
- [ ] Policy en enforcement activo
- [ ] Documentos de output de agentes muestran label aplicado
- [ ] Watermark visible en documentos etiquetados

## Notas de implementación

- Graph API beta endpoint para labels: `/beta/informationProtection/policy/labels` — verificar disponibilidad y estabilidad antes de usar en scripts de producción
- Auto-labeling puede tardar hasta 24 horas en procesar archivos existentes en SharePoint — no asumir cobertura inmediata al activar la policy
- Para validar auto-labeling: crear un documento de prueba con datos sintéticos tipo tarjeta de crédito y confirmar que la label se aplica automáticamente dentro de las 24h
- Priorizar el etiquetado manual de sitios SharePoint usados como fuentes de conocimiento de agentes antes de habilitar retrieval
