"""In-memory execution history for prototype reconciliation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ExecutionRecord:
    config: str
    passed: bool
    drift_gap: float
    at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutionStore:
    def __init__(self) -> None:
        self._records: list[ExecutionRecord] = []
        self.topology_change_activity: float = 0.0
        self.system_selector_epoch: int = 0

    def record(self, config: str, passed: bool, drift_gap: float = 0.0) -> None:
        self._records.append(ExecutionRecord(config=config, passed=passed, drift_gap=drift_gap))

    def count_7d(self, config: str) -> int:
        cutoff = datetime.now(timezone.utc).timestamp() - 7 * 86400
        return sum(
            1
            for r in self._records
            if r.config == config and r.at.timestamp() >= cutoff
        )

    def recent_stats(self, config: str, limit: int = 10) -> tuple[int, int]:
        recent = [r for r in self._records if r.config == config][-limit:]
        failures = sum(1 for r in recent if not r.passed)
        return failures, len(recent)

    def last_execution_iso(self, config: str) -> str | None:
        for r in reversed(self._records):
            if r.config == config:
                return r.at.isoformat()
        return None

    def update_topology(self, activity: float, selector_epoch: int) -> None:
        self.topology_change_activity = activity
        self.system_selector_epoch = selector_epoch


STORE = ExecutionStore()
