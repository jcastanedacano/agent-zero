// rbac-001 lab: Microsoft.Authorization/roleAssignments/write self-escalation.
// Deploys, into THIS resource group (scope it to a throwaway RG; see README):
//   - uamiVulnerable + aciVulnerable: Role Based Access Control Administrator, no condition, attached to an Azure
//     Container Instance running the az CLI — exec into it and the identity can assign itself Owner.
//   - uamiHardened + aciHardened:     the same built-in role, with an Azure ABAC condition that blocks assigning
//     Owner, User Access Administrator or Role Based Access Control Administrator itself. The condition is
//     Microsoft's own documented pattern for constraining role-assignment delegation (see README for the source).
// The container groups exist only so the guided steps have somewhere to run `az login --identity` as each
// identity: nothing here performs the escalation itself. That stays a human-run step (see the path's lab.flow).
targetScope = 'resourceGroup'

@description('Suffix appended to every resource name, so repeat deployments in the same resource group do not collide.')
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

// Same role, with a condition (Azure ABAC, v2.0) that denies the write when the role being assigned is any one of
// blockedRoleDefinitionIds. ForAnyOfAllValues (not ForAnyOfAnyValues) is required: the single role being requested
// must be NotEquals every value in the blocked set for the write to be allowed, so it is blocked if it matches any
// one of them. The identity can still delegate any role outside that set; it cannot reach Owner through this path.
resource assignHardened 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, uamiHardened.id, rbacAdminRoleId, 'hardened')
  properties: {
    roleDefinitionId: rbacAdminRoleResourceId
    principalId: uamiHardened.properties.principalId
    principalType: 'ServicePrincipal'
    condition: '((!(ActionMatches{\'Microsoft.Authorization/roleAssignments/write\'})) OR (@Request[Microsoft.Authorization/roleAssignments:RoleDefinitionId] ForAnyOfAllValues:GuidNotEquals {${join(blockedRoleDefinitionIds, ', ')}}))'
    conditionVersion: '2.0'
  }
}

// One container per identity so the guided steps have a host to `az container exec` into and sign in as that
// identity: a Cloud Shell session cannot attach a user-assigned identity, and ACI's identity integration provides
// the token endpoint `az login --identity` needs. Both idle (sleep infinity) until exec'd into.
resource aciVulnerable 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: 'lab-rbac001-vulnerable-cli-${nameSuffix}'
  location: resourceGroup().location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${uamiVulnerable.id}': {} }
  }
  properties: {
    osType: 'Linux'
    restartPolicy: 'Never'
    containers: [
      {
        name: 'cli'
        properties: {
          image: 'mcr.microsoft.com/azure-cli:latest'
          command: ['/bin/sh', '-c', 'trap exit TERM; sleep infinity & wait']
          resources: { requests: { cpu: 1, memoryInGB: json('1.5') } }
        }
      }
    ]
  }
  tags: { lab: 'rbac-001', variant: 'vulnerable' }
}

resource aciHardened 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: 'lab-rbac001-hardened-cli-${nameSuffix}'
  location: resourceGroup().location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${uamiHardened.id}': {} }
  }
  properties: {
    osType: 'Linux'
    restartPolicy: 'Never'
    containers: [
      {
        name: 'cli'
        properties: {
          image: 'mcr.microsoft.com/azure-cli:latest'
          command: ['/bin/sh', '-c', 'trap exit TERM; sleep infinity & wait']
          resources: { requests: { cpu: 1, memoryInGB: json('1.5') } }
        }
      }
    ]
  }
  tags: { lab: 'rbac-001', variant: 'hardened' }
}

output vulnerablePrincipalId string = uamiVulnerable.properties.principalId
output vulnerableClientId string = uamiVulnerable.properties.clientId
output vulnerableContainerGroup string = aciVulnerable.name
output hardenedPrincipalId string = uamiHardened.properties.principalId
output hardenedClientId string = uamiHardened.properties.clientId
output hardenedContainerGroup string = aciHardened.name
output resourceGroupName string = resourceGroup().name
output resourceGroupScope string = resourceGroup().id
