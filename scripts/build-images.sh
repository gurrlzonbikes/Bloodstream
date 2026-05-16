#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLUSTER_NAME="${CLUSTER_NAME:-bloodstream}"

echo "==> Building images into k3d cluster ${CLUSTER_NAME}"
k3d image import bloodstream/demo-frontend:latest -c "${CLUSTER_NAME}" 2>/dev/null || true

docker build -t bloodstream/demo-frontend:latest -f "${ROOT}/demo-app/Dockerfile.frontend" "${ROOT}/demo-app"
docker build -t bloodstream/demo-service:latest -f "${ROOT}/demo-app/Dockerfile.service" "${ROOT}/demo-app"
docker build -t bloodstream/operator:latest "${ROOT}/operator"
docker build -t bloodstream/e2e:latest "${ROOT}/e2e"

if command -v k3d &>/dev/null; then
  k3d image import \
    bloodstream/demo-frontend:latest \
    bloodstream/demo-service:latest \
    bloodstream/operator:latest \
    bloodstream/e2e:latest \
    -c "${CLUSTER_NAME}"
fi

echo "==> Images built and imported"
