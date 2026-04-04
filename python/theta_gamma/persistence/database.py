"""
Database — SQLite database connection and schema management.

Provides the core database infrastructure for Theta-Gamma persistence.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any


class Database:
    """
    SQLite database manager.

    Manages database connections, schema migrations, and provides
    context managers for safe database access.

    Example:
        >>> db = Database("theta_gamma.db")
        >>> db.init()
        >>> with db.connection() as conn:
        ...     cursor = conn.execute("SELECT * FROM metrics LIMIT 1")
    """

    def __init__(self, db_path: Path | str) -> None:
        """
        Initialize database.

        Args:
            db_path: Path to SQLite database file
        """
        self._db_path = Path(db_path)
        self._connection: sqlite3.Connection | None = None

    def init(self) -> None:
        """Initialize database schema."""
        with self.connection() as conn:
            # Metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id TEXT NOT NULL,
                    value REAL NOT NULL,
                    checkpoint_id TEXT,
                    run_id TEXT,
                    created_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)

            # Gate results table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS gate_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gate_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    evaluated_at TEXT NOT NULL,
                    all_passed INTEGER NOT NULL,
                    consecutive_failures INTEGER DEFAULT 0,
                    criterion_results TEXT,
                    message TEXT
                )
            """)

            # Checkpoints table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    checkpoint_id TEXT UNIQUE NOT NULL,
                    path TEXT NOT NULL,
                    gate_id TEXT,
                    metrics TEXT,
                    created_at TEXT NOT NULL,
                    size_bytes INTEGER,
                    is_best INTEGER DEFAULT 0
                )
            """)

            # Decision log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decision_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    decision_id TEXT NOT NULL,
                    decision_class TEXT,
                    tier TEXT NOT NULL,
                    choice_made TEXT NOT NULL,
                    rationale TEXT,
                    reversible TEXT,
                    artifacts_affected TEXT,
                    created_at TEXT NOT NULL,
                    override INTEGER DEFAULT 0,
                    amendment INTEGER DEFAULT 0
                )
            """)

            # Incidents table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id TEXT UNIQUE NOT NULL,
                    failure_mode_id TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    owner TEXT,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    resolved_at TEXT,
                    root_cause TEXT,
                    resolution_method TEXT,
                    escalation_target TEXT,
                    sla_met INTEGER DEFAULT 1
                )
            """)

            # Weekly reports table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weekly_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week TEXT UNIQUE NOT NULL,
                    generated_at TEXT NOT NULL,
                    go_no_go_decision TEXT NOT NULL,
                    metrics_summary TEXT,
                    gate_status TEXT,
                    budget_status TEXT,
                    top_packets TEXT,
                    watch_items TEXT,
                    blockers TEXT,
                    next_7_days_plan TEXT
                )
            """)

            # Create indexes
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_metrics_id ON metrics(metric_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_metrics_created ON metrics(created_at)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_gates_id ON gate_results(gate_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_checkpoints_id ON checkpoints(checkpoint_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_decisions_id ON decision_log(decision_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_incidents_state ON incidents(state)"
            )

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for database connection.

        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute(
        self,
        query: str,
        params: tuple[Any, ...] = (),
    ) -> list[sqlite3.Row]:
        """
        Execute a query and return results.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of Row results
        """
        with self.connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()

    def executemany(
        self,
        query: str,
        params_list: list[tuple[Any, ...]],
    ) -> int:
        """
        Execute a query with multiple parameter sets.

        Args:
            query: SQL query
            params_list: List of parameter tuples

        Returns:
            Number of rows affected
        """
        with self.connection() as conn:
            cursor = conn.executemany(query, params_list)
            return cursor.rowcount

    def fetchone(
        self,
        query: str,
        params: tuple[Any, ...] = (),
    ) -> sqlite3.Row | None:
        """
        Execute query and fetch one result.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Row or None if not found
        """
        with self.connection() as conn:
            return conn.execute(query, params).fetchone()

    def fetchall(
        self,
        query: str,
        params: tuple[Any, ...] = (),
    ) -> list[sqlite3.Row]:
        """
        Execute query and fetch all results.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of rows
        """
        with self.connection() as conn:
            return conn.execute(query, params).fetchall()

    def delete(self) -> None:
        """Delete the database file."""
        if self._db_path.exists():
            self._db_path.unlink()


# Module-level database instance (singleton pattern)
_database: Database | None = None


def get_database(db_path: Path | str | None = None) -> Database:
    """
    Get or create the database instance.

    Args:
        db_path: Optional path to database file

    Returns:
        Database instance
    """
    # Use module-level variable (avoid global keyword)
    import theta_gamma.persistence.database as _db_module

    if _db_module._database is None:
        if db_path is None:
            db_path = Path("theta_gamma.db")
        _db_module._database = Database(db_path)

    return _db_module._database


def init_database(db_path: Path | str | None = None) -> Database:
    """
    Initialize the database with schema.

    Args:
        db_path: Optional path to database file

    Returns:
        Initialized Database instance
    """
    db = get_database(db_path)
    db.init()
    return db
