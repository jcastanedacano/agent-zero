# Module 01 — Discover & Prioritize | Track B

**Module duration:** 90 minutes

**Learning objective:**
By the end of this module, participants will be able to design an agent inventory architecture covering cloud sources and endpoints, configure Defender AI Agent Inventory and Purview DSPM for AI in a demo tenant, identify structural inventory blind spots, and produce a visibility gap assessment for their organization.

**Module agenda:**

| Time | Activity | Type |
|------|----------|------|
| 20 min | Discovery architecture: sources, tables, connectors, and blind spots by agent type | Presentation |
| 15 min | Walk-through of `AgentsInfo`: schema, key fields, documented limitations | Presentation |
| 45 min | Lab: Activate Defender AI Agent Inventory + inventory KQL | Lab |
| 10 min | Gap assessment: design the organization's visibility map | Discussion |

---

**Core content (points the facilitator must cover):**

1. **Discovery topology by agent type:** Copilot Studio and Azure AI Foundry generate telemetry in `AgentsInfo`. Power Automate with AI steps appears in `CloudAppEvents`. Local agents (Claude Code, MCP servers, LLM scripts) generate no cloud signal without an active endpoint connector — this is the structural blind spot that no Purview or Defender control resolves on its own.

   **Closing the local agent blind spot with Intune and Microsoft Defender for Endpoint:** For organizations with managed devices, two controls extend discovery to endpoint-hosted agents. (a) **Microsoft Defender for Endpoint** (MDE) discovers unsanctioned local agents running on managed devices and can apply security baselines that restrict common agent execution paths — if an MDE policy is active, a local LLM script running outside approved paths generates an alert. (b) **Intune** device compliance policies can require that local AI agents run inside **Windows Execution Containers** — Windows-based isolation environments where the agent is assigned a distinct Entra Agent ID and is subject to the same Conditional Access policies as cloud agents. Without Execution Containers, a local agent inherits the device user's identity and is invisible to CA. This is the only mechanism that brings local agents into the same governance perimeter as tenant-registered agents. Reference: [Zero Trust security for AI agents](https://techcommunity.microsoft.com/blog/microsoftmechanicsblog/zero-trust-security-for-ai-agents/4533091) (Microsoft Mechanics, 2026).

2. **Shadow AI as the default state:** Agent Builder (M365 Copilot) allows any licensed user to create and publish agents without approval. These agents appear in Agent 365 Registry but without an Entra Agent ID, no technical owner, and no DLP review. They are not exceptions — they are the baseline case in any M365 E5 tenant with Copilot enabled.

3. **Applicable Microsoft controls:** Purview DSPM for AI maps agent interactions with sensitive data — it complements but does not replace identity inventory. Defender AI Agent Inventory requires active connectors per platform. SharePoint Advanced Management audits which sites are accessed by agents. Agent 365 is the central registry, but only covers registered agents.

   > **DSPM version note (GA May 2026):** Microsoft Purview shipped a new, unified version of Data Security Posture Management that supersedes the classic "DSPM for AI" this module has referenced. The new version covers both AI apps/agents and traditional data stores in one experience, extends to third-party SaaS and IaaS (Google Cloud Platform, Snowflake, Databricks), and integrates partner risk data (Varonis, Cyera, BigID, OneTrust). The classic DSPM for AI experience still exists and still works for tenants that haven't migrated, but new features land only in the unified version going forward. When configuring the lab, confirm which version the demo tenant is on before following portal navigation steps — menu paths differ between classic and unified. Reference: [Learn about Data Security Posture Management](https://learn.microsoft.com/purview/data-security-posture-management-learn-about), Microsoft Learn.

4. **The cost of an incomplete inventory:** An agent not listed in the inventory does not appear in Conditional Access policies, has no technical owner for escalation, and is not subject to Sentinel analytics rules. The inventory gap is the gap across every subsequent security layer.

