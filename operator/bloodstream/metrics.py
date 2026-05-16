from prometheus_client import Counter, Gauge, Histogram

CONFIG_VITALITY = Gauge(
    "bloodstream_config_vitality",
    "Vitality score for an execution configuration",
    ["config", "traffic_class", "namespace"],
)
EXECUTION_DENSITY = Gauge(
    "bloodstream_execution_density",
    "Execution density relative to circulation target",
    ["config", "namespace"],
)
DORMANCY_PRESSURE = Gauge(
    "bloodstream_dormancy_pressure",
    "Accumulated dormancy pressure",
    ["config", "namespace"],
)
DRIFT_SCORE = Gauge(
    "bloodstream_drift_score",
    "Operational drift score",
    ["config", "namespace"],
)
DRIFT_PRESSURE = Gauge(
    "bloodstream_drift_pressure",
    "Drift pressure from dormancy and topology change",
    ["config", "namespace"],
)
RECONCILIATION_LATENCY = Histogram(
    "bloodstream_reconciliation_latency_seconds",
    "Time since last successful reconciliation",
    ["config", "namespace"],
    buckets=[3600, 7200, 86400, 172800, 604800],
)
FLAKE_PRESSURE = Gauge(
    "bloodstream_flake_pressure",
    "Flake pressure from recent failures",
    ["config", "namespace"],
)
CONGESTION_SCORE = Gauge(
    "bloodstream_congestion_score",
    "Traffic congestion in execution corridor",
    ["config", "namespace"],
)
EXECUTIONS_TOTAL = Counter(
    "bloodstream_executions_total",
    "Circulation events executed",
    ["config", "traffic_class", "result", "namespace"],
)
PATH_VITALITY = Gauge(
    "bloodstream_path_vitality",
    "Aggregate vitality for a topology path",
    ["path", "namespace"],
)
TOPOLOGY_CHANGE_ACTIVITY = Gauge(
    "bloodstream_topology_change_activity",
    "System evolution activity level",
    ["namespace"],
)


def publish_config_metrics(
    namespace: str,
    config: str,
    traffic_class: str,
    vitality: float,
    density: float,
    dormancy: float,
    drift: float,
    drift_pressure: float,
    flake: float,
    congestion: float,
    hours_since_reconciliation: float,
) -> None:
    labels = {"config": config, "namespace": namespace}
    CONFIG_VITALITY.labels(config=config, traffic_class=traffic_class, namespace=namespace).set(vitality)
    EXECUTION_DENSITY.labels(**labels).set(density)
    DORMANCY_PRESSURE.labels(**labels).set(dormancy)
    DRIFT_SCORE.labels(**labels).set(drift)
    DRIFT_PRESSURE.labels(**labels).set(drift_pressure)
    FLAKE_PRESSURE.labels(**labels).set(flake)
    CONGESTION_SCORE.labels(**labels).set(congestion)
    RECONCILIATION_LATENCY.labels(**labels).observe(hours_since_reconciliation * 3600)
