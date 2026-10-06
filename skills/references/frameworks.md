# Framework Mappings Reference

Mappings of the skills in this repository against standard security frameworks.
Each skill includes the relevant identifiers in its YAML frontmatter.

---

## MITRE ATLAS (2026.09)

An adversarial tactics and techniques framework specific to AI/ML systems. Names verified against the official ATLAS data release 2026.09; this table is generated from each skill's `atlas_techniques` frontmatter, so every skill in the library appears here.

| Technique | Name | Skills that cover it |
|---------|--------|---------------------|
| AML.T0010 | AI Supply Chain Compromise | discover-third-party-ai-risk |
| AML.T0010.005 | AI Supply Chain Compromise: AI Agent Tool | discover-third-party-ai-risk |
| AML.T0012 | Valid Accounts | govern-ca-policy-workload-identity, govern-entra-agent-id, govern-foundry-rbac, govern-pim-agent-roles, secure-ca-policy-agents, secure-least-privilege-agent-identity |
| AML.T0016 | Obtain Capabilities | discover-third-party-ai-risk |
| AML.T0025 | Exfiltration via Cyber Means | protect-insider-risk-management-agents, secure-network-isolation-agent |
| AML.T0036 | Data from Information Repositories | discover-purview-dspm-ai, protect-information-barriers-agents |
| AML.T0040 | AI Model Inference API Access | detect-agent-identity-abuse, detect-anomalous-agent-behavior, discover-enumerate-foundry-agents, discover-shadow-ai-entra-principals, govern-entra-agent-id, govern-foundry-rbac, govern-lifecycle-decommission-agent, govern-pim-agent-roles, secure-ca-policy-agents, secure-least-privilege-agent-identity, secure-managed-identity-foundry, secure-network-isolation-agent |
| AML.T0051 | LLM Prompt Injection | detect-alert-prompt-injection-sentinel, detect-respond-playbook-agent-containment, detect-security-copilot-triage, discover-inventory-agents-copilot-studio |
| AML.T0054 | LLM Jailbreak | detect-alert-prompt-injection-sentinel, detect-security-copilot-triage, detect-sentinel-mcp-server, discover-inventory-agents-copilot-studio, govern-agent365-approval-flow |
| AML.T0055 | Unsecured Credentials | secure-managed-identity-foundry, secure-secret-management-keyvault |
| AML.T0057 | LLM Data Leakage | detect-data-exfiltration-agent, discover-classify-agent-connectors, govern-dlp-policy-copilot-prompts, protect-data-loss-prevention-agent-outputs, protect-information-barriers-agents, protect-insider-risk-management-agents, protect-purview-ai-hub-monitoring, protect-sensitivity-labels-ai-outputs |
| AML.T0083 | Credentials from AI Agent Configuration | secure-secret-management-keyvault |
| AML.T0084 | Discover AI Agent Configuration | detect-agent-identity-abuse, detect-anomalous-agent-behavior, discover-enumerate-foundry-agents, discover-purview-dspm-ai, discover-shadow-ai-entra-principals, govern-foundry-rbac |
| AML.T0086 | Exfiltration via AI Agent Tool Invocation | detect-anomalous-agent-behavior, detect-data-exfiltration-agent, detect-respond-playbook-agent-containment, discover-classify-agent-connectors, govern-dlp-policy-copilot-prompts, protect-data-loss-prevention-agent-outputs, protect-purview-ai-hub-monitoring, protect-sensitivity-labels-ai-outputs |
| AML.T0091.000 | Use Alternate Authentication Material: Application Access Token | detect-agent-identity-abuse, detect-respond-playbook-agent-containment, govern-ca-policy-workload-identity |
| AML.T0103 | Deploy AI Agent | detect-agent-identity-abuse, discover-inventory-agents-copilot-studio, discover-shadow-ai-entra-principals, govern-agent365-approval-flow |
| AML.T0109 | AI Supply Chain Rug Pull | discover-third-party-ai-risk |

