#!/usr/bin/env bash
# Local simulation of uneven circulation without Kubernetes
set -euo pipefail
OPERATOR_URL="${OPERATOR_URL:-http://localhost:9091}"

corridor_configs=(chrome-latest default-feature-flags staging-env)
satellite_configs=(safari firefox android-low-end slow-network feature-flag-alt-checkout degraded-payment-provider old-ui-version)

echo "==> Simulating high-density corridor traffic"
for _ in $(seq 1 20); do
  for cfg in "${corridor_configs[@]}"; do
    curl -sf -X POST "${OPERATOR_URL}/execution" \
      -H 'Content-Type: application/json' \
      -d "{\"config\":\"${cfg}\",\"trafficClass\":\"corridor\",\"passed\":true}" >/dev/null
  done
done

echo "==> Simulating dormant satellites (no circulation)"
sleep 2

echo "==> Occasional satellite failure"
for cfg in "${satellite_configs[@]}"; do
  curl -sf -X POST "${OPERATOR_URL}/execution" \
    -H 'Content-Type: application/json' \
    -d "{\"config\":\"${cfg}\",\"trafficClass\":\"satellite\",\"passed\":false}" >/dev/null || true
done

echo "==> Reconciliation circulation for one dormant config"
curl -sf -X POST "${OPERATOR_URL}/execution" \
  -H 'Content-Type: application/json' \
  -d '{"config":"safari","trafficClass":"satellite","passed":true}'

echo "Done. Check metrics at http://localhost:8080/metrics"
