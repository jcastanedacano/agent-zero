# Pilar 01 — Discover & Prioritize | Track B

**Duración del módulo:** 90 minutos

**Objetivo de aprendizaje:**
Al finalizar este módulo, el participante será capaz de diseñar una arquitectura de inventario de agentes de IA que cubra fuentes cloud y endpoints, configurar Defender AI Agent Inventory y Purview DSPM for AI en un tenant demo, identificar los blind spots estructurales del inventario, y producir un gap assessment de visibilidad para su organización.

**Agenda del módulo:**

| Tiempo | Actividad | Tipo |
|--------|-----------|------|
| 20 min | Arquitectura de descubrimiento: fuentes, tablas, conectores y blind spots por tipo de agente | Exposición |
| 15 min | Recorrido por `AIAgentsInfo`: schema, campos clave, limitaciones documentadas | Exposición |
| 45 min | Lab: Activación de Defender AI Agent Inventory + KQL de inventario | Lab |
| 10 min | Gap assessment: diseño del mapa de visibilidad de la organización | Discusión |

---

**Contenido core (puntos que el facilitador debe cubrir):**

1. **Topología de descubrimiento por tipo de agente:** Copilot Studio y Azure AI Foundry generan telemetría en `AIAgentsInfo`. Power Automate con pasos de IA aparece en `CloudAppEvents`. Los agentes locales (Claude Code, MCP servers, scripts con LLM) no generan señal cloud sin endpoint connector activo — este es el blind spot estructural que ningún control de Purview ni Defender resuelve por sí solo.

2. **Shadow AI como estado por defecto:** Agent Builder (M365 Copilot) permite a cualquier usuario licenciado crear y publicar agentes sin aprobación. Estos agentes aparecen en Agent 365 Registry pero sin Entra Agent ID, sin dueño técnico y sin revisión de DLP. No son excepciones — son el caso base en cualquier tenant M365 E5 con Copilot habilitado.

3. **Controles Microsoft aplicables:** Purview DSPM for AI mapea las interacciones de los agentes con datos sensibles — complementa pero no reemplaza el inventario de identidades. Defender AI Agent Inventory requiere conectores activos por plataforma. SharePoint Advanced Management audita qué sitios son accedidos por agentes. Agent 365 es el registro central, pero solo cubre agentes registrados.

4. **El costo del inventario incompleto:** Un agente no listado en el inventario no aparece en las políticas de Conditional Access, no tiene dueño técnico para escalada y no está sujeto a las analytics rules de Sentinel. La brecha de inventario es la brecha de todas las capas de seguridad posteriores.

---

**Ejercicio / Lab:**

- **Nombre:** Diseño del architecture de inventario de agentes
- **Modalidad:** Parejas
- **Descripción:**
  1. Acceder a Microsoft Defender XDR → AI Agent Inventory; verificar qué conectores están activos y qué tablas retornan datos
  2. En Sentinel → Logs, ejecutar la query de inventario completo de `AIAgentsInfo` del KQL Library (P01-Agent-Discovery.kql) y documentar el recuento por tipo y status de gestión
  3. Identificar qué categorías de agentes del entorno de la organización NO aparecerán en este inventario (agentes locales, third-party sin conector, etc.) — documentar como blind spots
  4. Diseñar en un diagrama el flujo de telemetría: qué agente → qué conector → qué tabla → qué query detecta → qué control aplica
  5. Completar la sección "Domain 1 — Discover" del Gap Assessment Template
- **Herramientas requeridas:** Microsoft Defender XDR (AI Agent Inventory), Microsoft Sentinel (Logs), KQL Library del repositorio, Gap Assessment Template
- **Entregable:** Diagrama de flujo de telemetría + sección Domain 1 del Gap Assessment completada con recuento real de agentes, blind spots identificados y recomendaciones de control

---

**Preguntas de cierre para el facilitador:**
- En su diagrama, ¿cuántos tipos de agente quedaron fuera del inventario cloud? ¿Qué arquitectura de endpoint (MDE onboarding, sensor local) resolvería esos blind spots?
- Si tuvieran que presentar el inventario de agentes a un comité de riesgo la semana que viene, ¿qué dato de la query ejecutada les generaría más preguntas de parte del comité, y cómo responderían?

**Conexión al siguiente pilar:** El inventario es el input del proceso de gobernanza. Sin saber qué agentes existen, no es posible asignar dueños ni crear políticas. El Pilar 02 toma la lista de agentes del inventario y responde: ¿quién es responsable de cada uno, qué proceso los aprueba, y cómo se gestiona su ciclo de vida?

→ [Módulo 02 — Govern & Control](./Module-02-Govern.md)
