<#
.SYNOPSIS
  Bring up the TodoApp stack on a local kind-based Kubernetes cluster.

.DESCRIPTION
  End-to-end local cluster bootstrap:
    1. Creates a kind cluster named "todoapp" (if one doesn't exist)
       from k8s/kind-cluster.yaml, which maps host :5000 and :8080 to
       the NodePort services.
    2. Builds the backend + frontend Docker images locally.
    3. Loads those images into the kind cluster's node (no registry).
    4. Creates or updates the backend JWT secret with a freshly generated one
       (pass -JwtSecret to override).
    5. Applies all manifests via ``kubectl apply -k k8s``.
    6. Waits for all Deployments to become Available, then prints the
       URLs the app is reachable on.

.PARAMETER JwtSecret
  Optional. JWT signing secret for the backend. When omitted, a
  cryptographically random 64-char hex value is generated.

.PARAMETER SkipBuild
  Skip ``docker build``. Useful when the images are already current
  in the local Docker daemon.

.EXAMPLE
  pwsh ./scripts/k8s-up.ps1
  pwsh ./scripts/k8s-up.ps1 -SkipBuild
#>
[CmdletBinding()]
param(
  [string]$JwtSecret,
  [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

$repoRoot  = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$clusterName = "todoapp"
$namespace   = "todoapp"

function Require-Tool {
  param([string]$Name)
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if (-not $cmd) { throw "Required tool '$Name' not found on PATH." }
}

Require-Tool docker
Require-Tool kind
Require-Tool kubectl

function Get-KindClusters {
  # ``kind get clusters`` writes "No kind clusters found." to stderr when
  # the list is empty. With $ErrorActionPreference=Stop PowerShell 5.1
  # converts that to a terminating NativeCommandError even on exit code
  # 0, so we run the call with EAP=Continue and parse stdout only.
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

# --- 1. Cluster ---------------------------------------------------------------
$existing = Get-KindClusters
if ($existing -contains $clusterName) {
  Write-Host "[k8s-up] kind cluster '$clusterName' already exists -- reusing"
} else {
  Write-Host "[k8s-up] Creating kind cluster '$clusterName'"
  kind create cluster --name $clusterName --config (Join-Path $repoRoot "k8s/kind-cluster.yaml") | Out-Host
}

kubectl config use-context "kind-$clusterName" | Out-Host

# --- 2. Images ----------------------------------------------------------------
if (-not $SkipBuild) {
  Write-Host "[k8s-up] Building backend image (todoapp-backend:local)"
  docker build -t todoapp-backend:local (Join-Path $repoRoot "backend") | Out-Host

  Write-Host "[k8s-up] Building frontend image (todoapp-frontend:local)"
  # Build arg matches the NodePort the kind cluster publishes on the host.
  docker build `
    --build-arg VITE_API_BASE_URL=http://localhost:5000 `
    -t todoapp-frontend:local `
    (Join-Path $repoRoot "frontend") | Out-Host
}

Write-Host "[k8s-up] Loading images into kind"
kind load docker-image --name $clusterName todoapp-backend:local  | Out-Host
kind load docker-image --name $clusterName todoapp-frontend:local | Out-Host

# --- 3. Real JWT secret -------------------------------------------------------
if (-not $JwtSecret) {
  $JwtSecret = python -c "import secrets; print(secrets.token_hex(32))"
  if (-not $JwtSecret) {
    # Fallback if python is unavailable.
    $JwtSecret = ([Guid]::NewGuid().ToString("N") + [Guid]::NewGuid().ToString("N"))
  }
}
Write-Host "[k8s-up] Ensuring namespace exists"
kubectl apply -f (Join-Path $repoRoot "k8s/namespace.yaml") | Out-Host

Write-Host "[k8s-up] Creating backend-secrets with a fresh JWT signing key"
# ``create --dry-run=client -o yaml | apply -f -`` is the canonical
# idempotent "upsert" pattern for Kubernetes secrets.
kubectl create secret generic backend-secrets `
  --namespace $namespace `
  --from-literal=JWT_SECRET_KEY=$JwtSecret `
  --dry-run=client -o yaml `
  | kubectl apply -f - | Out-Host

# --- 4. Manifests -------------------------------------------------------------
Write-Host "[k8s-up] Applying manifests"
kubectl apply -k (Join-Path $repoRoot "k8s") | Out-Host

# Bounce the backend pods so they pick up the new secret immediately.
kubectl rollout restart deployment/backend --namespace $namespace | Out-Host

# --- 5. Wait for availability -------------------------------------------------
Write-Host "[k8s-up] Waiting for deployments to become Available"
kubectl wait --namespace $namespace --for=condition=Available --timeout=180s deployment/mongo    | Out-Host
kubectl wait --namespace $namespace --for=condition=Available --timeout=180s deployment/backend  | Out-Host
kubectl wait --namespace $namespace --for=condition=Available --timeout=180s deployment/frontend | Out-Host

Write-Host ""
Write-Host "[k8s-up] Stack is up. Try:" -ForegroundColor Green
Write-Host "  Frontend:     http://localhost:8080"
Write-Host "  Backend API:  http://localhost:5000"
Write-Host "  Swagger UI:   http://localhost:5000/docs"
Write-Host ""
Write-Host "Teardown with: pwsh ./scripts/k8s-down.ps1"
