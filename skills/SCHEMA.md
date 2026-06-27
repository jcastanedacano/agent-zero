# Skills Schema v1.0

Formato estándar para todas las skills de este repositorio.
Basado en agentskills.io, adaptado para Microsoft Security stack.

---

## Estructura de directorios por skill

```
skills/{pilar}/{skill-name}/
├── SKILL.md          ← Definición (YAML frontmatter + Markdown)
├── queries/
│   └── *.kql         ← KQL para {workspace-name} (validado contra tablas existentes)
└── references/
    └── frameworks.md ← Mapeos ATLAS, D3FEND, NIST AI RMF, CSF 2.0
```

---

## YAML Frontmatter

```yaml
---
name: {skill-kebab-case}             # max 64 chars, sin versión
version: "1.0"
pillar: {discover|govern|secure|protect|detect}
subdomain: {ms-copilot-studio|ms-entra|ms-sentinel|ms-purview|ms-foundry}
description: >-
  {qué hace} {en qué producto MS} {qué riesgo mitiga} — ~30 tokens
tags: [{pillar}, {ms-product}, {scenario}]
atlas_techniques: []   # MITRE ATLAS v5.4 — AML.Txxxx
d3fend_techniques: []  # MITRE D3FEND v1.3 — D3-xxxx
nist_ai_rmf: []        # GOVERN|MAP|MEASURE|MANAGE-x.x
nist_csf: []           # GV|ID|PR|DE|RS|RC + categoría
ms_license: []         # licencias mínimas requeridas
ms_roles: []           # roles Entra ID requeridos
effort_hours: {n}
---
```

## Secciones Markdown obligatorias

```markdown
## Cuándo usar
## Prerrequisitos
## Workflow
## Verificación
## Notas {workspace-name}
```

## Convención de nombres

`{pilar}-{verbo}-{objeto}-{producto}`

- `discover-inventory-agents-copilot-studio`
- `govern-ca-policy-workload-identity`
- `detect-alert-prompt-injection-sentinel`
