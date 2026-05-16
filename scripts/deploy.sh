#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Applying CRDs"
kubectl apply -f "${ROOT}/operator/crds/"

echo "==> Deploying namespaces"
kubectl apply -f "${ROOT}/deploy/k8s/00-namespaces.yaml"

echo "==> Deploying operator and observability"
kubectl apply -f "${ROOT}/deploy/k8s/operator.yaml"
kubectl apply -f "${ROOT}/deploy/observability/prometheus.yaml"
kubectl apply -f "${ROOT}/deploy/observability/grafana.yaml"
kubectl apply -f "${ROOT}/deploy/observability/otel-collector.yaml"

echo "==> Applying Bloodstream configs and paths"
kubectl apply -f "${ROOT}/deploy/k8s/configs-corridor.yaml"
kubectl apply -f "${ROOT}/deploy/k8s/configs-satellite.yaml"
kubectl apply -f "${ROOT}/deploy/k8s/paths.yaml"

echo "==> Deploying Argo circulation workflows"
kubectl apply -f "${ROOT}/deploy/argo/rbac.yaml"
kubectl apply -f "${ROOT}/deploy/argo/corridor-circulation.yaml"
kubectl apply -f "${ROOT}/deploy/argo/satellite-circulation.yaml"
kubectl apply -f "${ROOT}/deploy/argo/reconcile-dormant.yaml"

echo "==> Importing Grafana dashboard"
kubectl create configmap grafana-dashboard-bloodstream \
  --from-file=bloodstream-topology.json="${ROOT}/deploy/observability/dashboards/bloodstream-topology.json" \
  -n bloodstream --dry-run=client -o yaml | kubectl apply -f -
kubectl rollout restart deployment/grafana -n bloodstream 2>/dev/null || true

echo "==> Waiting for operator"
kubectl wait --for=condition=available deployment/bloodstream-operator -n bloodstream --timeout=120s || true

echo ""
echo "Bloodstream deployed."
echo "  Grafana:    kubectl port-forward -n bloodstream svc/grafana 3000:3000"
echo "  Prometheus: kubectl port-forward -n bloodstream svc/prometheus 9090:9090"
echo "  Configs:    kubectl get bloodstreamconfigs -n bloodstream"
echo "  Argo UI:    kubectl port-forward -n argo svc/argo-server 2746:2746"
