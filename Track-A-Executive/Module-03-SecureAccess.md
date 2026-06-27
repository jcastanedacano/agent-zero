# Pilar 03 — Secure Access | Track A

**Duración del módulo:** 45 minutos

**Objetivo de aprendizaje:**
Al finalizar este módulo, el participante será capaz de explicar por qué las políticas de acceso diseñadas para usuarios humanos no aplican directamente a agentes de IA, evaluar el riesgo de configuraciones heredadas en su entorno, y tomar decisiones de inversión en controles de identidad para agentes en el contexto de una estrategia de Conditional Access empresarial.

**Agenda del módulo:**

| Tiempo | Actividad | Tipo |
|--------|-----------|------|
| 10 min | Identidad de agente vs. identidad humana: por qué la herencia de políticas crea falsa seguridad | Exposición |
| 10 min | Vectores de riesgo: CA heredada, permisos excesivos, OAuth sin control, lavado de identidad | Exposición |
| 20 min | Ejercicio: Escenario de decisión — Crisis de acceso agentic | Roleplay |
| 5 min | Cierre y conexión al pilar 4 | Discusión |

---

**Contenido core (puntos que el facilitador debe cubrir):**

1. **La trampa del MFA para agentes:** Las políticas de Conditional Access que requieren MFA para usuarios humanos son **inválidas para agentes** — un agente no puede completar MFA interactivo. Si una política aplica MFA como control de acceso a un agente, la política existe pero no ejecuta ninguna acción: ni bloquea ni autentica. El resultado es una falsa sensación de seguridad.

2. **Privilegio mínimo verificable:** Los agentes acumulan permisos sin un proceso sistemático de revisión. OAuth consent sin control permite que un agente obtenga `Mail.ReadWrite` sin que ningún administrador lo apruebe explícitamente. El gap no es de intención — es de proceso.

3. **Controles Microsoft aplicables:** Entra CA for Agents permite crear políticas específicas para identidades de agente usando `clientApplications.includeAgentIdServicePrincipals`. Entra ID Protection detecta comportamiento anómalo en service principals. PIM just-in-time limita el tiempo de exposición de permisos elevados. Defender for Cloud Apps audita el comportamiento de aplicaciones conectadas.

4. **Lavado de identidad como vector de riesgo:** Un agente puede operar bajo la identidad delegada de un usuario humano, ejecutando acciones que en los logs parecen realizadas por la persona. Sin identidad de agente separada (Entra Agent ID), la trazabilidad forense es imposible.

---

**Ejercicio / Lab:**

- **Nombre:** Crisis de acceso agentic
- **Modalidad:** Grupal (equipos de 3-4 personas)
- **Descripción:**
  1. El facilitador presenta el escenario: "Un agente de ventas desplegado hace 3 meses empieza a acceder a carpetas de RRHH en SharePoint. Los logs muestran la actividad bajo el nombre del Director de Ventas, quien afirma no haber iniciado esas acciones."
  2. Cada equipo tiene 8 minutos para responder: ¿cómo lo detectaron (o por qué no lo detectaron antes)? ¿Quién es responsable?
  3. El equipo debe decidir: ¿revocan el acceso del agente inmediatamente o investigan primero? ¿Cómo revocan si no saben exactamente qué permisos tiene?
  4. Cada equipo presenta su decisión en 2 minutos y la justifica
  5. El facilitador revela qué controles del Pilar 03 habrían prevenido o acelerado la detección
- **Herramientas requeridas:** Descripción del escenario (impresa o proyectada); tarjetas con los controles disponibles del Pilar 03
- **Entregable:** Decisión documentada por equipo: qué hicieron, quién fue responsable, y qué control habrían necesitado para responder más rápido. Incorporado al Risk Posture Map.

---

**Preguntas de cierre para el facilitador:**
- En el escenario planteado, ¿cuánto tiempo le tomaría a su organización identificar que fue un agente y no el Director de Ventas quien realizó las acciones? ¿Qué proceso lo haría posible?
- ¿Qué postura de riesgo es más aceptable: bloquear acceso del agente hasta confirmar la identidad, o mantenerlo activo mientras se investiga? ¿Qué factores de su organización determinan esa decisión?

**Conexión al siguiente pilar:** Controlar quién accede no es suficiente si los datos que el agente puede leer no están clasificados ni protegidos. El Pilar 04 cubre la protección de datos: cómo evitar que un agente con acceso legítimo se convierta en un vector de exfiltración.

→ [Módulo 04 — Protect Data](./Module-04-ProtectData.md)
