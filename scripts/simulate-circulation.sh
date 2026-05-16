#!/usr/bin/env bash
# Local simulation of uneven circulation without Kubernetes
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OPERATOR_URL="${OPERATOR_URL:-http://localhost:9091}"
EVOLUTION_URL="${EVOLUTION_URL:-http://localhost:3004}"

corridor_configs=(chrome-latest default-feature-flags staging-env)
satellite_configs=(safari firefox android-low-end slow-network feature-flag-alt-checkout degraded-payment-provider old-ui-version)

echo "==> Simulating high-density corridor traffic"
for _ in $(seq 1 20); do
  for cfg in "${corridor_configs[@]}"; do
    curl -sf -X POST "${OPERATOR_URL}/execution" \
      -H 'Content-Type: application/json' \
      -d "{\"config\":\"${cfg}\",\"trafficClass\":\"corridor\",\"passed\":true,\"driftGap\":0}" >/dev/null
  done
done

echo "==> Advancing system evolution (topology change pressure)"
curl -sf -X POST "${EVOLUTION_URL}/evolve" -H 'Content-Type: application/json' -d '{"steps": 3}'

echo "==> Simulating dormant satellites (no circulation)"
sleep 2

echo "==> Occasional satellite failure (stale selectors + drift)"
for cfg in "${satellite_configs[@]}"; do
  curl -sf -X POST "${OPERATOR_URL}/execution" \
    -H 'Content-Type: application/json' \
    -d "{\"config\":\"${cfg}\",\"trafficClass\":\"satellite\",\"passed\":false,\"driftGap\":3}" >/dev/null || true
done

echo "==> Reconciliation circulation for one dormant config"
curl -sf -X POST "${OPERATOR_URL}/execution" \
  -H 'Content-Type: application/json' \
  -d '{"config":"safari","trafficClass":"satellite","passed":true,"driftGap":0}'

echo "Done. Check metrics at http://localhost:8080/metrics"
