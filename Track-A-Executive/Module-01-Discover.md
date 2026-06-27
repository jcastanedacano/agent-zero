# Pilar 01 — Discover & Prioritize | Track A

**Duración del módulo:** 45 minutos

**Objetivo de aprendizaje:**
Al finalizar este módulo, el participante será capaz de articular el riesgo de la IA en la sombra para su organización, identificar las categorías de agentes que podrían estar operando sin visibilidad, y tomar una decisión fundada sobre la inversión en capacidades de inventario en el contexto de una estrategia de seguridad empresarial.

**Agenda del módulo:**

| Tiempo | Actividad | Tipo |
|--------|-----------|------|
| 10 min | El problema de la IA no gestionada: por qué el inventario es el punto cero de cualquier estrategia | Exposición |
| 10 min | Categorías de riesgo: Shadow AI, exposición de identidad, agentes locales sin telemetría | Exposición |
| 20 min | Ejercicio: Mapa de riesgo de agentes en tu organización | Ejercicio |
| 5 min | Cierre: preguntas de reflexión y conexión al pilar 2 | Discusión |

---

**Contenido core (puntos que el facilitador debe cubrir):**

1. **Shadow AI como vector primario:** Los agentes de IA se despliegan hoy sin aprobación formal — por equipos de negocio, desarrolladores individuales y proveedores externos. El riesgo no es hipotético; es la condición base de cualquier organización con M365 E5 activo.

2. **El problema de los agentes locales:** Los agentes que corren en endpoints (fuera de la nube) no generan telemetría en Defender ni en Purview. La brecha no es de política — es de visibilidad. Sin endpoint connector activo, no hay señal.

3. **Controles Microsoft aplicables:** Purview DSPM for AI y Defender AI Agent Inventory permiten construir un inventario de agentes cloud. SharePoint Advanced Management cierra la exposición de datos que esos agentes consumen. Agent 365 provee el registro centralizado.

4. **El costo de no actuar:** Cada agente no gestionado que accede a SharePoint hereda los errores de ACL del corpus. Un solo agente con acceso excesivo puede exponer datos sensibles a todos los usuarios que interactúan con él.

---

**Ejercicio / Lab:**

- **Nombre:** Mapa de riesgo de agentes
- **Modalidad:** Individual con puesta en común grupal
- **Descripción:**
  1. El participante recibe una tarjeta con 8 categorías de agentes posibles (Copilot Studio, Power Automate con IA, agentes de terceros, scripts locales con LLM, agentes de RRHH/ventas/IT, etc.)
  2. Marca cuáles cree que existen hoy en su organización (con o sin certeza)
  3. Para cada uno que marcó, responde: ¿tiene dueño técnico identificado? ¿está en algún inventario?
  4. Calcula su "score de visibilidad": porcentaje de agentes marcados con dueño conocido sobre total marcado
  5. Comparte el resultado con el grupo y discute qué categoría genera más sorpresa
- **Herramientas requeridas:** Tarjeta impresa o digital con las 8 categorías (provista por el facilitador); no se requiere acceso a ningún sistema
- **Entregable:** Score de visibilidad personal + lista de categorías de agentes sin dueño identificado, incorporada al Risk Posture Map del participante

---

**Preguntas de cierre para el facilitador:**
- Si mañana su equipo de seguridad les preguntara "¿cuántos agentes de IA activos tiene la organización?", ¿podrían responder con certeza? ¿Qué les impediría responder?
- ¿Qué categoría de agente de la tarjeta les generó más incertidumbre, y qué decisión ejecutiva podría reducir esa incertidumbre en los próximos 30 días?

**Conexión al siguiente pilar:** Tener visibilidad del landscape de agentes es el primer paso — pero visibilidad sin ownership es una lista sin responsables. El Pilar 02 responde la pregunta de gobernanza: quién es dueño de cada agente, qué política lo rige y cómo se gestiona su ciclo de vida.

→ [Módulo 02 — Govern & Control](./Module-02-Govern.md)
