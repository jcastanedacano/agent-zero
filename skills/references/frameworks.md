# Framework Mappings Reference

Mapeos de las skills de este repositorio contra frameworks de seguridad estándar.
Cada skill incluye los identificadores relevantes en su YAML frontmatter.

---

## MITRE ATLAS v5.4

Framework de tácticas y técnicas adversariales específico para sistemas de IA/ML.

| Técnica | Nombre | Skills que la cubren |
|---------|--------|---------------------|
| AML.T0012 | Valid Accounts | govern-entra-agent-id, secure-ca-policy-agents, govern-foundry-rbac |
| AML.T0025 | Exfiltration via ML Inference API | protect-insider-risk-management-agents, detect-data-exfiltration-agent |
| AML.T0037 | Data from Information Repositories | discover-purview-dspm-ai, protect-sensitivity-labels-ai-outputs |
| AML.T0040 | ML Supply Chain Compromise | discover-shadow-ai-entra-principals, govern-entra-agent-id, govern-foundry-rbac |
| AML.T0051 | LLM Prompt Injection | detect-alert-prompt-injection-sentinel, detect-security-copilot-triage |
| AML.T0054 | LLM Jailbreak | detect-alert-prompt-injection-sentinel, detect-sentinel-mcp-server, detect-security-copilot-triage |
| AML.T0056 | Discover AI Model Ontology | discover-shadow-ai-entra-principals, discover-purview-dspm-ai, govern-foundry-rbac |
| AML.T0057 | Exfiltration via Cyber Means | protect-insider-risk-management-agents, detect-data-exfiltration-agent |

Referencia: [atlas.mitre.org](https://atlas.mitre.org)

---

## MITRE D3FEND v1.3

Contramedidas defensivas mapeadas contra técnicas de ataque.

| Técnica | Nombre | Skills que la cubren |
|---------|--------|---------------------|
| D3-DAM | Data Access Monitoring | discover-purview-dspm-ai, protect-insider-risk-management-agents |
| D3-MAN | Message Authentication | govern-entra-agent-id, secure-ca-policy-agents, govern-foundry-rbac |
| D3-NTA | Network Traffic Analysis | detect-sentinel-mcp-server, detect-security-copilot-triage |
| D3-PA | Platform Allowlisting | detect-alert-prompt-injection-sentinel |
| D3-SBV | Service Binary Verification | detect-alert-prompt-injection-sentinel, detect-security-copilot-triage, detect-sentinel-mcp-server |
| D3-SFA | Service Failure Analysis | discover-shadow-ai-entra-principals, discover-purview-dspm-ai, govern-entra-agent-id |
| D3-UAP | User Account Permissions | secure-ca-policy-agents, govern-foundry-rbac |
| D3-UBA | User Behavior Analysis | protect-insider-risk-management-agents |

Referencia: [d3fend.mitre.org](https://d3fend.mitre.org)

---

## NIST AI Risk Management Framework (AI RMF)

Marco de gestión de riesgos específico para sistemas de IA.

| Función | Categoría | Skills que la cubren |
|---------|-----------|---------------------|
| GOVERN-1.1 | Políticas de IA establecidas | discover-purview-dspm-ai |
| GOVERN-2.1 | Roles y responsabilidades definidos | govern-entra-agent-id, secure-ca-policy-agents, govern-foundry-rbac |
| GOVERN-4.1 | Monitoreo continuo de riesgos | detect-sentinel-mcp-server |
| GOVERN-4.2 | Controles de acceso para sistemas AI | govern-foundry-rbac |
| MAP-1.1 | Contexto organizacional de riesgo AI | discover-purview-dspm-ai, govern-entra-agent-id |
| MAP-1.5 | Dependencias e impactos de sistemas AI | govern-entra-agent-id, govern-foundry-rbac |
| MAP-2.1 | Impactos en stakeholders mapeados | discover-purview-dspm-ai |
| MANAGE-2.4 | Respuesta a incidentes de AI | secure-ca-policy-agents |
| MANAGE-3.2 | Monitoreo post-deployment | protect-insider-risk-management-agents, detect-sentinel-mcp-server, detect-security-copilot-triage |
| MANAGE-4.1 | Mejora continua de controles | detect-sentinel-mcp-server, detect-security-copilot-triage |
| MEASURE-2.6 | Métricas de seguridad de AI | protect-insider-risk-management-agents |

Referencia: [nist.gov/artificial-intelligence/ai-risk-management-framework](https://www.nist.gov/artificial-intelligence/ai-risk-management-framework)

---

## NIST Cybersecurity Framework 2.0 (CSF)

| Función | Categoría | Skills que la cubren |
|---------|-----------|---------------------|
| GV (Govern) | GV.OC | Contexto organizacional |
| ID (Identify) | ID.AM-02 | Inventario de software/activos | discover-shadow-ai-entra-principals, govern-entra-agent-id |
| ID (Identify) | ID.AM-05 | Recursos priorizados por riesgo | discover-purview-dspm-ai |
| ID (Identify) | ID.RA-01 | Identificación de vulnerabilidades | discover-purview-dspm-ai |
| PR (Protect) | PR.AA-01 | Identidades gestionadas | govern-entra-agent-id |
| PR (Protect) | PR.AA-04 | Autenticación resistente a phishing | govern-foundry-rbac |
| PR.AA-05 | Control de acceso | secure-ca-policy-agents, govern-foundry-rbac |
| PR.AC-04 | Permisos y autorizaciones | secure-ca-policy-agents, govern-foundry-rbac |
| PR.AC-06 | Identidades autenticadas | govern-foundry-rbac |
| PR.DS-05 | Protección de datos en uso | protect-insider-risk-management-agents |
| DE (Detect) | DE.AE-02 | Análisis de eventos anómalos | detect-security-copilot-triage |
| DE.CM-01 | Monitoreo continuo | detect-sentinel-mcp-server |
| DE.CM-03 | Monitoreo de personal | protect-insider-risk-management-agents |
| RS (Respond) | RS.AN-01 | Análisis de incidentes | detect-security-copilot-triage |
| RS.AN-03 | Análisis forense | detect-sentinel-mcp-server, detect-security-copilot-triage |
| RS.CO-02 | Coordinación de respuesta | detect-sentinel-mcp-server |

Referencia: [nist.gov/cyberframework](https://www.nist.gov/cyberframework)

---

## Cobertura del framework por pilar

| Pilar | Skills | ATLAS | D3FEND | NIST AI RMF | NIST CSF |
|-------|--------|-------|--------|-------------|----------|
| 01 Discover | 5 | 3 técnicas | 3 técnicas | MAP-1.x, GOVERN-1.1 | ID.AM, ID.RA |
| 02 Govern | 7 | 3 técnicas | 2 técnicas | GOVERN-2.x, GOVERN-4.x | PR.AA, PR.AC |
| 03 Secure | 5 | 2 técnicas | 2 técnicas | GOVERN-2.1, MANAGE-2.4 | PR.AA, PR.AC |
| 04 Protect | 5 | 2 técnicas | 2 técnicas | MEASURE-2.6, MANAGE-3.2 | PR.DS, DE.CM |
| 05 Detect | 7 | 3 técnicas | 3 técnicas | MANAGE-3.2, MANAGE-4.1 | DE.AE, DE.CM, RS.AN |
