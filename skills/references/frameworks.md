# Framework Mappings Reference

Mappings of the skills in this repository against standard security frameworks.
Each skill includes the relevant identifiers in its YAML frontmatter.

---

## MITRE ATLAS (2026.09)

An adversarial tactics and techniques framework specific to AI/ML systems. Names checked against the official ATLAS data release 2026.09; this table is generated from each skill's `atlas_techniques` field.

| Technique | Name | Skills that cover it |
|---------|---------|---------|
| AML.T0010 | AI Supply Chain Compromise | discover-third-party-ai-risk |
| AML.T0010.005 | AI Supply Chain Compromise: AI Agent Tool | discover-third-party-ai-risk |
| AML.T0012 | Valid Accounts | detect-agent-identity-abuse, detect-anomalous-agent-behavior, discover-shadow-ai-entra-principals, govern-ca-policy-workload-identity, govern-entra-agent-id, govern-foundry-rbac, govern-lifecycle-decommission-agent, govern-pim-agent-roles, secure-ca-policy-agents, secure-least-privilege-agent-identity |
| AML.T0016 | Obtain Capabilities | discover-third-party-ai-risk |
| AML.T0025 | Exfiltration via Cyber Means | protect-insider-risk-management-agents, secure-network-isolation-agent |
| AML.T0036 | Data from Information Repositories | discover-purview-dspm-ai, protect-information-barriers-agents |
| AML.T0040 | AI Model Inference API Access | discover-enumerate-foundry-agents, govern-foundry-rbac, secure-managed-identity-foundry, secure-network-isolation-agent |
| AML.T0051 | LLM Prompt Injection | detect-alert-prompt-injection-sentinel, detect-respond-playbook-agent-containment, detect-security-copilot-triage |
| AML.T0054 | LLM Jailbreak | detect-alert-prompt-injection-sentinel, detect-security-copilot-triage, detect-sentinel-mcp-server |
| AML.T0055 | Unsecured Credentials | secure-managed-identity-foundry, secure-secret-management-keyvault |
| AML.T0057 | LLM Data Leakage | detect-data-exfiltration-agent, discover-classify-agent-connectors, discover-purview-dspm-ai, govern-dlp-policy-copilot-prompts, protect-data-loss-prevention-agent-outputs, protect-information-barriers-agents, protect-insider-risk-management-agents, protect-purview-ai-hub-monitoring, protect-sensitivity-labels-ai-outputs |
| AML.T0083 | Credentials from AI Agent Configuration | secure-secret-management-keyvault |
| AML.T0084 | Discover AI Agent Configuration | discover-enumerate-foundry-agents, govern-foundry-rbac |
| AML.T0086 | Exfiltration via AI Agent Tool Invocation | detect-anomalous-agent-behavior, detect-data-exfiltration-agent, detect-respond-playbook-agent-containment, discover-classify-agent-connectors, govern-dlp-policy-copilot-prompts, protect-data-loss-prevention-agent-outputs, protect-purview-ai-hub-monitoring, protect-sensitivity-labels-ai-outputs |
| AML.T0091.000 | Use Alternate Authentication Material: Application Access Token | detect-agent-identity-abuse, detect-respond-playbook-agent-containment, govern-ca-policy-workload-identity |
| AML.T0103 | Deploy AI Agent | detect-agent-identity-abuse, discover-inventory-agents-copilot-studio, discover-shadow-ai-entra-principals, govern-agent365-approval-flow, govern-entra-agent-id |
| AML.T0109 | AI Supply Chain Rug Pull | discover-third-party-ai-risk |

