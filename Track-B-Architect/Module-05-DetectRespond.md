# Pilar 05 — Detect & Respond | Track B

**Duración del módulo:** 90 minutos

**Objetivo de aprendizaje:**
Al finalizar este módulo, el participante será capaz de diseñar una arquitectura de detección y respuesta específica para agentes de IA, integrar las señales de comportamiento agentic en Microsoft Sentinel, crear analytics rules con enforcement automatizado vía Logic App, identificar los falsos negativos estructurales del modelo de detección actual, y completar el Gap Assessment con un roadmap de 90 días de implementación priorizado.

**Agenda del módulo:**

| Tiempo | Actividad | Tipo |
|--------|-----------|------|
| 20 min | Arquitectura SOC para agentes: fuentes de señal, tablas, cadena de detección a enforcement | Exposición |
| 15 min | Falsos negativos estructurales: por qué las detecciones calibradas para humanos fallan con agentes | Exposición |
| 45 min | Lab: Analytics rules en Sentinel + Logic App enforcement + KQL de detección | Lab |
| 10 min | Consolidación del Gap Assessment y roadmap de 90 días | Discusión |

---

**Contenido core (puntos que el facilitador debe cubrir):**

1. **Falsos negativos estructurales por calibración humana:** Las reglas de detección calibradas para comportamiento humano generan falsos negativos cuando monitorizan agentes. Un agente que hace 5.000 llamadas a SharePoint por hora puede estar operando normalmente o ejecutando una exfiltración — la diferencia está en el delta respecto a su baseline, no en el volumen absoluto. Sin un baseline por agente, cualquier umbral fijo genera falsos positivos o falsos negativos.

2. **Postura de detección vs. postura de enforcement:** Una organización con detección activa pero sin automatización de respuesta tiene un MTTR limitado por el tiempo de reacción humana. Para agentes que actúan en segundos, el objetivo arquitectónico es: detección automática → contención automática → revisión humana. El Logic App de revocación de token es el control de contención mínimo viable.

3. **Controles Microsoft aplicables:** Defender XDR integra señales de comportamiento de agentes con el contexto de identidad y dispositivo. Microsoft Sentinel con el MCP server nativo permite consultar el estado de los agentes desde el contexto de una investigación activa. Security Copilot acelera el triage de incidentes complejos. Purview Audit provee la cadena de custodia forense con inmutabilidad. Agent 365 correlaciona eventos de incidente con el registro de ownership del agente.

4. **El MCP server nativo de Sentinel como diferenciador arquitectónico:** El MCP server de Sentinel permite a un agente de seguridad (Security Copilot o custom) consultar el estado de incidentes, ejecutar queries KQL y actualizar el estado de una investigación directamente desde el contexto de conversación — sin salir de la interfaz de triage. Este es el puente entre la detección agentic y la respuesta agentic.

---

**Ejercicio / Lab:**

- **Nombre:** Arquitectura de detección y respuesta agentic en Sentinel
- **Modalidad:** Individual
- **Descripción:**
  1. En Microsoft Sentinel → Analytics, crear la regla "Agentic AI — Jailbreak Attempt Detected" usando la query del KQL Library (P05-Jailbreak-Detection.kql): frecuencia = 5 min, severity = High, entity mapping = AccountId
  2. Crear la regla "Agentic AI — Volume Spike Anomaly" con baseline dinámico usando `percentile()` sobre una ventana de 7 días — documentar por qué un umbral fijo falla para comportamiento de agentes
  3. En Azure Logic Apps, crear el playbook `playbook-revoke-agent-token` que: recibe el alert de Sentinel, llama a Graph API `POST /users/{id}/revokeSignInSessions`, agrega un comentario al incidente en Sentinel y envía email al dueño técnico del agente
  4. En Sentinel → Automation, crear una automation rule que ejecute el playbook cuando el alert name contiene "Jailbreak"
  5. Completar la sección "Domain 5 — Detect & Respond" del Gap Assessment Template y consolidar el roadmap de 90 días con todos los dominios
- **Herramientas requeridas:** Microsoft Sentinel (Analytics + Automation), Azure Logic Apps, Microsoft Graph API (Graph Explorer para validación), KQL Library P05, Gap Assessment Template
- **Entregable:** Dos analytics rules activas + Logic App playbook funcionando + automation rule configurada + Gap Assessment Template completo con roadmap de 90 días priorizado

---

**Preguntas de cierre para el facilitador:**
- Al diseñar el baseline dinámico para la regla de Volume Spike Anomaly, ¿qué ventana de tiempo usaron y por qué? ¿Cómo varía ese baseline si el agente tiene un patrón de uso muy diferente entre días laborables y fines de semana?
- En el roadmap de 90 días consolidado, ¿qué control del Gap Assessment tiene el mayor ROI de seguridad vs. esfuerzo de implementación? ¿Qué obstáculo organizacional (no técnico) es el que más demora la implementación de ese control?

**Consolidación del Track B:**
Este módulo cierra el Gap Assessment Template. El participante debe tener ahora:
- Arquitectura de inventario de agentes con blind spots documentados (Pilar 01)
- Modelo de gobernanza configurado en tenant demo (Pilar 02)
- CA policy válida para agentes validada con What If (Pilar 03)
- DLP policy para AI interactions + inventario de sitios (Pilar 04)
- Dos analytics rules activas + Logic App de enforcement (Pilar 05)

El Gap Assessment completo con roadmap de 90 días es el entregable formal del Track B y el insumo directo para el Track C (SOC Engineer), que operacionaliza la detección y respuesta diseñada aquí.

→ [Track C — SOC Engineer Workshop](../../Track-C-SOC-Engineer/README.md)
