# Pilar 02 — Govern & Control | Track A

**Duración del módulo:** 45 minutos

**Objetivo de aprendizaje:**
Al finalizar este módulo, el participante será capaz de evaluar la madurez del modelo de gobernanza de agentes de su organización, identificar los gaps más críticos de ownership y ciclo de vida, y priorizar las decisiones de política que reducen el riesgo de deriva del grafo de identidad en el contexto de su entorno Microsoft 365.

**Agenda del módulo:**

| Tiempo | Actividad | Tipo |
|--------|-----------|------|
| 10 min | Gobernanza de agentes: por qué es diferente a la gobernanza de aplicaciones tradicionales | Exposición |
| 10 min | Los cuatro gaps más frecuentes: sin dueño, makers sin controles, sin ciclo de vida, deriva del grafo | Exposición |
| 20 min | Ejercicio: Evaluación de madurez de gobernanza | Ejercicio |
| 5 min | Cierre y conexión al pilar 3 | Discusión |

---

**Contenido core (puntos que el facilitador debe cubrir):**

1. **El problema del dueño ausente:** Cuando un agente no tiene un dueño técnico asignado, ningún equipo es responsable de sus permisos, su comportamiento ni su descomisión. En entornos M365 E5, el vector más frecuente es Agent Builder: cualquier usuario licenciado puede publicar un agente que entra en producción sin aprobación.

2. **Deriva del grafo de identidad:** Los agentes acumulan permisos con el tiempo sin revisión. Un agente que inicia con `Sites.Read.All` puede terminar con `Mail.ReadWrite` después de varias integraciones. Sin un proceso de revisión de permisos, el grafo de identidad del agente diverge de lo que fue aprobado originalmente.

3. **Controles Microsoft aplicables:** Entra Agent ID provee identidad dedicada y gestionable por agente. El flujo de aprobación de Copilot Studio controla la publicación. Foundry RBAC y los controles de API restringen lo que los agentes pueden hacer en Azure AI. Power Platform DLP clasifica y bloquea conectores no autorizados.

4. **El ciclo de vida como control de seguridad:** Un agente descomisionado que mantiene permisos activos es un vector de ataque. El proceso de baja debe incluir revocación de tokens, eliminación de permisos y cierre del registro en Agent 365.

---

**Ejercicio / Lab:**

- **Nombre:** Evaluación de madurez de gobernanza
- **Modalidad:** Individual
- **Descripción:**
  1. El participante recibe una rúbrica con 5 dimensiones: ownership, proceso de aprobación, revisión de permisos, ciclo de vida y trazabilidad de makers
  2. Para cada dimensión, selecciona el nivel de madurez de su organización: Inicial / En desarrollo / Definido / Gestionado
  3. Identifica la dimensión con menor madurez y describe en dos oraciones qué decisión ejecutiva podría avanzarla un nivel
  4. Calcula el nivel de madurez promedio de gobernanza
  5. Registra el resultado en la sección "Domain 2" de su Risk Posture Map
- **Herramientas requeridas:** Rúbrica de madurez (provista por el facilitador); no requiere acceso a sistemas
- **Entregable:** Madurez de gobernanza documentada en el Risk Posture Map + una decisión ejecutiva priorizada para la dimensión más débil

---

**Preguntas de cierre para el facilitador:**
- ¿Existe hoy en su organización un proceso formal de aprobación antes de que un agente de IA entre en producción? ¿Quién lo aprueba y con qué criterios?
- Si un agente que se desplegó hace 6 meses ya no lo usa el equipo que lo creó, ¿qué pasaría con sus permisos? ¿Quién lo detectaría?

**Conexión al siguiente pilar:** Saber quién es dueño de un agente no resuelve el problema de qué puede hacer ese agente. El Pilar 03 trata el control de acceso: cómo garantizar que los agentes operan con privilegio mínimo verificable y qué significa la identidad de un agente en el contexto de las políticas de Conditional Access.

→ [Módulo 03 — Secure Access](./Module-03-SecureAccess.md)
