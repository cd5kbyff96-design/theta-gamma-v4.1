"""
Checkpoint Store — Persistent storage for model checkpoints.

Stores checkpoint metadata including path, metrics, and gate associations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from theta_gamma.persistence.database import Database


@dataclass
class CheckpointRecord:
    """
    A checkpoint record.

    Attributes:
        checkpoint_id: Unique checkpoint identifier
        path: File path to checkpoint
        gate_id: Associated gate (e.g., "G1", "G2")
        metrics: Dictionary of metric values
        created_at: Checkpoint timestamp
        size_bytes: Checkpoint file size
        is_best: Whether this is the best checkpoint for its gate
    """

    checkpoint_id: str
    path: str
    gate_id: str = ""
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0
    is_best: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "path": self.path,
            "gate_id": self.gate_id,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat(),
            "size_bytes": self.size_bytes,
            "is_best": self.is_best,
        }

    @classmethod
    def from_row(cls, row: Any) -> "CheckpointRecord":
        """Create from database row."""
        return cls(
            checkpoint_id=row["checkpoint_id"],
            path=row["path"],
            gate_id=row["gate_id"] or "",
            metrics=json.loads(row["metrics"]) if row["metrics"] else {},
            created_at=datetime.fromisoformat(row["created_at"]),
            size_bytes=row["size_bytes"] or 0,
            is_best=bool(row["is_best"]),
        )


class CheckpointStore:
    """
    Persistent checkpoint storage.

    Provides methods for storing, retrieving, and managing checkpoints.

    Example:
        >>> store = CheckpointStore(db)
        >>> store.save("ckpt-001", "/path/to/ckpt.pt", gate_id="G1")
        >>> best = store.get_best_for_gate("G1")
    """

    def __init__(self, db: Database) -> None:
        """
        Initialize checkpoint store.

        Args:
            db: Database instance
        """
        self._db = db

    def save(
        self,
        checkpoint_id: str,
        path: str | Path,
        gate_id: str = "",
        metrics: dict[str, float] | None = None,
        size_bytes: int = 0,
    ) -> None:
        """
        Save a checkpoint record.

        Args:
            checkpoint_id: Checkpoint identifier
            path: File path to checkpoint
            gate_id: Associated gate
            metrics: Metric values at checkpoint
            size_bytes: File size
        """
        self._db.execute(
            """
            INSERT OR REPLACE INTO checkpoints
            (checkpoint_id, path, gate_id, metrics, created_at, size_bytes, is_best)
            VALUES (?, ?, ?, ?, ?, ?, 0)
            """,
            (
                checkpoint_id,
                str(path),
                gate_id,
                json.dumps(metrics) if metrics else None,
                datetime.now().isoformat(),
                size_bytes,
            ),
        )

    def get(self, checkpoint_id: str) -> CheckpointRecord | None:
        """
        Get a checkpoint by ID.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            Checkpoint record or None
        """
        row = self._db.fetchone(
            "SELECT * FROM checkpoints WHERE checkpoint_id = ?",
            (checkpoint_id,),
        )
        return CheckpointRecord.from_row(row) if row else None

    def get_best_for_gate(self, gate_id: str) -> CheckpointRecord | None:
        """
        Get the best checkpoint for a gate.

        Args:
            gate_id: Gate identifier

        Returns:
            Best checkpoint or None
        """
        row = self._db.fetchone(
            """
            SELECT * FROM checkpoints
            WHERE gate_id = ? AND is_best = 1
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (gate_id,),
        )
        return CheckpointRecord.from_row(row) if row else None

    def get_all_for_gate(
        self,
        gate_id: str,
        limit: int = 10,
    ) -> list[CheckpointRecord]:
        """
        Get all checkpoints for a gate.

        Args:
            gate_id: Gate identifier
            limit: Maximum checkpoints to return

        Returns:
            List of checkpoint records
        """
        rows = self._db.fetchall(
            """
            SELECT * FROM checkpoints
            WHERE gate_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (gate_id, limit),
        )
        return [CheckpointRecord.from_row(row) for row in rows]

    def mark_as_best(self, checkpoint_id: str) -> None:
        """
        Mark a checkpoint as the best for its gate.

        Args:
            checkpoint_id: Checkpoint identifier
        """
        # First, get the checkpoint to find its gate
        checkpoint = self.get(checkpoint_id)
        if not checkpoint or not checkpoint.gate_id:
            return

        # Unmark all checkpoints for this gate
        self._db.execute(
            "UPDATE checkpoints SET is_best = 0 WHERE gate_id = ?",
            (checkpoint.gate_id,),
        )

        # Mark this one as best
        self._db.execute(
            "UPDATE checkpoints SET is_best = 1 WHERE checkpoint_id = ?",
            (checkpoint_id,),
        )

    def get_latest(self, limit: int = 10) -> list[CheckpointRecord]:
        """
        Get latest checkpoints.

        Args:
            limit: Maximum checkpoints to return

        Returns:
            List of checkpoint records
        """
        rows = self._db.fetchall(
            """
            SELECT * FROM checkpoints
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [CheckpointRecord.from_row(row) for row in rows]

    def delete(self, checkpoint_id: str) -> bool:
        """
        Delete a checkpoint record.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            True if deleted, False if not found
        """
        cursor = self._db.execute(
            "DELETE FROM checkpoints WHERE checkpoint_id = ?",
            (checkpoint_id,),
        )
        return cursor.rowcount > 0

    def count(self) -> int:
        """
        Get total checkpoint count.

        Returns:
            Number of checkpoints
        """
        row = self._db.fetchone("SELECT COUNT(*) as count FROM checkpoints")
        return row["count"] if row else 0
