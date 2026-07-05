# Run on local Kubernetes (kind)

This repo ships a full set of Kubernetes manifests and a
bring-up/teardown script that deploys TodoApp (frontend + backend +
MongoDB) onto a **local [kind](https://kind.sigs.k8s.io/) cluster**.
Everything is designed to work on a clean machine with just Docker +
kubectl + kind installed — no registry, no Ingress controller, no
cloud credentials.

## Contents

| Path | Purpose |
| ---- | ------- |
| [`k8s/kind-cluster.yaml`](../k8s/kind-cluster.yaml) | kind cluster definition with host port mappings for NodePort 30050/30080. |
| [`k8s/namespace.yaml`](../k8s/namespace.yaml) | `todoapp` namespace. |
| [`k8s/mongo.yaml`](../k8s/mongo.yaml) | MongoDB Deployment + PVC + ClusterIP Service. |
| [`k8s/backend.yaml`](../k8s/backend.yaml) | Flask API: ConfigMap, Secret template, Deployment (2 replicas, non-root, probes, resource limits), NodePort Service (30050). |
| [`k8s/frontend.yaml`](../k8s/frontend.yaml) | Vite + nginx: Deployment (2 replicas, probes, resource limits), NodePort Service (30080). |
| [`k8s/kustomization.yaml`](../k8s/kustomization.yaml) | Aggregates everything for `kubectl apply -k k8s`. |
| [`scripts/k8s-up.ps1`](../scripts/k8s-up.ps1) | End-to-end bring-up: create cluster → build → load → apply → wait. |
| [`scripts/k8s-down.ps1`](../scripts/k8s-down.ps1) | Teardown (optional image prune). |

## Prerequisites

| Tool | Tested version | Install |
| ---- | -------------- | ------- |
| Docker Desktop | 29.x | https://www.docker.com/products/docker-desktop/ |
| kubectl | v1.34+ | https://kubernetes.io/docs/tasks/tools/ |
| kind | v0.31+ | `winget install Kubernetes.kind` · `brew install kind` · [releases](https://github.com/kubernetes-sigs/kind/releases) |
| PowerShell 7 (for scripts) | 7.4+ | `winget install Microsoft.PowerShell` |

Docker Desktop must be running (the kind node runs as a Docker
container).

## Quick start (one command)

```powershell
pwsh ./scripts/k8s-up.ps1
```

The script will:

1. Create a `kind` cluster named `todoapp` from
   [`k8s/kind-cluster.yaml`](../k8s/kind-cluster.yaml) (skipped if it
   already exists).
2. Build `todoapp-backend:local` and `todoapp-frontend:local` via
   `docker build` (use `-SkipBuild` to reuse existing images).
3. `kind load docker-image` both images into the cluster node so no
   registry is needed.
4. `kubectl apply -k k8s` to create every resource.
5. Generate a random `JWT_SECRET_KEY` and upsert the `backend-secrets`
   Secret with it, then `kubectl rollout restart deployment/backend`
   so the new value is picked up.
6. Wait for all Deployments to become `Available` and print the URLs.

Override the JWT secret:

```powershell
pwsh ./scripts/k8s-up.ps1 -JwtSecret "my-own-hex-here"
```

## Accessing the app

The kind cluster publishes these NodePorts on the host:

| Service | URL | Backed by |
| ------- | --- | --------- |
| Frontend SPA | http://localhost:8080 | `Service/frontend` (NodePort 30080) |
| Backend API | http://localhost:5000 | `Service/backend`  (NodePort 30050) |
| Swagger UI | http://localhost:5000/docs | same backend Service |

Smoke-test via `curl`:

```shell
curl -o /dev/null -s -w "%{http_code}\n" http://localhost:8080/
curl -o /dev/null -s -w "%{http_code}\n" http://localhost:5000/docs
```

Full round-trip (register → login → create project) is identical to
the Compose verification documented in the root
[README](../README.md#run-with-docker).

## Inspecting the cluster

```shell
kubectl --context kind-todoapp -n todoapp get all
kubectl --context kind-todoapp -n todoapp describe deployment backend
kubectl --context kind-todoapp -n todoapp logs -l app.kubernetes.io/name=backend --tail=100
```

(Seed the default tag list inside a backend pod:)

```shell
kubectl --context kind-todoapp -n todoapp \
  exec -it deploy/backend -- python seed.py
```

## Manifest design notes

- **Labels**: every object carries `app.kubernetes.io/name`,
  `app.kubernetes.io/component`, and `app.kubernetes.io/part-of`.
  `managed-by` is added by Kustomize to metadata only
  (`includeSelectors: false`), so pod selectors stay minimal and
  future relabeling doesn't trigger immutability errors.
- **Resource requests/limits**: set on every container so the
  scheduler can make good placement decisions and the cluster never
  gets OOM-killed by a single runaway pod.
- **Probes**: backend and frontend use HTTP readiness + liveness
  probes. Mongo uses a `tcpSocket` liveness probe and a `mongosh`
  exec readiness probe (ping must return ok).
- **Rollout strategy**: RollingUpdate for stateless services
  (`maxSurge: 1, maxUnavailable: 0` so there's never a moment with
  zero replicas). Mongo uses `Recreate` because the PVC is RWO.
- **Security**: backend runs as a non-root user (UID 1001) that is
  baked into the image, drops all capabilities, and disables privilege
  escalation. Frontend drops all caps and re-adds only
  `NET_BIND_SERVICE` (nginx binds to port 80 in its entrypoint).
- **State**: Mongo uses a 1 Gi PVC mounted at `/data/db`. Data
  survives pod restarts. `kubectl delete pvc -n todoapp mongo-data`
  wipes it explicitly.
- **Config vs. secrets**: non-secret env (Mongo URI, DB name, port)
  lives in `backend-config` ConfigMap; the JWT signing key lives in
  `backend-secrets` Secret. The committed Secret has an intentionally
  invalid placeholder value so `kubectl apply -k` succeeds on a fresh
  cluster without ever running the backend on a public signing key; the
  bring-up script immediately upserts a real random value and restarts
  the backend pods.

## Teardown

```powershell
pwsh ./scripts/k8s-down.ps1               # delete the cluster
pwsh ./scripts/k8s-down.ps1 -PruneImages  # also delete the two :local images
```

Deleting the cluster removes every resource and the PVC's backing
storage. Docker images remain in the host daemon so the next bring-up
is fast.

## Troubleshooting

- **Pods stuck in `ImagePullBackOff`** — kind didn't load the image
  yet. Re-run `pwsh ./scripts/k8s-up.ps1` or manually
  `kind load docker-image --name todoapp todoapp-backend:local`.
- **`Error: could not find tag for image todoapp-backend:local`** —
  run the script without `-SkipBuild` so the images are built first.
- **`connect: connection refused` on localhost:5000 / :8080** — the
  kind cluster config wasn't used. Verify with
  `kind get clusters` (expect `todoapp`) and
  `docker port todoapp-control-plane` (expect `30050/tcp` and
  `30080/tcp` mapped to `0.0.0.0:5000`/`0.0.0.0:8080`).
- **Backend crash-loops with 500s after bring-up** — the bring-up
  script restarts the backend after rotating the secret; wait for
  `kubectl rollout status deploy/backend -n todoapp` to finish.

## Moving to a real cluster

The same manifests deploy to any Kubernetes cluster with these swaps:

- Replace the `todoapp-backend:local` / `todoapp-frontend:local` image
  references with tags from a real registry.
- Switch the `frontend` and `backend` Services from `NodePort` to
  `ClusterIP` and put an Ingress (or LoadBalancer Service) in front.
- Promote Mongo to a StatefulSet or use a managed offering; the
  backend only needs `MONGO_URI` updated in the ConfigMap.
- Manage the JWT secret with your cluster's secret manager
  (External Secrets, SOPS, Vault) instead of the bring-up script's
  `kubectl create secret`.
