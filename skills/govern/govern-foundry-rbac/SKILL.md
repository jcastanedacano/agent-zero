---
name: govern-foundry-rbac
version: "1.0"
pillar: govern
subdomain: ms-foundry
description: >-
  Applies least privilege to Microsoft Foundry with the Foundry RBAC roles at
  the account, project and agent scope, audits the project connections that
  hold credentials, and limits which models can be deployed with Azure Policy.
tags: [govern, foundry, rbac, least-privilege, connections, azure-policy]
atlas_techniques: [AML.T0012, AML.T0040, AML.T0084]
d3fend_techniques: [D3-MAN, D3-UAP]
nist_ai_rmf: [GOVERN-2.1, GOVERN-4.2, MAP-1.5]
nist_csf: [PR.AA-04, PR.AC-04, PR.AC-06]
ms_license: [Microsoft Foundry, Azure subscription]
ms_roles: [Owner or Role Based Access Control Administrator (assign roles), Foundry Account Owner (deployments, shared connections), Foundry Project Manager (publish agents, assign Foundry User)]
effort_hours: 3
---

## When to use

- Configuring a Foundry project for a new agent
- Several agents share a project and need different permissions
- Auditing who can build agents, call them, deploy models and read connection credentials
- The periodic governance review of Pillar 02

## Prerequisites

- An Azure subscription with a Foundry resource (`Microsoft.CognitiveServices/accounts`, kind `AIServices`) and at least one project
- Owner or Role Based Access Control Administrator on the scope where you assign roles
- Azure CLI, or the Azure portal and the Foundry portal

## Scope of this skill

This skill covers projects that live under a Foundry resource. Hub-based projects (the older model built on Azure Machine Learning) use other roles: Azure AI Administrator
and Azure AI Developer apply to Azure Machine Learning workspaces and Foundry hubs only. Azure Machine Learning commands (`az ml connection`, `az ml online-deployment`) do not
reach Foundry resources.

## Foundry RBAC model

