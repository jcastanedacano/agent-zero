# Track B — Arquitecto / Consultor de Seguridad

**Audiencia:** Arquitectos de seguridad, consultores de seguridad, ingenieros de identidad, líderes técnicos de TI  
**Duración:** 8 horas (día completo)  
**Formato:** Labs hands-on en tenant M365 E5 demo con controles Microsoft reales  
**Output del participante:** Gap Assessment completado + roadmap de implementación de 90 días

---

## Prerrequisitos

- Tenant M365 E5 demo o CDX activo (ver [Prerequisites.md](../Facilitator-Kit/Prerequisites.md))
- Suscripción Azure con rol Contributor para despliegue del ARM template
- Roles en el tenant demo: Global Reader + Security Admin + Sentinel Contributor
- Familiaridad con Microsoft Entra ID, Microsoft Sentinel y Purview (nivel arquitecto)
- Recomendado: haber completado Track A o haber leído el resumen ejecutivo del framework

---

## Índice de módulos

| Módulo | Pilar | Lab | Duración |
|--------|-------|-----|----------|
| [01 — Discover & Prioritize](./Module-01-Discover.md) | Arquitectura de inventario de agentes | Defender AI Inventory + KQL de inventario | 90 min |
| [02 — Govern & Control](./Module-02-Govern.md) | Modelo de gobernanza y ciclo de vida | Entra Agent ID + Copilot Studio + DLP | 90 min |
| [03 — Secure Access](./Module-03-SecureAccess.md) | CA para identidades de agente | CA policy + What If + OAuth audit KQL | 90 min |
| [04 — Protect Data](./Module-04-ProtectData.md) | Protección de datos y DLP para IA | Purview DLP + SharePoint Advanced Management | 90 min |
| [05 — Detect & Respond](./Module-05-DetectRespond.md) | Arquitectura de detección y respuesta | Sentinel rules + Logic App playbook | 90 min |

Tiempo total de lab: ~7.5 horas. Reservar 30 minutos para consolidación del Gap Assessment y roadmap al cierre.

---

## Output del participante — Gap Assessment

Cada módulo contribuye una sección del Gap Assessment Template. Al finalizar el Track B, el participante tiene:

```
Gap Assessment — [Nombre de la Organización]
├── Domain 1 — Inventario de agentes con blind spots documentados
├── Domain 2 — Modelo de gobernanza configurado con gaps y owners asignados
├── Domain 3 — CA policy válida para agentes + evidencia de What If
├── Domain 4 — DLP policy para AI interactions + inventario de sitios
└── Domain 5 — Analytics rules activas + Logic App de enforcement
    └── Roadmap de 90 días consolidado con priorización por dominio
```

Usar el [Gap Assessment Template](./Templates/Gap-Assessment-Template.md) para documentar hallazgos durante cada módulo.

---

## Despliegue del entorno de lab

Desplegar el workspace de Sentinel con datos demo antes del inicio del lab:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fjcastanedacano%2Fmicrosoft-agentic-security-labs%2Fmain%2FARM-Templates%2Fazuredeploy.json)

→ Ver [ARM Templates README](../ARM-Templates/README.md) para detalles de parámetros y costo estimado.

---

## KQL Library

Todas las queries usadas en los labs están disponibles en [`/KQL-Library`](../KQL-Library/) para referencia, adaptación y despliegue en producción.
