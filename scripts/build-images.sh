#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLUSTER_NAME="${CLUSTER_NAME:-bloodstream}"

echo "==> Building images"
docker build -t bloodstream/operator:latest "${ROOT}/operator"
docker build -t bloodstream/circulation:latest "${ROOT}/circulation"

if command -v k3d &>/dev/null; then
  k3d image import \
    bloodstream/operator:latest \
    bloodstream/circulation:latest \
    -c "${CLUSTER_NAME}"
fi

echo "==> Images built and imported"