Reference: [atlas.mitre.org](https://atlas.mitre.org)

---

## MITRE D3FEND v1.6

Defensive countermeasures mapped against attack techniques. Ids and names checked against the D3FEND ontology 1.6.0 (released 2026-08-31); this table is generated from each skill's `d3fend_techniques` field. A skill with an empty list has no D3FEND technique that describes what it does.

| Technique | Name | Skills that cover it |
|---------|---------|---------|
| D3-ACH | Application Configuration Hardening | discover-third-party-ai-risk |
| D3-AI | Asset Inventory | discover-inventory-agents-copilot-studio, discover-shadow-ai-entra-principals, govern-entra-agent-id |
| D3-AL | Account Locking | detect-respond-playbook-agent-containment |
| D3-AM | Access Modeling | discover-classify-agent-connectors, discover-enumerate-foundry-agents, discover-inventory-agents-copilot-studio, discover-purview-dspm-ai, govern-lifecycle-decommission-agent, secure-least-privilege-agent-identity |
| D3-AMED | Access Mediation | govern-ca-policy-workload-identity, protect-information-barriers-agents, secure-ca-policy-agents |
| D3-ANCI | Authentication Cache Invalidation | detect-respond-playbook-agent-containment |
| D3-ANET | Authentication Event Thresholding | detect-agent-identity-abuse, detect-anomalous-agent-behavior |
| D3-APA | Access Policy Administration | govern-agent365-approval-flow, govern-foundry-rbac, govern-pim-agent-roles |
| D3-CF | Content Filtering | detect-alert-prompt-injection-sentinel, govern-dlp-policy-copilot-prompts, protect-data-loss-prevention-agent-outputs |
| D3-CH | Credential Hardening | secure-managed-identity-foundry, secure-secret-management-keyvault |
| D3-CRO | Credential Rotation | secure-secret-management-keyvault |
| D3-DI | Data Inventory | discover-classify-agent-connectors, discover-purview-dspm-ai, protect-purview-ai-hub-monitoring, protect-sensitivity-labels-ai-outputs |
| D3-FAPA | File Access Pattern Analysis | detect-data-exfiltration-agent |
| D3-FCR | File Content Rules | govern-dlp-policy-copilot-prompts, protect-data-loss-prevention-agent-outputs |
| D3-FE | File Encryption | protect-sensitivity-labels-ai-outputs |
| D3-MA | Message Analysis | detect-alert-prompt-injection-sentinel |
| D3-NAM | Network Access Mediation | govern-ca-policy-workload-identity |
| D3-NI | Network Isolation | secure-network-isolation-agent |
| D3-NTF | Network Traffic Filtering | secure-network-isolation-agent |
| D3-OTF | Outbound Traffic Filtering | detect-data-exfiltration-agent, secure-network-isolation-agent |
| D3-RAPA | Resource Access Pattern Analysis | detect-anomalous-agent-behavior |
| D3-SWI | Software Inventory | discover-third-party-ai-risk |
| D3-UAP | User Account Permissions | detect-agent-identity-abuse, discover-enumerate-foundry-agents, discover-shadow-ai-entra-principals, govern-agent365-approval-flow, govern-entra-agent-id, govern-foundry-rbac, govern-lifecycle-decommission-agent, govern-pim-agent-roles, secure-ca-policy-agents, secure-least-privilege-agent-identity, secure-managed-identity-foundry |
| D3-UBA | User Behavior Analysis | detect-anomalous-agent-behavior, protect-insider-risk-management-agents |
| D3-UDTA | User Data Transfer Analysis | detect-data-exfiltration-agent, protect-insider-risk-management-agents, protect-purview-ai-hub-monitoring |
| D3-UGLPA | User Geolocation Logon Pattern Analysis | detect-agent-identity-abuse |
| D3-UGPH | User Group Permissions | protect-information-barriers-agents |

Reference: [d3fend.mitre.org](https://d3fend.mitre.org)

---

## NIST AI Risk Management Framework (AI RMF)

A risk management framework specific to AI systems. Subcategory ids and statements checked against the AI RMF 1.0 Playbook; this table is generated from each skill's `nist_ai_rmf` field and shows the first sentence of each subcategory.

| Subcategory | What it says | Skills that cover it |
|---------|---------|---------|
| GOVERN-1.1 | Legal and regulatory requirements involving AI are understood, managed, and documented. | discover-purview-dspm-ai |
| GOVERN-1.4 | The risk management process and its outcomes are established through transparent policies, procedures, and other controls based on organizational risk priorities. | govern-agent365-approval-flow |
| GOVERN-1.6 | Mechanisms are in place to inventory AI systems and are resourced according to organizational risk priorities. | discover-enumerate-foundry-agents, discover-inventory-agents-copilot-studio, discover-shadow-ai-entra-principals, govern-entra-agent-id |
| GOVERN-1.7 | Processes and procedures are in place for decommissioning and phasing out of AI systems safely and in a manner that does not increase risks or decrease the organization’s trustworthiness. | govern-lifecycle-decommission-agent |
| GOVERN-2.1 | Roles and responsibilities and lines of communication related to mapping, measuring, and managing AI risks are documented and are clear to individuals and teams throughout the organization. | discover-shadow-ai-entra-principals, govern-agent365-approval-flow, govern-entra-agent-id, govern-foundry-rbac, govern-pim-agent-roles, secure-ca-policy-agents, secure-least-privilege-agent-identity |
| GOVERN-6.1 | Policies and procedures are in place that address AI risks associated with third-party entities, including risks of infringement of a third party’s intellectual property or other rights. | discover-third-party-ai-risk |
| MAP-1.1 | Intended purpose, potentially beneficial uses, context-specific laws, norms and expectations, and prospective settings in which the AI system will be deployed are understood and documented. | discover-inventory-agents-copilot-studio, discover-purview-dspm-ai |
| MAP-4.1 | Approaches for mapping AI technology and legal risks of its components – including the use of third-party data or software – are in place, followed, and documented, as are risks of infringement of a third-party’s intellectual property or other rights. | discover-third-party-ai-risk |
| MAP-4.2 | Internal risk controls for components of the AI system including third-party AI technologies are identified and documented. | discover-classify-agent-connectors, govern-foundry-rbac |
| MAP-5.1 | Likelihood and magnitude of each identified impact (both potentially beneficial and harmful) based on expected use, past uses of AI systems in similar contexts, public incident reports, feedback from those external to the team that developed or deployed the AI system, or other data are identified and documented. | discover-classify-agent-connectors |
| MEASURE-2.4 | The functionality and behavior of the AI system and its components – as identified in the MAP function – are monitored when in production. | detect-agent-identity-abuse, detect-anomalous-agent-behavior, detect-sentinel-mcp-server, protect-insider-risk-management-agents, protect-purview-ai-hub-monitoring |
| MEASURE-2.7 | AI system security and resilience – as identified in the MAP function – are evaluated and documented. | detect-alert-prompt-injection-sentinel, detect-data-exfiltration-agent, discover-enumerate-foundry-agents, govern-ca-policy-workload-identity, secure-managed-identity-foundry, secure-network-isolation-agent, secure-secret-management-keyvault |
| MEASURE-2.10 | Privacy risk of the AI system – as identified in the MAP function – is examined and documented. | discover-purview-dspm-ai, govern-dlp-policy-copilot-prompts, protect-data-loss-prevention-agent-outputs, protect-information-barriers-agents, protect-insider-risk-management-agents, protect-purview-ai-hub-monitoring, protect-sensitivity-labels-ai-outputs |
| MEASURE-3.1 | Approaches, personnel, and documentation are in place to regularly identify and track existing, unanticipated, and emergent AI risks based on factors such as intended and actual performance in deployed contexts. | detect-anomalous-agent-behavior |
| MANAGE-1.3 | Responses to the AI risks deemed high priority as identified by the Map function, are developed, planned, and documented. | govern-ca-policy-workload-identity, govern-dlp-policy-copilot-prompts, govern-foundry-rbac, govern-pim-agent-roles, protect-data-loss-prevention-agent-outputs, protect-information-barriers-agents, protect-sensitivity-labels-ai-outputs, secure-least-privilege-agent-identity, secure-managed-identity-foundry, secure-network-isolation-agent, secure-secret-management-keyvault |
| MANAGE-2.4 | Mechanisms are in place and applied, responsibilities are assigned and understood to supersede, disengage, or deactivate AI systems that demonstrate performance or outcomes inconsistent with intended use. | detect-respond-playbook-agent-containment, secure-ca-policy-agents |
| MANAGE-4.1 | Post-deployment AI system monitoring plans are implemented, including mechanisms for capturing and evaluating input from users and other relevant AI actors, appeal and override, decommissioning, incident response, recovery, and change management. | detect-agent-identity-abuse, detect-alert-prompt-injection-sentinel, detect-data-exfiltration-agent, detect-respond-playbook-agent-containment, detect-security-copilot-triage, detect-sentinel-mcp-server, govern-lifecycle-decommission-agent |
| MANAGE-4.3 | Incidents and errors are communicated to relevant AI actors including affected communities. | detect-respond-playbook-agent-containment, detect-security-copilot-triage |

Reference: [nist.gov/artificial-intelligence/ai-risk-management-framework](https://www.nist.gov/artificial-intelligence/ai-risk-management-framework)

---

## NIST Cybersecurity Framework 2.0 (CSF)

Subcategory ids and outcomes checked against CSF 2.0 (106 subcategories); this table is generated from each skill's `nist_csf` field. CSF 1.1 ids such as `PR.AC-04`, `PR.DS-05` or `ID.SC-2` do not exist in 2.0: access control moved to `PR.AA`, supply chain to `GV.SC`.

| Subcategory | Outcome | Skills that cover it |
|---------|---------|---------|
| DE.AE-02 | Potentially adverse events are analyzed to better understand associated activities | detect-agent-identity-abuse, detect-anomalous-agent-behavior, detect-security-copilot-triage |
| DE.AE-03 | Information is correlated from multiple sources | detect-data-exfiltration-agent |
| DE.CM-01 | Networks and network services are monitored to find potentially adverse events | secure-network-isolation-agent |
| DE.CM-03 | Personnel activity and technology usage are monitored to find potentially adverse events | detect-agent-identity-abuse, detect-anomalous-agent-behavior, protect-insider-risk-management-agents |
| DE.CM-09 | Computing hardware and software, runtime environments, and their data are monitored to find potentially adverse events | detect-alert-prompt-injection-sentinel, detect-data-exfiltration-agent, detect-sentinel-mcp-server, protect-purview-ai-hub-monitoring |
| GV.PO-01 | Policy for managing cybersecurity risks is established based on organizational context, cybersecurity strategy, and priorities and is communicated and enforced | govern-agent365-approval-flow |
| GV.SC-04 | Suppliers are known and prioritized by criticality | discover-third-party-ai-risk |
| GV.SC-06 | Planning and due diligence are performed to reduce risks before entering into formal supplier or other third-party relationships | discover-third-party-ai-risk |
| GV.SC-07 | The risks posed by a supplier, their products and services, and other third parties are understood, recorded, prioritized, assessed, responded to, and monitored over the course of the relationship | discover-third-party-ai-risk |
| ID.AM-02 | Inventories of software, services, and systems managed by the organization are maintained | discover-enumerate-foundry-agents, discover-inventory-agents-copilot-studio, discover-shadow-ai-entra-principals, govern-entra-agent-id |
| ID.AM-05 | Assets are prioritized based on classification, criticality, resources, and impact on the mission | discover-classify-agent-connectors, discover-inventory-agents-copilot-studio, discover-purview-dspm-ai |
| ID.AM-08 | Systems, hardware, software, services, and data are managed throughout their life cycles | govern-lifecycle-decommission-agent |
| ID.RA-01 | Vulnerabilities in assets are identified, validated, and recorded | discover-classify-agent-connectors, discover-enumerate-foundry-agents, discover-purview-dspm-ai, protect-purview-ai-hub-monitoring |
| PR.AA-01 | Identities and credentials for authorized users, services, and hardware are managed by the organization | discover-shadow-ai-entra-principals, govern-entra-agent-id, govern-foundry-rbac, govern-lifecycle-decommission-agent, secure-managed-identity-foundry, secure-secret-management-keyvault |
| PR.AA-03 | Users, services, and hardware are authenticated | govern-ca-policy-workload-identity, secure-ca-policy-agents, secure-managed-identity-foundry |
| PR.AA-05 | Access permissions, entitlements, and authorizations are defined in a policy, managed, enforced, and reviewed, and incorporate the principles of least privilege and separation of duties | govern-agent365-approval-flow, govern-ca-policy-workload-identity, govern-entra-agent-id, govern-foundry-rbac, govern-pim-agent-roles, protect-information-barriers-agents, secure-ca-policy-agents, secure-least-privilege-agent-identity |
| PR.DS-01 | The confidentiality, integrity, and availability of data-at-rest are protected | govern-dlp-policy-copilot-prompts, protect-sensitivity-labels-ai-outputs, secure-secret-management-keyvault |
| PR.DS-02 | The confidentiality, integrity, and availability of data-in-transit are protected | protect-data-loss-prevention-agent-outputs, protect-sensitivity-labels-ai-outputs |
| PR.DS-10 | The confidentiality, integrity, and availability of data-in-use are protected | govern-dlp-policy-copilot-prompts, protect-data-loss-prevention-agent-outputs, protect-information-barriers-agents, protect-insider-risk-management-agents |
| PR.IR-01 | Networks and environments are protected from unauthorized logical access and usage | secure-network-isolation-agent |
| RS.AN-03 | Analysis is performed to establish what has taken place during an incident and the root cause of the incident | detect-agent-identity-abuse, detect-alert-prompt-injection-sentinel, detect-data-exfiltration-agent, detect-security-copilot-triage, detect-sentinel-mcp-server |
| RS.CO-02 | Internal and external stakeholders are notified of incidents | detect-respond-playbook-agent-containment, detect-sentinel-mcp-server |
| RS.MA-01 | The incident response plan is executed in coordination with relevant third parties once an incident is declared | detect-respond-playbook-agent-containment |
| RS.MI-01 | Incidents are contained | detect-respond-playbook-agent-containment |

Reference: [nist.gov/cyberframework](https://www.nist.gov/cyberframework)

---

## Framework coverage by pillar

| Pillar | Skills | ATLAS | D3FEND | NIST AI RMF | NIST CSF |
|---------|---------|---------|---------|---------|---------|
| 01 Discover | 6 | 11 techniques | 6 techniques | GOVERN-1.x, GOVERN-2.x, GOVERN-6.x, MAP-1.x, MAP-4.x, MAP-5.x, MEASURE-2.x | GV.SC, ID.AM, ID.RA, PR.AA |
| 02 Govern | 7 | 7 techniques | 8 techniques | GOVERN-1.x, GOVERN-2.x, MAP-4.x, MEASURE-2.x, MANAGE-1.x, MANAGE-4.x | GV.PO, ID.AM, PR.AA, PR.DS |
| 03 Secure | 5 | 5 techniques | 8 techniques | GOVERN-2.x, MEASURE-2.x, MANAGE-1.x, MANAGE-2.x | DE.CM, PR.AA, PR.DS, PR.IR |
| 04 Protect | 5 | 4 techniques | 8 techniques | MEASURE-2.x, MANAGE-1.x | DE.CM, ID.RA, PR.AA, PR.DS |
| 05 Detect | 7 | 7 techniques | 12 techniques | MEASURE-2.x, MEASURE-3.x, MANAGE-2.x, MANAGE-4.x | DE.AE, DE.CM, RS.AN, RS.CO, RS.MA, RS.MI |
