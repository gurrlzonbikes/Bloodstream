#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-bloodstream}"
K3D_PORT="${K3D_PORT:-8080}"

echo "==> Creating k3d cluster: ${CLUSTER_NAME}"
if ! k3d cluster list 2>/dev/null | grep -q "${CLUSTER_NAME}"; then
  k3d cluster create "${CLUSTER_NAME}" \
    --api-port 6550 \
    -p "${K3D_PORT}:80@loadbalancer" \
    --agents 1
fi

echo "==> Installing Argo Workflows"
kubectl create namespace argo 2>/dev/null || true
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.6.5/install.yaml
kubectl patch deployment workflow-controller -n argo --type=json \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/args","value":["--auth-mode=server","--secure=false"]}]' 2>/dev/null || true

echo "==> Cluster ready. Context:"
kubectl config current-context
