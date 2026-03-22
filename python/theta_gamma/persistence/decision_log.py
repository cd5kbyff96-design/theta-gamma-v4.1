"""
Decision Log — Persistent storage for autonomous decisions.

Stores all autonomous decisions made by the pipeline per A0 specification.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from theta_gamma.persistence.database import Database


@dataclass
class DecisionLogEntry:
    """
    A decision log entry.

    Per A0 specification §8, every autonomous decision must produce
    a log entry with timestamp, decision class, tier, choice, rationale.

    Attributes:
        decision_id: Unique identifier
        decision_class: Reference to decision matrix (e.g., "DC-001")
        tier: Decision tier (T0-T4)
        choice_made: Choice made (default/fallback)
        rationale: One-line explanation
        reversible: Whether decision is reversible
        artifacts_affected: List of affected files/resources
        created_at: Decision timestamp
        override: Whether this was a human override
        amendment: Whether this was a contract amendment
    """

    decision_id: str
    decision_class: str
    tier: str
    choice_made: str
    rationale: str = ""
    reversible: bool = True
    artifacts_affected: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    override: bool = False
    amendment: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "decision_id": self.decision_id,
            "decision_class": self.decision_class,
            "tier": self.tier,
            "choice_made": self.choice_made,
            "rationale": self.rationale,
            "reversible": "yes" if self.reversible else "no",
            "artifacts_affected": self.artifacts_affected,
            "created_at": self.created_at.isoformat(),
            "override": self.override,
            "amendment": self.amendment,
        }

    @classmethod
    def from_row(cls, row: Any) -> "DecisionLogEntry":
        """Create from database row."""
        return cls(
            decision_id=row["decision_id"],
            decision_class=row["decision_class"] or "",
            tier=row["tier"],
            choice_made=row["choice_made"],
            rationale=row["rationale"] or "",
            reversible=row["reversible"] == "yes",
            artifacts_affected=json.loads(row["artifacts_affected"]) if row["artifacts_affected"] else [],
            created_at=datetime.fromisoformat(row["created_at"]),
            override=bool(row["override"]),
            amendment=bool(row["amendment"]),
        )


class DecisionLog:
    """
    Persistent decision log.

    Implements A0 specification §8 Logging Requirements.

    Example:
        >>> log = DecisionLog(db)
        >>> log.log("DC-001", "T0", "default", "Creating file in workspace")
        >>> entries = log.get_entries(limit=10)
    """

    def __init__(self, db: Database) -> None:
        """
        Initialize decision log.

        Args:
            db: Database instance
        """
        self._db = db

    def log(
        self,
        decision_class: str,
        tier: str,
        choice_made: str,
        rationale: str,
        reversible: bool = True,
        artifacts_affected: list[str] | None = None,
        override: bool = False,
        amendment: bool = False,
    ) -> str:
        """
        Log a decision.

        Args:
            decision_class: Decision class from matrix
            tier: Decision tier (T0-T4)
            choice_made: Choice made
            rationale: Explanation
            reversible: Whether reversible
            artifacts_affected: Affected resources
            override: Human override flag
            amendment: Contract amendment flag

        Returns:
            Decision ID
        """
        decision_id = f"DEC-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{tier}"

        self._db.execute(
            """
            INSERT INTO decision_log
            (decision_id, decision_class, tier, choice_made, rationale, reversible,
             artifacts_affected, created_at, override, amendment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision_id,
                decision_class,
                tier,
                choice_made,
                rationale,
                "yes" if reversible else "no",
                json.dumps(artifacts_affected) if artifacts_affected else None,
                datetime.now().isoformat(),
                1 if override else 0,
                1 if amendment else 0,
            ),
        )

        return decision_id

    def get_entry(self, decision_id: str) -> DecisionLogEntry | None:
        """
        Get a log entry by ID.

        Args:
            decision_id: Decision identifier

        Returns:
            Log entry or None
        """
        row = self._db.fetchone(
            "SELECT * FROM decision_log WHERE decision_id = ?",
            (decision_id,),
        )
        return DecisionLogEntry.from_row(row) if row else None

    def get_entries(
        self,
        decision_class: str | None = None,
        tier: str | None = None,
        limit: int = 100,
    ) -> list[DecisionLogEntry]:
        """
        Get log entries with filters.

        Args:
            decision_class: Optional class filter
            tier: Optional tier filter
            limit: Maximum entries to return

        Returns:
            List of log entries
        """
        conditions = []
        params: list[Any] = []

        if decision_class:
            conditions.append("decision_class = ?")
            params.append(decision_class)
        if tier:
            conditions.append("tier = ?")
            params.append(tier)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        rows = self._db.fetchall(
            f"""
            SELECT * FROM decision_log
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ?
            """,
            params + [limit],
        )

        return [DecisionLogEntry.from_row(row) for row in rows]

    def get_overrides(self, limit: int = 50) -> list[DecisionLogEntry]:
        """
        Get human override entries.

        Args:
            limit: Maximum entries to return

        Returns:
            List of override entries
        """
        rows = self._db.fetchall(
            """
            SELECT * FROM decision_log
            WHERE override = 1
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [DecisionLogEntry.from_row(row) for row in rows]

    def get_amendments(self, limit: int = 50) -> list[DecisionLogEntry]:
        """
        Get contract amendment entries.

        Args:
            limit: Maximum entries to return

        Returns:
            List of amendment entries
        """
        rows = self._db.fetchall(
            """
            SELECT * FROM decision_log
            WHERE amendment = 1
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [DecisionLogEntry.from_row(row) for row in rows]

    def get_daily_summary(self, date: datetime) -> dict[str, Any]:
        """
        Get daily decision summary.

        Args:
            date: Date to summarize

        Returns:
            Summary dictionary
        """
        date_str = date.strftime("%Y-%m-%d")

        rows = self._db.fetchall(
            """
            SELECT tier, COUNT(*) as count
            FROM decision_log
            WHERE created_at LIKE ?
            GROUP BY tier
            """,
            (f"{date_str}%",),
        )

        by_tier = {row["tier"]: row["count"] for row in rows}

        return {
            "date": date_str,
            "total": sum(by_tier.values()),
            "by_tier": by_tier,
        }

    def count(self) -> int:
        """
        Get total decision count.

        Returns:
            Number of logged decisions
        """
        row = self._db.fetchone("SELECT COUNT(*) as count FROM decision_log")
        return row["count"] if row else 0