Reference: [atlas.mitre.org](https://atlas.mitre.org)

---

## MITRE D3FEND v1.3

Defensive countermeasures mapped against attack techniques.

| Technique | Name | Skills that cover it |
|---------|--------|---------------------|
| D3-ACH | Application Configuration Hardening | discover-third-party-ai-risk |
| D3-AI | Asset Inventory | govern-entra-agent-id, discover-shadow-ai-entra-principals |
| D3-DAM | Data Access Monitoring | discover-purview-dspm-ai, protect-insider-risk-management-agents |
| D3-MAN | Message Authentication | secure-ca-policy-agents, govern-foundry-rbac |
| D3-NTA | Network Traffic Analysis | detect-sentinel-mcp-server, detect-security-copilot-triage |
| D3-PA | Platform Allowlisting | detect-alert-prompt-injection-sentinel |
| D3-SBV | Service Binary Verification | detect-alert-prompt-injection-sentinel, detect-security-copilot-triage, detect-sentinel-mcp-server |
| D3-SFA | System File Analysis | discover-inventory-agents-copilot-studio, discover-purview-dspm-ai, govern-agent365-approval-flow |
| D3-SWI | Software Inventory | discover-third-party-ai-risk |
| D3-UAP | User Account Permissions | secure-ca-policy-agents, govern-foundry-rbac, govern-entra-agent-id, discover-shadow-ai-entra-principals |
| D3-UBA | User Behavior Analysis | protect-insider-risk-management-agents |

Reference: [d3fend.mitre.org](https://d3fend.mitre.org)

---

## NIST AI Risk Management Framework (AI RMF)

A risk management framework specific to AI systems.

| Function | Category | Skills that cover it |
|---------|-----------|---------------------|
| GOVERN-1.1 | AI policies established | discover-purview-dspm-ai |
| GOVERN-1.6 | Mechanisms to inventory AI systems | govern-entra-agent-id, discover-shadow-ai-entra-principals |
| GOVERN-2.1 | Roles and responsibilities defined | govern-entra-agent-id, secure-ca-policy-agents, govern-foundry-rbac, discover-shadow-ai-entra-principals |
| GOVERN-4.1 | Continuous risk monitoring | detect-sentinel-mcp-server |
| GOVERN-4.2 | Access controls for AI systems | govern-foundry-rbac |
| GOVERN-6.1 | Policies for AI risks from third-party entities | discover-third-party-ai-risk |
| MAP-1.1 | AI risk organizational context | discover-purview-dspm-ai |
| MAP-1.5 | AI system dependencies and impacts | govern-foundry-rbac |
| MAP-2.1 | Stakeholder impacts mapped | discover-purview-dspm-ai |
| MAP-4.1 | Risk mapping of third-party components | discover-third-party-ai-risk |
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
| GV (Govern) | GV.SC-04 | Suppliers identified and ranked | discover-third-party-ai-risk |
| GV (Govern) | GV.SC-06 | Due diligence before supplier relationships | discover-third-party-ai-risk |
| GV (Govern) | GV.SC-07 | Supplier risk monitored over the relationship | discover-third-party-ai-risk |
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
| 01 Discover | 6 | 10 techniques | 3 techniques | MAP-1.x, GOVERN-1.1 | ID.AM, ID.RA |
| 02 Govern | 7 | 7 techniques | 2 techniques | GOVERN-2.x, GOVERN-4.x | PR.AA, PR.AC |
| 03 Secure | 5 | 5 techniques | 2 techniques | GOVERN-2.1, MANAGE-2.4 | PR.AA, PR.AC |
| 04 Protect | 5 | 4 techniques | 2 techniques | MEASURE-2.6, MANAGE-3.2 | PR.DS, DE.CM |
| 05 Detect | 7 | 8 techniques | 3 techniques | MANAGE-3.2, MANAGE-4.1 | DE.AE, DE.CM, RS.AN |
