# Pilar 02 — Govern & Control | Track B

**Duración del módulo:** 90 minutos

**Objetivo de aprendizaje:**
Al finalizar este módulo, el participante será capaz de diseñar un modelo de gobernanza de agentes que cubra ownership, aprobación, ciclo de vida y políticas DLP, configurar Entra Agent ID y el flujo de aprobación de Copilot Studio en un tenant demo, detectar el bypass de Agent Builder mediante KQL, y documentar los gaps de gobernanza de su organización con un roadmap de remediación priorizado.

**Agenda del módulo:**

| Tiempo | Actividad | Tipo |
|--------|-----------|------|
| 20 min | Modelo de gobernanza agentic: dimensiones, roles y flujos de aprobación | Exposición |
| 15 min | Entra Agent ID vs. Service Principal: diferencias de schema, targeting en CA, y valor forense | Exposición |
| 45 min | Lab: Entra Agent ID + aprobación Copilot Studio + DLP Power Platform + KQL governance | Lab |
| 10 min | Gap assessment: madurez de gobernanza y roadmap | Discusión |

---

**Contenido core (puntos que el facilitador debe cubrir):**

1. **El bypass de Agent Builder como gap sistémico:** Agent Builder (M365 Copilot) activa agentes inmediatamente sin pasar por el flujo de aprobación de Copilot Studio. Es un bypass de diseño a nivel de producto — no un error de configuración. El control compensatorio es una política de Conditional Access sobre el App ID de Agent Builder, o un alert rule en Sentinel sobre `AuditLogs` filtrando `AgentSource == "AgentBuilder"`.

2. **Deriva del grafo como riesgo acumulado:** Sin un proceso de revisión periódica de permisos, los agentes acumulan scopes de OAuth sin correlación con aprobaciones. La deriva es gradual e invisible: `Sites.Read.All` se convierte en `Sites.ReadWrite.All` después de que alguien en el equipo de desarrollo lo agrega sin un proceso de change management. La solución arquitectónica es PIM just-in-time para permisos de agente, no solo para roles humanos.

3. **Controles Microsoft aplicables:** Entra Agent ID establece identidad gestionable por agente, separada de las identidades de usuario y de los service principals genéricos. Copilot Studio governance habilita el flujo de aprobación antes de publicación. Foundry RBAC + controles a nivel de API restringen qué pueden hacer los agentes en Azure AI. Power Platform DLP clasifica y bloquea conectores por categoría (Business / Non-business / Blocked).

4. **El ciclo de vida como control de seguridad activo:** La descomisión de un agente debe incluir: revocación de tokens, eliminación de permisos en Entra, cierre del registro en Agent 365, y archivo de la documentación de ownership. Un agente "abandonado" con permisos activos es un vector de ataque con identidad legítima.

---

**Ejercicio / Lab:**

- **Nombre:** Implementación del modelo de gobernanza en tenant demo
- **Modalidad:** Individual
- **Descripción:**
  1. En Entra ID → App registrations, crear `demo-sales-agent` con permiso `Sites.Read.All` y marcarlo como Entra Agent ID en el manifest (`"tags": ["agent365", "EntraAgentID"]`)
  2. En Copilot Studio admin center → Settings → Agent publishing, habilitar el flujo de aprobación y configurar un aprobador
  3. En Power Platform admin center, crear la política DLP "Agentic AI — Restrict External Connectors" bloqueando HTTP y HTTP with Azure AD
  4. Ejecutar las queries de governance del KQL Library (P02-Governance-Gaps.kql): agentes sin Entra Agent ID, agentes publicados sin aprobación, deriva del grafo
  5. Completar la sección "Domain 2 — Govern" del Gap Assessment Template con los hallazgos reales del tenant demo
- **Herramientas requeridas:** Entra ID (App registrations + Manifest editor), Copilot Studio admin center, Power Platform admin center, Microsoft Sentinel (Logs), KQL Library P02, Gap Assessment Template
- **Entregable:** Entra Agent ID creado y verificado en Agent 365 Registry + sección Domain 2 del Gap Assessment completada con gaps identificados, owners asignados y fechas objetivo

---

**Preguntas de cierre para el facilitador:**
- Al ejecutar la query de agentes sin Entra Agent ID, ¿qué porcentaje del total de agentes apareció en ese resultado? ¿Qué proceso de su organización los habría registrado correctamente?
- Si tuvieran que implementar el modelo de gobernanza diseñado hoy en producción, ¿cuál sería el primer obstáculo organizacional (no técnico) que encontrarían?

**Conexión al siguiente pilar:** La gobernanza define quién aprueba un agente y qué proceso sigue. El Pilar 03 toma esas identidades aprobadas y define qué pueden acceder — least privilege verificable, CA policies específicas para agentes, y cómo auditar el OAuth consent drift antes de que escale.

→ [Módulo 03 — Secure Access](./Module-03-SecureAccess.md)
