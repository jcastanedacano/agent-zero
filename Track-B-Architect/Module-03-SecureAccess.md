# Pilar 03 — Secure Access | Track B

**Duración del módulo:** 90 minutos

**Objetivo de aprendizaje:**
Al finalizar este módulo, el participante será capaz de diseñar una arquitectura de Conditional Access específica para identidades de agente, configurar una CA policy válida usando `clientApplications.includeAgentIdServicePrincipals`, validarla con la herramienta What If, detectar OAuth consent drift mediante KQL, y documentar la diferencia crítica entre CA para usuarios y CA para agentes en el Gap Assessment de su organización.

**Agenda del módulo:**

| Tiempo | Actividad | Tipo |
|--------|-----------|------|
| 20 min | Arquitectura de CA para agentes: scopes, grant controls válidos e inválidos, Blueprint-level vs. per-instance | Exposición |
| 15 min | OAuth consent sin control: cómo los agentes acumulan permisos no revisados | Exposición |
| 45 min | Lab: CA policy para agentes + What If validation + KQL de auditoría de acceso | Lab |
| 10 min | Gap assessment: control de acceso y roadmap de least privilege | Discusión |

---

**Contenido core (puntos que el facilitador debe cubrir):**

1. **La trampa de `grantControls: mfa` para agentes:** Una política de CA que usa `mfa` como grant control sobre identidades de agente es **silenciosamente inválida** — no bloquea ni autentica. El agente no puede completar MFA interactivo, y la política no genera ningún evento de enforcement en los logs. La única opción válida para bloquear un agente con CA es `"builtInControls": ["block"]`. Esto no es un bug — está documentado en la referencia de CA for workload identities.

2. **Blueprint-level CA como patrón de escala:** Crear una política de CA por instancia de agente falla a escala. La arquitectura correcta es un Blueprint-level CA que usa `clientApplications.includeAgentIdServicePrincipals` para cubrir todas las identidades de agente actuales y futuras derivadas del mismo blueprint — sin configuración por instancia.

3. **Controles Microsoft aplicables:** Entra CA for Agents con `clientApplications.includeAgentIdServicePrincipals` permite policies específicas para agentes. Entra ID Protection evalúa el riesgo de service principals y puede alimentar condiciones de CA. PIM just-in-time limita la ventana de exposición de permisos elevados. Defender for Cloud Apps audita OAuth consent y surface anomalías de aplicación.

4. **OAuth consent como vector de acumulación silenciosa:** Un agente puede acumular permisos adicionales sin que ningún administrador lo apruebe explícitamente si el consent flow no está restringido. La señal está en `AuditLogs` bajo `Add delegated permission grant` — sin correlación con un evento de aprobación, es un indicador de deriva.

---

**Ejercicio / Lab:**

- **Nombre:** Diseño e implementación de CA para identidades de agente
- **Modalidad:** Individual
- **Descripción:**
  1. En Entra ID → Security → Conditional Access, crear la política "Agentic AI — Risk-Based Access Control" con: usuarios = none, apps = `clientApplications.includeAgentIdServicePrincipals`, condición = sign-in risk medium+, grant = block
  2. Validar con la herramienta **What If**: confirmar que la política aplica a `demo-sales-agent` con riesgo Medium, y que NO aplica a cuentas de usuario
  3. Intentar configurar la misma política con `grantControls: mfa` — documentar que la herramienta What If no genera enforcement y registrar el hallazgo en el Gap Assessment
  4. Ejecutar las queries del KQL Library (P03-Access-Anomalies.kql): OAuth consent sin revisión, sign-ins fuera de horario, agentes con scopes excesivos
  5. Completar la sección "Domain 3 — Secure Access" del Gap Assessment Template
- **Herramientas requeridas:** Entra ID (Conditional Access + What If), Microsoft Sentinel (Logs), KQL Library P03, Gap Assessment Template
- **Entregable:** CA policy creada y validada con What If (screenshot de validación) + evidencia documentada de la ineficacia de `grantControls: mfa` + sección Domain 3 del Gap Assessment completada

---

**Preguntas de cierre para el facilitador:**
- Al ejecutar el What If con `grantControls: mfa`, ¿qué resultado obtuvieron? ¿Cómo explicarían a un equipo de seguridad que una política "activa" en Entra CA no está generando ningún enforcement real?
- En su arquitectura de CA, ¿dónde colocarían el control de PIM just-in-time para permisos de agente? ¿Sería a nivel de Entra role o de OAuth scope?

**Conexión al siguiente pilar:** Controlar el acceso del agente limita el alcance potencial de un ataque, pero no protege los datos que el agente puede leer dentro de ese alcance. El Pilar 04 cubre la capa de datos: clasificación, etiquetado, DLP para interacciones de IA y el orden correcto de remediación antes de habilitar retrieval.

→ [Módulo 04 — Protect Data](./Module-04-ProtectData.md)
