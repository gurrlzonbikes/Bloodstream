"""Vitality and drift pressure model for execution configurations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class VitalityInput:
    traffic_class: str
    execution_count_7d: int
    minimum_runs_per_week: int
    hours_since_execution: float
    dormancy_threshold_hours: float
    drift_gap: float
    topology_change_activity: float
    target_vitality: float
    recent_failures: int
    recent_runs: int


@dataclass
class VitalityState:
    vitality_score: float
    dormancy_pressure: float
    execution_density: float
    drift_pressure: float
    drift_score: float
    flake_pressure: float
    congestion_score: float
    phase: str


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def compute_vitality(inp: VitalityInput) -> VitalityState:
    """Simple metabolically-inspired vitality formulas."""
    target = max(inp.minimum_runs_per_week, 1)
    execution_density = _clamp(inp.execution_count_7d / target)

    dormancy_ratio = inp.hours_since_execution / max(inp.dormancy_threshold_hours, 1)
    dormancy_pressure = _clamp(dormancy_ratio)

    # Drift correlates with dormancy duration and system evolution, not randomness
    drift_pressure = _clamp(
        (inp.drift_gap * 0.12)
        + (dormancy_pressure * 0.45)
        + (inp.topology_change_activity * 0.35)
    )
    drift_score = drift_pressure

    flake_pressure = 0.0
    if inp.recent_runs > 0:
        flake_pressure = _clamp(inp.recent_failures / inp.recent_runs)

    # High-traffic corridors stay healthy via maintenance-inducing traffic
    circulation_boost = execution_density * 0.55
    reconciliation_effect = (1.0 - drift_pressure) * 0.25
    vitality_raw = circulation_boost + reconciliation_effect - (dormancy_pressure * 0.35) - (flake_pressure * 0.2)
    vitality_score = _clamp(vitality_raw)

    congestion_score = _clamp(execution_density * 0.7 + flake_pressure * 0.3)

    if vitality_score >= inp.target_vitality:
        phase = "healthy"
    elif dormancy_pressure >= 0.85:
        phase = "dormant"
    elif drift_pressure >= 0.6:
        phase = "drifting"
    elif flake_pressure >= 0.5:
        phase = "congested"
    else:
        phase = "recovering"

    return VitalityState(
        vitality_score=round(vitality_score, 4),
        dormancy_pressure=round(dormancy_pressure, 4),
        execution_density=round(execution_density, 4),
        drift_pressure=round(drift_pressure, 4),
        drift_score=round(drift_score, 4),
        flake_pressure=round(flake_pressure, 4),
        congestion_score=round(congestion_score, 4),
        phase=phase,
    )


def hours_since(iso_timestamp: str | None) -> float:
    if not iso_timestamp:
        return 9999.0
    try:
        ts = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - ts.astimezone(timezone.utc)
        return max(delta.total_seconds() / 3600.0, 0.0)
    except ValueError:
        return 9999.0
