# Pilar 04 — Protect Data | Track B

**Duración del módulo:** 90 minutos

**Objetivo de aprendizaje:**
Al finalizar este módulo, el participante será capaz de diseñar una arquitectura de protección de datos para agentes de IA que cubra clasificación, DLP en interacciones y auditoría de exfiltración, configurar una política DLP de Purview para interacciones de IA en un tenant demo, auditar el oversharing en sitios SharePoint usados como fuente de conocimiento, y documentar el orden correcto de remediación antes de habilitar retrieval.

**Agenda del módulo:**

| Tiempo | Actividad | Tipo |
|--------|-----------|------|
| 20 min | Arquitectura de protección de datos para agentes: capas, vectores y el efecto multiplicador del oversharing | Exposición |
| 15 min | Purview DLP para interacciones de IA: diferencias vs. DLP tradicional, cobertura y limitaciones | Exposición |
| 45 min | Lab: DLP policy para AI interactions + auditoría de sensitivity labels + KQL de exfiltración | Lab |
| 10 min | Gap assessment: protección de datos y roadmap de etiquetado | Discusión |

---

**Contenido core (puntos que el facilitador debe cubrir):**

1. **El efecto multiplicador del oversharing:** Un error de ACL en SharePoint que expone un sitio confidencial a todos los usuarios es un riesgo manejable para humanos — requiere que alguien busque activamente. Para un agente con retrieval habilitado, ese error se amplifica a todos los usuarios que interactúan con el agente: la exposición es pasiva y automática. El agente no discrimina entre contenido sensible y no sensible — indexa todo lo que puede leer.

2. **Prompt injection sobre corpus envenenado:** Un atacante con acceso para editar documentos en SharePoint puede insertar instrucciones maliciosas que el agente ejecuta como si vinieran de un usuario legítimo. El agente no valida la fuente de las instrucciones — solo las ejecuta. Este vector no genera alertas en los logs estándar de actividad de usuario.

3. **Controles Microsoft aplicables:** Purview DLP configurado sobre "AI interactions" cubre prompts y respuestas en Microsoft 365 Copilot y otros agentes — no solo documentos y correos. Los sensitivity labels aplicados a sitios SharePoint restringen el índice del agente. SharePoint Advanced Management audita y remedia oversharing a nivel de sitio y colección de sitios. Insider Risk Management detecta patrones de exfiltración por volumen y por tipo de dato.

4. **El orden de remediación como control arquitectónico:** Habilitar retrieval antes de aplicar etiquetas y remediar ACL crea una ventana de exposición activa que puede durar semanas. El orden correcto es: (1) clasificar y etiquetar todos los sitios candidatos, (2) auditar y remediar errores de ACL, (3) habilitar retrieval del agente. Invertir este orden es el error más frecuente en deployments de agentes que acceden a SharePoint.

---

**Ejercicio / Lab:**

- **Nombre:** Arquitectura de protección de datos para agentes en tenant demo
- **Modalidad:** Individual
- **Descripción:**
  1. En Microsoft Purview compliance portal → Data loss prevention → Policies, crear la política "Agentic AI — Sensitive Data in AI Interactions": workload = AI interactions, regla = Credit Card Number en prompt o respuesta, acción = Block + notify + audit
  2. En SharePoint admin center, usar SharePoint Advanced Management para auditar el oversharing en al menos 2 sitios del tenant demo; documentar cuáles tienen sensitivity label aplicada y cuáles no
  3. Ejecutar las queries del KQL Library (P04-Exfiltration-Detection.kql): exfiltración por conector, documentos sin etiqueta accedidos por agentes, prompt injection patterns
  4. Diseñar el orden de remediación para los sitios sin etiqueta identificados, justificando la secuencia antes de habilitar retrieval
  5. Completar la sección "Domain 4 — Protect Data" del Gap Assessment Template incluyendo el inventario de sitios y el plan de etiquetado
- **Herramientas requeridas:** Microsoft Purview compliance portal (DLP), SharePoint admin center (Advanced Management), Microsoft Sentinel (Logs), KQL Library P04, Gap Assessment Template
- **Entregable:** DLP policy activa documentada + inventario de sitios con estado de etiquetado + orden de remediación justificado + sección Domain 4 del Gap Assessment completada

---

**Preguntas de cierre para el facilitador:**
- Al auditar los sitios de SharePoint del tenant demo, ¿cuántos tenían retrieval de agentes habilitado sin sensitivity label aplicada? ¿Qué proceso organizacional habría prevenido esa condición?
- Si tuvieran que diseñar una política de DLP que cubra tanto las respuestas del agente como los documentos que el agente genera o modifica, ¿qué workloads incluirían y qué tipos de información sensible priorizarían?

**Conexión al siguiente pilar:** Proteger los datos reduce la superficie de ataque pero no elimina la posibilidad de incidentes. El Pilar 05 cierra la arquitectura de seguridad con la capa de detección y respuesta: cómo integrar los agentes como señal activa en el SOC, qué analytics rules son específicas para comportamiento agentic, y cómo automatizar la contención.

→ [Módulo 05 — Detect & Respond](./Module-05-DetectRespond.md)
