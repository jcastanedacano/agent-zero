# Skills Schema v1.0

Standard format for every skill in this repository.
Based on agentskills.io, adapted for the Microsoft Security stack.

---

## Directory structure per skill

```
skills/{pillar}/{skill-name}/
├── SKILL.md          ← Definition (YAML frontmatter + Markdown)
├── queries/
│   └── *.kql         ← KQL for your Sentinel workspace (validated against existing tables)
└── references/
    └── frameworks.md ← ATLAS, D3FEND, NIST AI RMF, CSF 2.0 mappings
```

---

## YAML Frontmatter

```yaml
---
name: {skill-kebab-case}             # max 64 chars, no version
version: "1.0"
pillar: {discover|govern|secure|protect|detect}
subdomain: {ms-copilot-studio|ms-entra|ms-sentinel|ms-purview|ms-foundry}
description: >-
  {what it does} {on which MS product} {what risk it mitigates} — ~30 tokens
tags: [{pillar}, {ms-product}, {scenario}]
atlas_techniques: []   # MITRE ATLAS (2026.09) — AML.Txxxx[.xxx], verify IDs at atlas.mitre.org
d3fend_techniques: []  # MITRE D3FEND v1.3 — D3-xxxx
nist_ai_rmf: []        # GOVERN|MAP|MEASURE|MANAGE-x.x
nist_csf: []           # GV|ID|PR|DE|RS|RC + category
ms_license: []         # minimum licenses required
ms_roles: []           # required Entra ID roles
effort_hours: {n}

# --- Universal Skill Format security manifest (OWASP AST10) ---
# Required for enterprise skill registries and cross-platform portability.
# Addresses AST01 (malicious skills), AST04 (insecure metadata), AST08 (poor scanning),
# and AST10 (cross-platform reuse) from the OWASP Agentic Skills Top 10 (2026).
risk_tier: {low|medium|high|critical}  # Blast radius classification
permissions:
  read_files: {true|false}
  write_files: {true|false}
  network_access: {true|false}
  deny_write:                          # Paths this skill must never modify
    - ".claude/settings.json"
    - "SOUL.md"
    - "MEMORY.md"
scan_status:
  last_scanned: {ISO-8601 date}        # Date of last security scan
  scanner: {tool name}                 # e.g., NVIDIA SkillSpector, manual review
  result: {clean|flagged|pending}
content_hash: {sha256-hex}             # SHA-256 of SKILL.md at time of scan
signature: {base64-sig}                # Optional: signing key for provenance
---
```

### risk_tier guidance

| Tier | Criteria | Examples |
|------|----------|---------|
| `low` | Read-only; no external calls; no credential access | Discovery queries, read-only KQL |
| `medium` | Writes to tenant config; calls internal APIs | DLP policy updates, CA policy creation |
| `high` | External network access; credential or key management | MCP server connectors, Key Vault access |
| `critical` | Can modify identity, revoke tokens, or delete data | Agent decommission, role assignment |

### deny_write defaults

All skills **must** include `deny_write` for at minimum:
- `.claude/settings.json` — prevents hook injection (AST02 supply chain vector)
- `SOUL.md` / `MEMORY.md` — prevents persistent instruction backdoors (AST01 malicious skill pattern)

## Required Markdown sections

```markdown
## When to use
## Prerequisites
## Workflow
## Verification
## Environment notes
```

## Naming convention

`{pillar}-{verb}-{object}-{product}`

- `discover-inventory-agents-copilot-studio`
- `govern-ca-policy-workload-identity`
- `detect-alert-prompt-injection-sentinel`
