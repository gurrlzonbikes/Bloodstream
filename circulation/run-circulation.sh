#!/usr/bin/env bash
# Run Automation Panda chapter-03 example tests for one Bloodstream execution config.
set -euo pipefail

cd /workshop/chapter-code/chapter-03

CONFIG="${BLOODSTREAM_CONFIG:-chrome-latest}"
TRAFFIC="${TRAFFIC_CLASS:-satellite}"

case "$CONFIG" in
  safari) PROJECT=webkit ;;
  firefox) PROJECT=firefox ;;
  *) PROJECT=chromium ;;
esac

echo "==> Circulation: config=${CONFIG} traffic=${TRAFFIC} project=${PROJECT}"

set +e
npx playwright test tests/example.spec.ts --project="${PROJECT}"
EXIT=$?
set -e

if [ -n "${METRICS_PUSH_URL:-}" ]; then
  PASSED=false
  [ "$EXIT" -eq 0 ] && PASSED=true
  curl -sf -X POST "${METRICS_PUSH_URL}" \
    -H "Content-Type: application/json" \
    -d "{\"config\":\"${CONFIG}\",\"trafficClass\":\"${TRAFFIC}\",\"passed\":${PASSED}}" \
    || echo "warning: metrics push failed" >&2
fi

exit "$EXIT"
