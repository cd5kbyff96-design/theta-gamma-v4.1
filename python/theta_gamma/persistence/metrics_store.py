"""
Metrics Store — Persistent storage for metric history.

Stores and retrieves metric values with support for time-series queries
and aggregation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from theta_gamma.persistence.database import Database


@dataclass
class MetricRecord:
    """
    A metric record.

    Attributes:
        metric_id: Metric identifier (e.g., "M-CM-001")
        value: Metric value
        checkpoint_id: Optional checkpoint ID
        run_id: Optional run identifier
        created_at: Record timestamp
        metadata: Optional metadata dictionary
    """

    metric_id: str
    value: float
    checkpoint_id: str = ""
    run_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metric_id": self.metric_id,
            "value": self.value,
            "checkpoint_id": self.checkpoint_id,
            "run_id": self.run_id,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_row(cls, row: Any) -> "MetricRecord":
        """Create from database row."""
        return cls(
            metric_id=row["metric_id"],
            value=row["value"],
            checkpoint_id=row["checkpoint_id"] or "",
            run_id=row["run_id"] or "",
            created_at=datetime.fromisoformat(row["created_at"]),
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )


class MetricsStore:
    """
    Persistent metrics storage.

    Provides methods for storing, retrieving, and aggregating metric values.

    Example:
        >>> store = MetricsStore(db)
        >>> store.record("M-CM-001", 45.0, run_id="run-001")
        >>> values = store.get_values("M-CM-001", limit=10)
    """

    def __init__(self, db: Database) -> None:
        """
        Initialize metrics store.

        Args:
            db: Database instance
        """
        self._db = db

    def record(
        self,
        metric_id: str,
        value: float,
        checkpoint_id: str = "",
        run_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """
        Record a metric value.

        Args:
            metric_id: Metric identifier
            value: Metric value
            checkpoint_id: Optional checkpoint ID
            run_id: Optional run identifier
            metadata: Optional metadata

        Returns:
            Record ID
        """
        cursor = self._db.execute(
            """
            INSERT INTO metrics (metric_id, value, checkpoint_id, run_id, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                metric_id,
                value,
                checkpoint_id,
                run_id,
                datetime.now().isoformat(),
                json.dumps(metadata) if metadata else None,
            ),
        )
        return cursor.lastrowid

    def record_batch(self, records: list[MetricRecord]) -> int:
        """
        Record multiple metrics in a batch.

        Args:
            records: List of metric records

        Returns:
            Number of records inserted
        """
        params_list = [
            (
                r.metric_id,
                r.value,
                r.checkpoint_id,
                r.run_id,
                r.created_at.isoformat(),
                json.dumps(r.metadata) if r.metadata else None,
            )
            for r in records
        ]

        self._db.executemany(
            """
            INSERT INTO metrics (metric_id, value, checkpoint_id, run_id, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            params_list,
        )
        return len(records)

    def get_values(
        self,
        metric_id: str,
        limit: int = 100,
        run_id: str | None = None,
    ) -> list[float]:
        """
        Get metric values.

        Args:
            metric_id: Metric identifier
            limit: Maximum values to return
            run_id: Optional run filter

        Returns:
            List of metric values
        """
        if run_id:
            rows = self._db.fetchall(
                """
                SELECT value FROM metrics
                WHERE metric_id = ? AND run_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (metric_id, run_id, limit),
            )
        else:
            rows = self._db.fetchall(
                """
                SELECT value FROM metrics
                WHERE metric_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (metric_id, limit),
            )

        return [row["value"] for row in rows]

    def get_latest(
        self,
        metric_id: str,
        run_id: str | None = None,
    ) -> float | None:
        """
        Get latest metric value.

        Args:
            metric_id: Metric identifier
            run_id: Optional run filter

        Returns:
            Latest value or None if not found
        """
        values = self.get_values(metric_id, limit=1, run_id=run_id)
        return values[0] if values else None

    def get_mean(
        self,
        metric_id: str,
        window: int = 10,
        run_id: str | None = None,
    ) -> float | None:
        """
        Get mean of recent metric values.

        Args:
            metric_id: Metric identifier
            window: Number of values to average
            run_id: Optional run filter

        Returns:
            Mean value or None if not enough values
        """
        values = self.get_values(metric_id, limit=window, run_id=run_id)
        if not values:
            return None
        return sum(values) / len(values)

    def get_stddev(
        self,
        metric_id: str,
        window: int = 10,
        run_id: str | None = None,
    ) -> float | None:
        """
        Get standard deviation of recent metric values.

        Args:
            metric_id: Metric identifier
            window: Number of values
            run_id: Optional run filter

        Returns:
            Standard deviation or None if not enough values
        """
        values = self.get_values(metric_id, limit=window, run_id=run_id)
        if len(values) < 2:
            return None

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5

    def get_records(
        self,
        metric_id: str | None = None,
        run_id: str | None = None,
        checkpoint_id: str | None = None,
        limit: int = 100,
    ) -> list[MetricRecord]:
        """
        Get metric records with filters.

        Args:
            metric_id: Optional metric filter
            run_id: Optional run filter
            checkpoint_id: Optional checkpoint filter
            limit: Maximum records to return

        Returns:
            List of metric records
        """
        conditions = []
        params: list[Any] = []

        if metric_id:
            conditions.append("metric_id = ?")
            params.append(metric_id)
        if run_id:
            conditions.append("run_id = ?")
            params.append(run_id)
        if checkpoint_id:
            conditions.append("checkpoint_id = ?")
            params.append(checkpoint_id)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        rows = self._db.fetchall(
            f"""
            SELECT * FROM metrics
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ?
            """,
            params + [limit],
        )

        return [MetricRecord.from_row(row) for row in rows]

    def get_metrics_for_run(self, run_id: str) -> dict[str, float]:
        """
        Get latest metrics for a run.

        Args:
            run_id: Run identifier

        Returns:
            Dictionary of metric_id to latest value
        """
        records = self.get_records(run_id=run_id, limit=1000)
        metrics: dict[str, float] = {}

        for record in records:
            if record.metric_id not in metrics:
                metrics[record.metric_id] = record.value

        return metrics

    def delete_before(self, cutoff: datetime) -> int:
        """
        Delete records older than cutoff.

        Args:
            cutoff: Cutoff datetime

        Returns:
            Number of records deleted
        """
        cursor = self._db.execute(
            "DELETE FROM metrics WHERE created_at < ?",
            (cutoff.isoformat(),),
        )
        return cursor.rowcount
