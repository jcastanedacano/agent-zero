# Framework Mappings Reference

Mappings of the skills in this repository against standard security frameworks.
Each skill includes the relevant identifiers in its YAML frontmatter.

---

## MITRE ATLAS v5.4

An adversarial tactics and techniques framework specific to AI/ML systems.

| Technique | Name | Skills that cover it |
|---------|--------|---------------------|
| AML.T0012 | Valid Accounts | govern-entra-agent-id, secure-ca-policy-agents, govern-foundry-rbac |
| AML.T0025 | Exfiltration via ML Inference API | protect-insider-risk-management-agents, detect-data-exfiltration-agent |
| AML.T0037 | Data from Information Repositories | discover-purview-dspm-ai, protect-sensitivity-labels-ai-outputs |
| AML.T0040 | ML Supply Chain Compromise | discover-shadow-ai-entra-principals, govern-entra-agent-id, govern-foundry-rbac |
| AML.T0051 | LLM Prompt Injection | detect-alert-prompt-injection-sentinel, detect-security-copilot-triage |
| AML.T0054 | LLM Jailbreak | detect-alert-prompt-injection-sentinel, detect-sentinel-mcp-server, detect-security-copilot-triage |
| AML.T0056 | Discover AI Model Ontology | discover-shadow-ai-entra-principals, discover-purview-dspm-ai, govern-foundry-rbac |
| AML.T0057 | Exfiltration via Cyber Means | protect-insider-risk-management-agents, detect-data-exfiltration-agent |

Reference: [atlas.mitre.org](https://atlas.mitre.org)

---

## MITRE D3FEND v1.3

Defensive countermeasures mapped against attack techniques.

| Technique | Name | Skills that cover it |
|---------|--------|---------------------|
| D3-DAM | Data Access Monitoring | discover-purview-dspm-ai, protect-insider-risk-management-agents |
| D3-MAN | Message Authentication | govern-entra-agent-id, secure-ca-policy-agents, govern-foundry-rbac |
| D3-NTA | Network Traffic Analysis | detect-sentinel-mcp-server, detect-security-copilot-triage |
| D3-PA | Platform Allowlisting | detect-alert-prompt-injection-sentinel |
| D3-SBV | Service Binary Verification | detect-alert-prompt-injection-sentinel, detect-security-copilot-triage, detect-sentinel-mcp-server |
| D3-SFA | Service Failure Analysis | discover-shadow-ai-entra-principals, discover-purview-dspm-ai, govern-entra-agent-id |
| D3-UAP | User Account Permissions | secure-ca-policy-agents, govern-foundry-rbac |
| D3-UBA | User Behavior Analysis | protect-insider-risk-management-agents |

Reference: [d3fend.mitre.org](https://d3fend.mitre.org)

---

## NIST AI Risk Management Framework (AI RMF)

A risk management framework specific to AI systems.

| Function | Category | Skills that cover it |
|---------|-----------|---------------------|
| GOVERN-1.1 | AI policies established | discover-purview-dspm-ai |
| GOVERN-2.1 | Roles and responsibilities defined | govern-entra-agent-id, secure-ca-policy-agents, govern-foundry-rbac |
| GOVERN-4.1 | Continuous risk monitoring | detect-sentinel-mcp-server |
| GOVERN-4.2 | Access controls for AI systems | govern-foundry-rbac |
| MAP-1.1 | AI risk organizational context | discover-purview-dspm-ai, govern-entra-agent-id |
| MAP-1.5 | AI system dependencies and impacts | govern-entra-agent-id, govern-foundry-rbac |
| MAP-2.1 | Stakeholder impacts mapped | discover-purview-dspm-ai |
| MANAGE-2.4 | AI incident response | secure-ca-policy-agents |
| MANAGE-3.2 | Post-deployment monitoring | protect-insider-risk-management-agents, detect-sentinel-mcp-server, detect-security-copilot-triage |
| MANAGE-4.1 | Continuous improvement of controls | detect-sentinel-mcp-server, detect-security-copilot-triage |
| MEASURE-2.6 | AI security metrics | protect-insider-risk-management-agents |

Reference: [nist.gov/artificial-intelligence/ai-risk-management-framework](https://www.nist.gov/artificial-intelligence/ai-risk-management-framework)

---

## NIST Cybersecurity Framework 2.0 (CSF)

| Function | Category | Skills that cover it |
|---------|-----------|---------------------|
| GV (Govern) | GV.OC | Organizational context |
| ID (Identify) | ID.AM-02 | Software/asset inventory | discover-shadow-ai-entra-principals, govern-entra-agent-id |
| ID (Identify) | ID.AM-05 | Resources prioritized by risk | discover-purview-dspm-ai |
| ID (Identify) | ID.RA-01 | Vulnerability identification | discover-purview-dspm-ai |
| PR (Protect) | PR.AA-01 | Managed identities | govern-entra-agent-id |
| PR (Protect) | PR.AA-04 | Phishing-resistant authentication | govern-foundry-rbac |
| PR.AA-05 | Access control | secure-ca-policy-agents, govern-foundry-rbac |
| PR.AC-04 | Permissions and authorizations | secure-ca-policy-agents, govern-foundry-rbac |
| PR.AC-06 | Authenticated identities | govern-foundry-rbac |
| PR.DS-05 | Data-in-use protection | protect-insider-risk-management-agents |
| DE (Detect) | DE.AE-02 | Anomalous event analysis | detect-security-copilot-triage |
| DE.CM-01 | Continuous monitoring | detect-sentinel-mcp-server |
| DE.CM-03 | Personnel monitoring | protect-insider-risk-management-agents |
| RS (Respond) | RS.AN-01 | Incident analysis | detect-security-copilot-triage |
| RS.AN-03 | Forensic analysis | detect-sentinel-mcp-server, detect-security-copilot-triage |
| RS.CO-02 | Response coordination | detect-sentinel-mcp-server |

Reference: [nist.gov/cyberframework](https://www.nist.gov/cyberframework)

---

## Framework coverage by pillar

| Pillar | Skills | ATLAS | D3FEND | NIST AI RMF | NIST CSF |
|-------|--------|-------|--------|-------------|----------|
| 01 Discover | 5 | 3 techniques | 3 techniques | MAP-1.x, GOVERN-1.1 | ID.AM, ID.RA |
| 02 Govern | 7 | 3 techniques | 2 techniques | GOVERN-2.x, GOVERN-4.x | PR.AA, PR.AC |
| 03 Secure | 5 | 2 techniques | 2 techniques | GOVERN-2.1, MANAGE-2.4 | PR.AA, PR.AC |
| 04 Protect | 5 | 2 techniques | 2 techniques | MEASURE-2.6, MANAGE-3.2 | PR.DS, DE.CM |
| 05 Detect | 7 | 3 techniques | 3 techniques | MANAGE-3.2, MANAGE-4.1 | DE.AE, DE.CM, RS.AN |
