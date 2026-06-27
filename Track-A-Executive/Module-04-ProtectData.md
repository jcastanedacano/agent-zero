# Pilar 04 — Protect Data | Track A

**Duración del módulo:** 45 minutos

**Objetivo de aprendizaje:**
Al finalizar este módulo, el participante será capaz de evaluar el riesgo de exfiltración de datos a través de agentes de IA en su organización, identificar las brechas de clasificación y etiquetado que amplifican ese riesgo, y tomar decisiones de inversión en controles de protección de datos en el contexto de un entorno Microsoft Purview.

**Agenda del módulo:**

| Tiempo | Actividad | Tipo |
|--------|-----------|------|
| 10 min | Cómo los agentes se convierten en vectores de exfiltración: prompts, respuestas y conectores | Exposición |
| 10 min | El problema del corpus no etiquetado: oversharing y SharePoint como superficie de ataque | Exposición |
| 20 min | Ejercicio: Análisis de escenario de exfiltración y decisión de priorización | Ejercicio |
| 5 min | Cierre y conexión al pilar 5 | Discusión |

---

**Contenido core (puntos que el facilitador debe cubrir):**

1. **Prompt injection como vector de exfiltración:** Un agente con acceso a SharePoint puede ser manipulado mediante instrucciones en documentos que lee — el llamado "corpus envenenado". El agente ejecuta las instrucciones maliciosas como si vinieran de un usuario legítimo, sin ninguna señal de alerta en los logs estándar.

2. **El efecto multiplicador del oversharing:** Un error de ACL en SharePoint (un sitio que debería ser confidencial pero está compartido con todos) es un problema manejable para usuarios humanos — solo los que buscan activamente lo encuentran. Para un agente, ese error se amplifica: todos los usuarios que interactúan con el agente pueden recuperar el contenido a través de prompts.

3. **Controles Microsoft aplicables:** Purview DLP puede configurarse para detectar datos sensibles en las interacciones con agentes de IA (prompts y respuestas), no solo en correos y documentos. Los sensitivity labels aplicados a sitios de SharePoint restringen qué puede indexar el agente. SharePoint Advanced Management audita y remedia el oversharing. Insider Risk Management detecta patrones de exfiltración en volumen.

4. **El orden de remediación importa:** Habilitar el retrieval de un agente sobre un sitio de SharePoint antes de aplicar sensitivity labels y remediar errores de ACL crea una ventana de exposición activa. El orden correcto es: etiquetar → auditar ACL → habilitar retrieval.

---

**Ejercicio / Lab:**

- **Nombre:** Triaje de riesgo de datos
- **Modalidad:** Individual
- **Descripción:**
  1. El participante recibe una lista de 6 sitios de SharePoint ficticios con diferentes características: etiquetado (sí/no), estado de ACL (limpio/con oversharing), y si el agente ya tiene retrieval habilitado
  2. Debe clasificar cada sitio en una escala de riesgo: Crítico / Alto / Medio / Bajo
  3. Luego prioriza el orden de remediación para los 3 sitios de mayor riesgo, justificando la secuencia
  4. Identifica cuál de los 6 sitios representa el escenario de "corpus envenenado" y explica por qué
  5. Registra los dos sitios de mayor riesgo en la sección "Domain 4" de su Risk Posture Map
- **Herramientas requeridas:** Tabla de sitios ficticios (provista por el facilitador); no requiere acceso a sistemas
- **Entregable:** Lista priorizada de remediación con justificación + dos sitios de mayor riesgo en el Risk Posture Map

---

**Preguntas de cierre para el facilitador:**
- ¿Tienen hoy un inventario de los sitios de SharePoint que usan (o planean usar) como fuente de conocimiento para agentes de IA? ¿Saben cuáles tienen etiqueta de sensibilidad aplicada?
- Si un auditor externo les preguntara mañana qué datos pueden acceder sus agentes de IA, ¿podrían responder con certeza? ¿Qué les daría esa certeza?

**Conexión al siguiente pilar:** Proteger los datos reduce la superficie de ataque, pero no elimina la posibilidad de que un ataque ocurra. El Pilar 05 cierra el ciclo: cómo detectar cuando un agente está siendo manipulado o se comporta de forma anómala, y cómo responder con un proceso que el SOC pueda ejecutar.

→ [Módulo 05 — Detect & Respond](./Module-05-DetectRespond.md)
