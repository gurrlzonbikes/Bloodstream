# Bloodstream

Kubernetes-native **verification circulation** platform. Bloodstream models E2E verification as a living traffic system where execution configurations remain reliable only through continuous operational circulation.

This is not a test runner — it is a control plane for execution vitality, dormant configuration decay, and topology synchronization.

## What the prototype demonstrates

| Behavior | Mechanism |
|----------|-----------|
| Uneven traffic | Corridor configs run every 30m; satellites every 6h |
| Dormant decay | Drift correlates with dormancy + system evolution |
| Vitality scoring | `BloodstreamConfig` controller + Prometheus metrics |
| Circulation restore | Argo `reconcile-dormant` workflow |
| Topology awareness | `BloodstreamPath` aggregates config vitality |
| Observability | Grafana dashboard: heatmap, drift, density |

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                  Bloodstream Control Plane                   │
│  CRDs: BloodstreamConfig, BloodstreamPath                   │
│  Operator: vitality reconciliation + Prometheus metrics      │
│  Argo: circulation events (corridor / satellite / reconcile)│
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  Demo topology: frontend → auth → payments (+ flags/evolution)│
│  Playwright circulation jobs per execution configuration       │
└─────────────────────────────────────────────────────────────┘
```

## Quick start (local demo app)

```bash
make demo          # docker compose — shop on :3000
make test          # Playwright checkout-flow (chrome-latest)
```

## Quick start (Kubernetes)

Requires: Docker, k3d, kubectl

```bash
make cluster       # k3d cluster + Argo Workflows
make deploy        # build images, apply CRDs, operator, workflows
```

Port-forwards:

```bash
kubectl port-forward -n bloodstream svc/grafana 3000:3000      # admin / bloodstream
kubectl port-forward -n bloodstream svc/prometheus 9090:9090
kubectl port-forward -n bloodstream-demo svc/demo-frontend 3000:80
kubectl get bloodstreamconfigs -n bloodstream
```

## Execution configurations

**Corridor (high traffic):** `chrome-latest`, `default-feature-flags`, `staging-env`

**Satellite (low traffic):** `safari`, `firefox`, `android-low-end`, `slow-network`, `feature-flag-alt-checkout`, `degraded-payment-provider`, `old-ui-version`

## Vitality model

Each config tracks:

- `vitalityScore` — circulation health
- `dormancyPressure` — time since last execution
- `executionDensity` — runs vs weekly target
- `driftScore` — desync from evolving topology
- `flakePressure` — recent failure rate

Drift is **deterministic**: `driftGap × evolution + dormancy × topologyChangeActivity`.

## Metrics

```text
bloodstream_config_vitality
bloodstream_execution_density
bloodstream_dormancy_pressure
bloodstream_drift_score
bloodstream_drift_pressure
bloodstream_reconciliation_latency_seconds
bloodstream_flake_pressure
bloodstream_congestion_score
bloodstream_executions_total
bloodstream_path_vitality
```

## Simulating decay locally

With demo app + operator running:

```bash
make operator-dev   # terminal 1
make simulate       # inject corridor traffic + evolution + dormant satellites
```

## Project layout

```text
demo-app/     Fake ecommerce + evolution service
e2e/          Playwright circulation tests
operator/     CRDs, controller, vitality model, metrics
deploy/       Kubernetes, Argo, Prometheus, Grafana
scripts/      cluster-setup, build, deploy, simulate
```

## Core thesis

> Frequently exercised configurations stay healthy because they continuously receive maintenance-inducing traffic. Rarely exercised configs decay because reconciliation pressure disappears.

Bloodstream makes that uneven confidence **visible and operable**.
