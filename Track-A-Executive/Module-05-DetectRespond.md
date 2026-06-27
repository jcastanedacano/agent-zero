# Pilar 05 — Detect & Respond | Track A

**Duración del módulo:** 45 minutos

**Objetivo de aprendizaje:**
Al finalizar este módulo, el participante será capaz de evaluar la capacidad de detección y respuesta de su organización frente a incidentes agentic, identificar las brechas entre la postura de detección actual y lo que requiere un agente de IA integrado al SOC, y tomar decisiones de inversión y priorización para reducir el tiempo de respuesta ante incidentes generados por agentes.

**Agenda del módulo:**

| Tiempo | Actividad | Tipo |
|--------|-----------|------|
| 10 min | Agentes como señal de seguridad: por qué el SOC necesita una capa específica para IA agentic | Exposición |
| 10 min | Falsos negativos estructurales: por qué las detecciones genéricas no alcanzan para agentes | Exposición |
| 20 min | Ejercicio: Simulación de decisión ante incidente agentic | Roleplay |
| 5 min | Cierre y consolidación del Risk Posture Map | Discusión |

---

**Contenido core (puntos que el facilitador debe cubrir):**

1. **Jailbreak como vector de incidente:** Un intento de jailbreak exitoso convierte al agente en un ejecutor de instrucciones maliciosas con acceso legítimo a los sistemas de la organización. A diferencia de un malware, el agente comprometido opera dentro de los canales autorizados — lo que hace que las defensas perimetrales sean insuficientes.

2. **Anomalía de agente vs. anomalía de usuario:** Las herramientas de detección calibradas para comportamiento humano generan falsos negativos estructurales cuando monitorean agentes. Un agente que hace 5.000 llamadas a SharePoint en una hora es normal en su operación y puede ser un ataque — la diferencia está en el patrón, no en el volumen.

3. **Controles Microsoft aplicables:** Defender XDR integra señales de comportamiento de agentes. Microsoft Sentinel con el MCP server nativo permite consultar el estado de los agentes desde el contexto de investigación. Security Copilot acelera el triage de incidentes agentic. Purview Audit provee la cadena de custodia forense. Agent 365 correlaciona eventos de incidente con el registro de agentes.

4. **El objetivo de MTTR para agentes:** El tiempo de respuesta estándar de un SOC humano (30 min – 2 horas para contención) puede ser inadecuado para un agente comprometido que actúa en segundos. El objetivo debe ser automatización de la contención inicial con revisión humana posterior.

---

**Ejercicio / Lab:**

- **Nombre:** Mesa de crisis: incidente agentic
- **Modalidad:** Grupal (toda la sala, facilitador como moderador)
- **Descripción:**
  1. El facilitador presenta el escenario: "A las 2:47 AM, un analista de turno recibe una alerta de Sentinel: el agente de atención a clientes intentó acceder 847 veces a un sitio de SharePoint clasificado como Confidencial en 3 minutos. El agente tiene permiso de lectura sobre ese sitio, así que la alerta no bloquea el acceso."
  2. El facilitador hace las preguntas clave al grupo: ¿Revocan el token del agente de inmediato? ¿Escalan a CISO? ¿Notifican a clientes?
  3. El grupo debate cada decisión, el facilitador registra los puntos de desacuerdo
  4. El facilitador revela el desenlace: el acceso era legítimo — un proceso de indexación programado. Pero la organización no tenía documentación del comportamiento esperado del agente. Discusión: ¿cómo habrían diferenciado el incidente real del falso positivo?
  5. Cada participante registra en su Risk Posture Map: ¿tiene su organización un baseline documentado del comportamiento esperado de sus agentes?
- **Herramientas requeridas:** Descripción del escenario (proyectada); pizarra o tablero digital para registrar las decisiones del grupo
- **Entregable:** Risk Posture Map completo con las 5 secciones completadas (una por módulo) — entregable final del Track A

---

**Preguntas de cierre para el facilitador:**
- ¿Tiene su SOC hoy alertas específicas para comportamiento anómalo de agentes de IA, o usa las mismas alertas configuradas para usuarios humanos?
- Si tuvieran que revocar el acceso de un agente comprometido en los próximos 5 minutos, ¿saben quién tendría que hacer qué, y en qué sistema?

**Consolidación del Track A:**
Este módulo cierra el Risk Posture Map. El participante debe tener ahora:
- Un score de visibilidad de agentes (Pilar 01)
- Un nivel de madurez de gobernanza (Pilar 02)
- Una decisión de acceso documentada (Pilar 03)
- Una lista de sitios de SharePoint priorizados para remediación (Pilar 04)
- Un estado de capacidad de detección y respuesta (Pilar 05)

El Risk Posture Map completo es el insumo para encargar el Track B (arquitectos) y el Track C (SOC) a los equipos técnicos de la organización.
