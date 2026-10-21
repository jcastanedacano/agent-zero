// rbac-001 lab: Microsoft.Authorization/roleAssignments/write self-escalation.
// Deploys two user-assigned managed identities into THIS resource group (scope it to a throwaway RG; see README):
//   - uamiVulnerable: Role Based Access Control Administrator, no condition — can assign itself Owner on this resource group.
//   - uamiHardened:   the same built-in role, with an Azure ABAC condition that blocks assigning Owner, User Access
//     Administrator or Role Based Access Control Administrator itself. The condition is Microsoft's own documented
//     pattern for constraining role-assignment delegation (see README for the source).
// Nothing here signs in as either identity or performs the escalation: that is the guided step in the path's lab
// block, run with the Azure CLI, after this template is deployed.
targetScope = 'resourceGroup'

@description('Suffix appended to both identity names, so repeat deployments in the same resource group do not collide.')
param nameSuffix string = uniqueString(resourceGroup().id, deployment().name)

@description('Built-in role IDs the hardened identity is blocked from assigning. Defaults to the three that can reach Owner-equivalent control of this scope.')
param blockedRoleDefinitionIds array = [
  '8e3af657-a8ff-443c-a75c-2fe8c4bcb635' // Owner
  '18d7d88d-d35e-4fb5-a5c3-7773c20a72d9' // User Access Administrator
  'f58310d9-a9f6-439a-9e8d-f62e7b41a168' // Role Based Access Control Administrator (the role being delegated)
]

var rbacAdminRoleId = 'f58310d9-a9f6-439a-9e8d-f62e7b41a168'
var rbacAdminRoleResourceId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', rbacAdminRoleId)

resource uamiVulnerable 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'lab-rbac001-vulnerable-${nameSuffix}'
  location: resourceGroup().location
  tags: { lab: 'rbac-001', variant: 'vulnerable' }
}

resource uamiHardened 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'lab-rbac001-hardened-${nameSuffix}'
  location: resourceGroup().location
  tags: { lab: 'rbac-001', variant: 'hardened' }
}

// No condition: this identity can create a roleAssignments/write for any role, including Owner, on this resource group.
resource assignVulnerable 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, uamiVulnerable.id, rbacAdminRoleId, 'vulnerable')
  properties: {
    roleDefinitionId: rbacAdminRoleResourceId
    principalId: uamiVulnerable.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Same role, with a condition (Azure ABAC, v2.0) that denies the write when the role being assigned is one of
// blockedRoleDefinitionIds. The identity can still delegate any other role; it cannot reach Owner through this path.
resource assignHardened 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, uamiHardened.id, rbacAdminRoleId, 'hardened')
  properties: {
    roleDefinitionId: rbacAdminRoleResourceId
    principalId: uamiHardened.properties.principalId
    principalType: 'ServicePrincipal'
    condition: '((!(ActionMatches{\'Microsoft.Authorization/roleAssignments/write\'})) OR (@Request[Microsoft.Authorization/roleAssignments:RoleDefinitionId] ForAnyOfAnyValues:GuidNotEquals {${join(blockedRoleDefinitionIds, ', ')}}))'
    conditionVersion: '2.0'
  }
}

output vulnerablePrincipalId string = uamiVulnerable.properties.principalId
output vulnerableClientId string = uamiVulnerable.properties.clientId
output hardenedPrincipalId string = uamiHardened.properties.principalId
output hardenedClientId string = uamiHardened.properties.clientId
output resourceGroupScope string = resourceGroup().id
