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
│  CRDs · Operator · Argo circulation workflows · Grafana      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  Circulation pod (bloodstream/circulation image)             │
│  Clones Automation Panda Playwright ch.03 → playwright.dev   │
└─────────────────────────────────────────────────────────────┘
```

## Quick start (local circulation test)

Requires Docker (builds image, clones [awesome-web-testing-playwright](https://github.com/AutomationPanda/awesome-web-testing-playwright) inside):

```bash
make test
```

## Quick start (Kubernetes)

Requires: Docker, k3d, kubectl

```bash
make cluster       # k3d cluster + Argo Workflows
make deploy        # build images, apply CRDs, operator, workflows
```

Port-forwards:

```bash
kubectl port-forward -n bloodstream svc/grafana 3000:3000
kubectl port-forward -n bloodstream svc/prometheus 9090:9090
kubectl get bloodstreamconfigs -n bloodstream
```

## Execution configurations

**Corridor (high traffic):** `chrome-latest`, `default-feature-flags`, `staging-env`

**Satellite (low traffic):** `safari`, `firefox`, `android-low-end`, `slow-network`, `feature-flag-alt-checkout`, `degraded-payment-provider`, `old-ui-version`

Circulation runs [chapter-03 example tests](https://github.com/AutomationPanda/awesome-web-testing-playwright/blob/main/chapter-code/chapter-03/tests/example.spec.ts) against **https://playwright.dev** (outbound network only).

## Vitality model

Each config tracks:

- `vitalityScore` — circulation health
- `dormancyPressure` — time since last execution
- `executionDensity` — runs vs weekly target
- `driftScore` — desync from evolving topology
- `flakePressure` — recent failure rate

## Simulating decay locally

With operator running:

```bash
make operator-dev   # terminal 1
make simulate       # inject corridor + dormant satellite traffic
```

## Project layout

```text
circulation/  Docker image — clones Panda ch.03, runs against playwright.dev
operator/     CRDs, controller, vitality model, metrics
deploy/       Kubernetes, Argo, Prometheus, Grafana
scripts/      cluster-setup, build, deploy, simulate
```

## Core thesis

> Frequently exercised configurations stay healthy because they continuously receive maintenance-inducing traffic. Rarely exercised configs decay because reconciliation pressure disappears.

Bloodstream makes that uneven confidence **visible and operable**.
