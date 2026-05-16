"""Bloodstream verification circulation controller."""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone

import httpx
import kopf
from kubernetes import client, config

from .metrics import PATH_VITALITY, TOPOLOGY_CHANGE_ACTIVITY, publish_config_metrics
from .store import STORE
from .vitality import VitalityInput, compute_vitality, hours_since

logger = logging.getLogger(__name__)

EVOLUTION_URL = os.getenv(
    "EVOLUTION_URL",
    "http://demo-evolution.bloodstream-demo.svc.cluster.local:3004",
)
NAMESPACE = os.getenv("BLOODSTREAM_NAMESPACE", "bloodstream")


def _api() -> client.CustomObjectsApi:
    return client.CustomObjectsApi()


async def fetch_evolution_state() -> dict:
    try:
        async with httpx.AsyncClient(timeout=5.0) as http:
            res = await http.get(f"{EVOLUTION_URL}/state")
            res.raise_for_status()
            return res.json()
    except Exception as exc:
        logger.warning("evolution fetch failed: %s", exc)
        return {"generation": 0, "selectorEpoch": 0, "topologyChangeActivity": 0}


def reconcile_config(spec: dict, status: dict | None, name: str, namespace: str, evolution: dict) -> dict:
    status = status or {}
    circulation = spec.get("circulation", {})
    vitality_spec = spec.get("vitality", {})

    min_runs = int(circulation.get("minimumRunsPerWeek", 1))
    dormancy_threshold = float(circulation.get("dormancyThresholdHours", 72))
    target = float(vitality_spec.get("targetScore", 0.7))
    traffic_class = spec.get("trafficClass", "satellite")

    execution_count = STORE.count_7d(name)
    last_exec = STORE.last_execution_iso(name) or status.get("lastExecution")
    hours_dormant = hours_since(last_exec)
    failures, recent_runs = STORE.recent_stats(name)

    selector_epoch = int(evolution.get("selectorEpoch", 0))
    reconciled_epoch = int(status.get("reconciledSelectorEpoch", 0))
    if traffic_class == "corridor":
        reconciled_epoch = selector_epoch  # corridors continuously reconcile
    drift_gap = max(0, selector_epoch - reconciled_epoch)

    topology_activity = float(evolution.get("topologyChangeActivity", STORE.topology_change_activity))

    state = compute_vitality(
        VitalityInput(
            traffic_class=traffic_class,
            execution_count_7d=execution_count,
            minimum_runs_per_week=min_runs,
            hours_since_execution=hours_dormant,
            dormancy_threshold_hours=dormancy_threshold,
            drift_gap=drift_gap,
            topology_change_activity=topology_activity,
            target_vitality=target,
            recent_failures=failures,
            recent_runs=recent_runs,
        )
    )

    publish_config_metrics(
        namespace=namespace,
        config=name,
        traffic_class=traffic_class,
        vitality=state.vitality_score,
        density=state.execution_density,
        dormancy=state.dormancy_pressure,
        drift=state.drift_score,
        drift_pressure=state.drift_pressure,
        flake=state.flake_pressure,
        congestion=state.congestion_score,
        hours_since_reconciliation=hours_since(status.get("lastReconciliation")),
    )

    now = datetime.now(timezone.utc).isoformat()
    new_status = {
        "vitalityScore": state.vitality_score,
        "dormancyPressure": state.dormancy_pressure,
        "executionDensity": state.execution_density,
        "driftPressure": state.drift_pressure,
        "driftScore": state.drift_score,
        "flakePressure": state.flake_pressure,
        "congestionScore": state.congestion_score,
        "phase": state.phase,
        "executionCount7d": execution_count,
        "lastExecution": last_exec or status.get("lastExecution"),
        "reconciledSelectorEpoch": reconciled_epoch,
    }

    if execution_count > 0 and state.vitality_score >= target * 0.9:
        new_status["lastReconciliation"] = now
        new_status["reconciledSelectorEpoch"] = selector_epoch

    return new_status


@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    settings.posting.level = logging.INFO
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()


@kopf.on.create("bloodstream.io", "v1", "bloodstreamconfigs")
@kopf.on.update("bloodstream.io", "v1", "bloodstreamconfigs")
async def reconcile_bloodstream_config(spec, status, name, namespace, **_):
    evolution = await fetch_evolution_state()
    STORE.update_topology(
        float(evolution.get("topologyChangeActivity", 0)),
        int(evolution.get("selectorEpoch", 0)),
    )
    new_status = reconcile_config(spec, status, name, namespace, evolution)
    return {"status": new_status}


@kopf.on.create("bloodstream.io", "v1", "bloodstreampaths")
@kopf.on.update("bloodstream.io", "v1", "bloodstreampaths")
async def reconcile_bloodstream_path(spec, status, name, namespace, **_):
    status = status or {}
    configs = spec.get("configs", [])
    config_vitality: dict[str, float] = {}
    dormant: list[str] = []

    api = _api()
    for cfg_name in configs:
        try:
            obj = api.get_namespaced_custom_object(
                group="bloodstream.io",
                version="v1",
                namespace=namespace,
                plural="bloodstreamconfigs",
                name=cfg_name,
            )
            vs = obj.get("status", {}).get("vitalityScore", 0.5)
            phase = obj.get("status", {}).get("phase", "unknown")
            config_vitality[cfg_name] = vs
            if phase in ("dormant", "drifting"):
                dormant.append(cfg_name)
        except client.exceptions.ApiException:
            config_vitality[cfg_name] = 0.0
            dormant.append(cfg_name)

    path_vitality = sum(config_vitality.values()) / max(len(config_vitality), 1)
    PATH_VITALITY.labels(path=name, namespace=namespace).set(path_vitality)

    return {
        "status": {
            "pathVitality": round(path_vitality, 4),
            "configVitality": config_vitality,
            "dormantConfigs": dormant,
            "lastTopologySync": datetime.now(timezone.utc).isoformat(),
        }
    }


@kopf.timer("bloodstream.io", "v1", "bloodstreamconfigs", interval=30.0)
async def periodic_reconcile(spec, status, name, namespace, **_):
    evolution = await fetch_evolution_state()
    return {"status": reconcile_config(spec, status, name, namespace, evolution)}


async def evolution_pressure_loop():
    """Increase system evolution when dormant configs accumulate risk."""
    while True:
        await asyncio.sleep(120)
        try:
            api = _api()
            configs = api.list_namespaced_custom_object(
                group="bloodstream.io",
                version="v1",
                namespace=NAMESPACE,
                plural="bloodstreamconfigs",
            )
            dormant_count = sum(
                1
                for item in configs.get("items", [])
                if item.get("status", {}).get("phase") in ("dormant", "drifting")
            )
            if dormant_count >= 2:
                async with httpx.AsyncClient(timeout=5.0) as http:
                    await http.post(f"{EVOLUTION_URL}/evolve", json={"steps": 1})
                    logger.info("evolution step triggered (%d dormant configs)", dormant_count)
        except Exception as exc:
            logger.debug("evolution loop: %s", exc)


@kopf.on.startup()
async def start_background_tasks(**_):
    asyncio.create_task(evolution_pressure_loop())
