from bloodstream.vitality import VitalityInput, compute_vitality


def test_corridor_stays_healthy_with_traffic():
    state = compute_vitality(
        VitalityInput(
            traffic_class="corridor",
            execution_count_7d=50,
            minimum_runs_per_week=50,
            hours_since_execution=2,
            dormancy_threshold_hours=12,
            drift_gap=0,
            topology_change_activity=0.3,
            target_vitality=0.85,
            recent_failures=0,
            recent_runs=10,
        )
    )
    assert state.vitality_score >= 0.65
    assert state.phase in ("healthy", "recovering")


def test_dormant_satellite_drifts():
    state = compute_vitality(
        VitalityInput(
            traffic_class="satellite",
            execution_count_7d=0,
            minimum_runs_per_week=1,
            hours_since_execution=200,
            dormancy_threshold_hours=72,
            drift_gap=4,
            topology_change_activity=0.6,
            target_vitality=0.7,
            recent_failures=3,
            recent_runs=3,
        )
    )
    assert state.dormancy_pressure > 0.8
    assert state.drift_score > 0.5
    assert state.phase in ("dormant", "drifting", "congested")
