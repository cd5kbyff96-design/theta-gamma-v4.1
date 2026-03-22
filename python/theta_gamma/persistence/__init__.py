"""
Persistence module — SQLite storage for metrics, checkpoints, and decisions.

This module provides persistent storage for:
- Metrics history
- Gate evaluation results
- Checkpoint metadata
- Decision logs
- Incident records
"""

from theta_gamma.persistence.database import (
    Database,
    get_database,
    init_database,
)
from theta_gamma.persistence.metrics_store import (
    MetricsStore,
    MetricRecord,
)
from theta_gamma.persistence.checkpoints import (
    CheckpointStore,
    CheckpointRecord,
)
from theta_gamma.persistence.decision_log import (
    DecisionLog,
    DecisionLogEntry,
)

__all__ = [
    # Database
    "Database",
    "get_database",
    "init_database",
    # Metrics
    "MetricsStore",
    "MetricRecord",
    # Checkpoints
    "CheckpointStore",
    "CheckpointRecord",
    # Decisions
    "DecisionLog",
    "DecisionLogEntry",
]