Three scopes: the **Foundry resource** (the administrative, security and monitoring boundary), the **project** (access control for Foundry APIs, tools and developer workflows)
and the **agent** (a single agent, evaluated today only for access to that agent's endpoint). Scope URIs:

```
/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}
/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}/projects/{project}
/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}/projects/{project}/agents/{agent}
```

| Role (ID) | Build in a project | Interact with agent endpoints | Publish agents | Manage models and accounts | Assign roles |
|---|---|---|---|---|---|
| Foundry Agent Consumer (`eed3b665-ab3a-47b6-8f48-c9382fb1dad6`) | no | yes | no | no | no |
| Foundry User (`53ca6127-db72-4b80-b1b0-d745d6d5456d`) | yes | yes | no | no | no |
| Foundry Project Manager (`eadc314b-1a2d-4efa-be10-5d325db5065e`) | yes | yes | yes | no | only Foundry User |
| Foundry Account Owner (`e47c6f54-e4a2-4754-9501-8e0985b135e1`) | no | no | no | yes | Foundry User, ACR and monitoring roles |
| Foundry Owner (`c883944f-8b7b-4483-af10-35834be79c4a`) | yes | yes | yes | yes | Foundry User, ACR and monitoring roles |

The Foundry roles were renamed from Azure AI User, Azure AI Owner, Azure AI Account Owner and Azure AI Project Manager; the IDs and permissions did not change. Use the ID in scripts.
Azure Owner and Contributor create projects and deploy models, but have no data actions: they cannot build agents or call agent endpoints. Reader only reads.

Four facts that shape every control below (all from Microsoft Learn):

1. RBAC applies when callers authenticate with Entra ID. If key authentication is on, the key gives full access without role restrictions. Turn it off first (`disableLocalAuth`; see the
   `secure-managed-identity-foundry` skill), or the roles in this skill do not bind anyone who holds a key.
2. Do not assign built-in roles that start with `Cognitive Services` in Foundry scenarios (the exception is Cognitive Services Usages Reader, assigned at subscription scope to see quota),
   and do not use `Azure AI Developer`, which is scoped to Azure Machine Learning workspaces and Foundry hubs.
3. Role assignments at agent scope only decide who can interact with that agent's endpoints. They grant no control plane permission and do not limit what the agent can use.
4. Unpublished agents of a project share the project's agent identity; a published agent gets its own identity and needs its own role assignments on the resources it reaches
   (Learn notes that the publishing experience is changing, so confirm which identity your agents use).

## Workflow

### Step 1 — Audit the role assignments that reach Foundry

Query 1 in `queries/` (Azure Resource Graph) gives the matrix of Foundry-relevant roles by scope level and principal type; Query 2 lists each assignment that needs a decision. From the CLI:

```bash
az role assignment list \
  --scope "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}" \
  --include-inherited \
  --query "[].{Principal:principalName, Type:principalType, Role:roleDefinitionName, Scope:scope}" \
  --output table
```

`--include-inherited` matters: an assignment at the resource group or the subscription applies to every Foundry resource under it. Look for:

- A Foundry role at resource group or subscription scope (it applies to every Foundry resource there) where one project was meant
- `Azure AI Developer`, any `Cognitive Services` role, and `Azure AI Inference Deployment Operator` (a role that creates deployments, not one that calls them)
- Foundry Account Owner or Foundry Owner held by people who do not manage the resource
- Service principals with Owner or Contributor: they manage the account and, while keys are on, can list them

### Step 2 — Assign by persona at the smallest scope

Learn's sample mapping:

| Persona | Role and scope | Why |
|---|---|---|
| IT administrator | Owner on the subscription | Meets enterprise standards, assigns the manager roles |
| Manager | Foundry Account Owner on the Foundry resource | Manages the resource, deploys models, audits connections, creates shared connections; cannot build, can assign Foundry User |
| Team lead | Foundry Project Manager on the Foundry resource | Creates projects and publishes agents, assigns Foundry User |
| Developer | Foundry User on the project, Reader on the Foundry resource | Builds agents in a project with pre-deployed models and connections |
| Agent consumer or service | Foundry Agent Consumer on the project, or on one agent | Calls agent endpoints, nothing else |

```bash
# Foundry Agent Consumer on one agent (the Azure portal only assigns it at account scope; use the CLI for project or agent scope)
az role assignment create \
  --assignee-object-id "{principalId}" \
  --assignee-principal-type ServicePrincipal \
  --role "eed3b665-ab3a-47b6-8f48-c9382fb1dad6" \
  --scope "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}/projects/{project}/agents/{agent}"

# Replace a broad assignment: remove it, then assign the right role at the right scope
az role assignment delete \
  --assignee "{principalId}" \
  --role "64702f94-c441-49e6-a78b-ef80e0188fee" \
  --scope "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}"

az role assignment create \
  --assignee-object-id "{principalId}" \
  --assignee-principal-type User \
  --role "53ca6127-db72-4b80-b1b0-d745d6d5456d" \
  --scope "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}/projects/{project}"
```

The project's managed identity needs Foundry User on the Foundry resource (added automatically when the project is created in the portal by someone who can assign roles).

### Step 3 — Audit the connections

A connection holds how a project reaches a resource: Azure AI Search, Storage, Cosmos DB, Application Insights, a container registry, an API with a key. Connections are listed per project and per
Foundry resource. They are not in Azure Resource Graph, so use the CLI or the ARM API (the list hides the credentials; the permission `Microsoft.CognitiveServices/accounts/connections/listsecrets/action` returns them).

```bash
# Per project
az cognitiveservices account project connection list \
  --name {account} --project-name {project} --resource-group {rg} --output json

# Shared at the Foundry resource
az cognitiveservices account connection list \
  --name {account} --resource-group {rg} --output json
```

Read `properties.authType`, `properties.category`, `properties.target`, `properties.isSharedToAll` and `properties.sharedUserList`. `ApiKey`, `AccessKey`, `AccountKey`, `SAS`, `PAT`, `UsernamePassword`, `ServicePrincipal` and `OAuth2`
store a secret; `AAD`, `ManagedIdentity` and `None` do not. For each connection with a secret ask whether Entra ID or a managed identity can replace it, and who owns it. Remove what no agent needs:

```bash
az cognitiveservices account project connection delete \
  --connection-name {connection} --name {account} --project-name {project} --resource-group {rg}
```

Adding a connection requires Foundry User, Foundry Owner or Azure Contributor (or higher), so every developer who can build in the project can also add one. Learn lists no way to scope a connection to a single
agent: connections belong to the project (or the Foundry resource), so the practical boundary between agents with different needs is a separate project.
Treat connections that leave Microsoft services as an exfiltration path and review them with the same priority as Graph permissions.

### Step 4 — Control which models can be deployed (Azure Policy)

Learn documents no per-agent authorization of a model deployment, and tags on a deployment do not authorize anything. What exists:

1. **Who can deploy**: `deployments/write` is held by Foundry Account Owner, Foundry Owner, Azure Owner and Contributor, and Cognitive Services Contributor; Foundry User and Foundry Project Manager can read deployments, not create them.
2. **Which models**: two built-in policies, evaluated when the deployment is created. "Foundry model deployments should only use approved models" takes `allowedPublishers` and `allowedAssetIds` (matched as a prefix:
   end the ID with `/` to match one model, add the version to match one version). "Foundry model deployments should meet eligibility requirements" takes `onlyAllowDirectFromAzure` and `denyPreviewModels`.
3. **Which deployment types**: a custom policy on `Microsoft.CognitiveServices/accounts/deployments/sku.name` (Learn's example blocks `GlobalStandard`).

```bash
az policy definition list \
  --query "[?displayName=='Foundry model deployments should only use approved models'].{name:name, id:id}" -o table

az policy assignment create \
  --name "foundry-approved-models" \
  --scope "/subscriptions/{sub}" \
  --policy "{policy-definition-id}" \
  --params '{"effect":{"value":"Deny"},"allowedPublishers":{"value":["OpenAI"]},"allowedAssetIds":{"value":["azureml://registries/azure-openai/models/gpt-4.1-mini/"]}}'
```

A Deny policy acts on new or updated deployments; one that already exists is reported as non-compliant, not removed. List them with `az cognitiveservices account deployment list --name {account} --resource-group {rg}` and compare. Per-deployment content filtering is the
`raiPolicyName` of each deployment; two preview built-in policies ("Cognitive Services Agents should only use allowed ...", Audit effect only) check the content filtering of agents. To give an agent less than the whole account,
use a separate Foundry resource or project, or an AI gateway (API Management) in front of its MCP tools (preview, MCP tools only).

### Step 5 — Block features people should not use

To stop a group from building agents (or using fine-tuning, evaluations and so on), create a custom role that excludes the data action in `notDataActions`, for example
`Microsoft.CognitiveServices/accounts/AIServices/agents/*`, and assign it. A user keeps any permission that another role of theirs grants, so check all their assignments. Learn's own custom-role example
includes `Microsoft.CognitiveServices/accounts/listkeys/action`: leave it out once key access is off.

### Step 6 — Monitor

Query 3 (changes to Foundry accounts, projects, connections and deployments) and Query 4 (role assignments and removals under a Foundry scope) in `queries/` read the Activity Log. The key listing is Query 2 of the
`secure-managed-identity-foundry` skill.

## Verification

- [ ] Query 1 and Query 2 reviewed: no `Cognitive Services` role, `Azure AI Developer` or `Azure AI Inference Deployment Operator` assigned on Foundry scopes without a documented reason
- [ ] No Foundry role at subscription or resource group scope unless every Foundry resource under it should be reachable
- [ ] Developers hold Foundry User on the project; services and consumers hold Foundry Agent Consumer on the project or the agent
- [ ] Every connection with a stored secret has an owner and a reason; the rest were replaced by Entra ID or managed identity, or deleted
- [ ] The approved-models policy is assigned with effect Deny, and the existing deployments were compared against it
- [ ] Key access is off on the Foundry resource (RBAC does not bind key holders)
- [ ] Queries 3 and 4 run in Sentinel
- [ ] Findings added to the "Domain 2" section of the Gap Assessment Template

## Implementation notes

- Azure Owner and Contributor are not Foundry data-plane roles, but with local authentication on they can list the keys and call the account without a token
- Foundry RBAC roles inherit from Azure RBAC: an assignment at the resource group or the subscription reaches every Foundry resource below it
- In the validation tenant, listing connections returned `credentials` null and the `target` field in full (for Application Insights it is the whole connection string with the instrumentation key): treat the list output as sensitive
- Learn is not consistent on whether Foundry Project Manager can create projects: the permissions matrix says no, the sample mapping and the hosted agent permissions page say yes. Test it in your tenant before relying on it
- A Learn page for classic hub-based projects still lists connection permissions for Owner, Contributor and Azure AI Developer on the hub: that is the old model
- Combine with `secure-managed-identity-foundry`: RBAC in Foundry plus Entra ID instead of keys
- Removed in this version, because it describes a different product or does not exist: the hub role table (`Azure AI Foundry Owner`, `Azure AI Foundry Contributor`), scopes under `Microsoft.MachineLearningServices/workspaces`, `az ml connection` and
  `az ml online-deployment update --set tags.authorized_agents`, the assignment of `Azure AI Inference Deployment Operator` as a least-privilege role for an agent identity (it creates deployments and has no data actions),
  `Azure AI Developer` and `Cognitive Services Contributor` as the skill's own roles, and a KQL on `MICROSOFT.MACHINELEARNINGSERVICES` that read an `agentId` property the Activity Log does not carry (the file it pointed to did not exist)