5. **PHANTOM-B: la lente de threat modeling para cada agente que el inventario encuentra:** Un inventario responde que agentes existen. La pregunta inmediatamente siguiente es que puede salir mal con cada uno, y ahi la mayoria de los equipos se queda sin metodo. PHANTOM-B (Adam Shostack, 2026) es el analogo de STRIDE para LLMs, escrito por el mismo autor: un mnemonico de ocho amenazas pensado para quien **consume** un LLM, no para quien lo entrena, que es exactamente la posicion de una organizacion que despliega Copilot o agentes en Azure AI Foundry.

   | Letra | Amenaza | Pregunta que dispara sobre cada agente del inventario |
   |-------|---------|------------------------------------------------------|
   | **P** | Prompt injection | Que entradas no confiables llegan a este agente, directas o via corpus y respuestas de herramientas? |
   | **H** | Hallucination | Que pasa aguas abajo si la respuesta es plausible y falsa? |
   | **A** | Anthropomorphization | Estamos asumiendo intencion, culpa o cumplimiento donde solo hay prediccion de tokens? |
   | **N** | Non-explainability | Cuando tenemos que justificar la salida, ante quien, y con que evidencia? |
   | **T** | Training issues | Que sabemos del origen del modelo, sus datos y su fine-tuning? |
   | **O** | Over-reliance | Que decisiones toma este agente sin revision, y cual es el radio de impacto? |
   | **M** | Missing security engineering | Hicimos la ingenieria de seguridad de siempre, o el LLM la desplazo? |
   | **B** | Biases | Que sesgos hereda, y en este caso de uso son aceptables o son un problema legal? |

   Tres razones para usarlo en este modulo y no mas adelante: (a) es barato de aprender y de aplicar, a diferencia de MAESTRO o ATLAS, lo que lo hace el unico framework de esta serie que un equipo puede adoptar en una reunion; (b) Shostack lo diseno como **prompts, no como taxonomia**: no se trata de clasificar cada amenaza en su casilla sino de verificar que se considero al menos una de cada tipo, que es justo lo que hace falta cuando se recorre un inventario recien construido; (c) no incluye controles ni mitigaciones, por decision explicita del autor, lo que lo vuelve complementario y no competidor de los Modulos 02 a 07 de este track, que son precisamente los controles.

   **La incomodidad que vale discutir con el grupo:** Shostack sostiene que llamar "agentic" a la IA es en si mismo un caso de antropomorfizacion, una de sus ocho amenazas. Es una critica directa al vocabulario de este workshop y conviene ponerla sobre la mesa en lugar de esquivarla. El argumento operativo detras: si se asume que el sistema tiene intencion, se asume tambien que entiende una instruccion de "no hagas X" y que la respetara. De ahi salen dos errores concretos que este track corrige mas adelante: aprobar lo que el agente *dice* que va a hacer en lugar del comando real (Modulo 02, punto 5) y creer que un "detente" en el system prompt es un kill switch (Modulo 02, punto 10).

   Referencia: Adam Shostack, "PHANTOM-B: A STRIDE Analog for LLMs", Shostack + Associates White Paper #6, julio 2026, CC-BY.

---

**Exercise / Lab:**

- **Name:** Agent inventory architecture design
- **Format:** Pairs
- **Description:**
  1. Open Microsoft Defender XDR → AI Agent Inventory; verify which connectors are active and which tables return data
  2. In Sentinel → Logs, run the full `AgentsInfo` inventory query from the KQL Library (P01-Agent-Discovery.kql) and document the count by platform and lifecycle status
  3. Identify which categories of agents in the organization's environment will NOT appear in this inventory (local agents, third-party without connector, etc.) — document as blind spots
  4. Design a telemetry flow diagram: which agent → which connector → which table → which query detects it → which control applies
  5. **Pasada PHANTOM-B sobre el inventario:** elegir los 3 agentes de mayor exposicion del paso 2 y, para cada uno, recorrer las ocho letras respondiendo con una frase por amenaza. No buscar exhaustividad: el objetivo es detectar en cual de las ocho el equipo no tiene ninguna respuesta, porque ese es el gap real. Registrar el resultado como una matriz de 3 agentes por 8 amenazas
  6. Complete the "Domain 1 — Discover" section of the Gap Assessment Template
- **Required tools:** Microsoft Defender XDR (AI Agent Inventory), Microsoft Sentinel (Logs), KQL Library (repository), PHANTOM-B (tabla del punto 5 de este modulo), Gap Assessment Template
- **Deliverable:** Telemetry flow diagram + matriz PHANTOM-B de 3 agentes x 8 amenazas + Domain 1 section of the Gap Assessment completed with real agent count, identified blind spots, and control recommendations

---

**Closing questions for the facilitator:**
- In your diagram, how many agent types fell outside the cloud inventory? What endpoint architecture (MDE onboarding, local sensor) would close those blind spots?
- If you had to present the agent inventory to a risk committee next week, what result from the query you ran would generate the most questions from the committee, and how would you answer?

**Connection to the next domain:** Inventory is the input to the governance process. Without knowing which agents exist, it is not possible to assign owners or create policies. Domain 2 takes the agent list from inventory and answers: who is responsible for each one, what process approves them, and how is their lifecycle managed?

→ [Module 02 — Govern & Control](./Module-02-Govern.md)
