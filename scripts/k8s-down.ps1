<#
.SYNOPSIS
  Tear down the local TodoApp kind cluster.

.DESCRIPTION
  Deletes the kind cluster created by ``scripts/k8s-up.ps1``, which
  also removes every resource and the cluster's attached volumes.
  Docker images built during bring-up stay in the host's local Docker
  cache so the next ``k8s-up`` run is fast -- pass -PruneImages to
  delete those too.

.PARAMETER PruneImages
  Also remove the locally built ``todoapp-backend:local`` and
  ``todoapp-frontend:local`` images from the host Docker daemon.

.EXAMPLE
  pwsh ./scripts/k8s-down.ps1
  pwsh ./scripts/k8s-down.ps1 -PruneImages
#>
[CmdletBinding()]
param(
  [switch]$PruneImages
)

$ErrorActionPreference = "Stop"

$clusterName = "todoapp"

function Require-Tool {
  param([string]$Name)
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if (-not $cmd) { throw "Required tool '$Name' not found on PATH." }
}

Require-Tool kind

function Get-KindClusters {
  # ``kind get clusters`` prints "No kind clusters found." to stderr when
  # the list is empty. EAP=Stop converts that into a terminating error
  # on PowerShell 5.1, so we run the call with EAP=Continue.
  $prev = $ErrorActionPreference
  $ErrorActionPreference = 'Continue'
  try {
    $stdout = & kind get clusters 2>$null
    if (-not $stdout) { return @() }
    return @($stdout | Where-Object { $_ -and $_.Trim() })
  } finally {
    $ErrorActionPreference = $prev
  }
}

$existing = Get-KindClusters
if ($existing -contains $clusterName) {
  Write-Host "[k8s-down] Deleting kind cluster '$clusterName'"
  kind delete cluster --name $clusterName | Out-Host
} else {
  Write-Host "[k8s-down] kind cluster '$clusterName' not found -- nothing to delete"
}

if ($PruneImages) {
  Write-Host "[k8s-down] Removing locally built images"
  docker image rm --force todoapp-backend:local todoapp-frontend:local 2>$null | Out-Host
}

Write-Host "[k8s-down] Done."
