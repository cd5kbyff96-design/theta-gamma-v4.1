"""
Task Packets — Self-contained units of work.

This module defines task packets that are compiled from planning
artifacts and executed autonomously or by humans.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PacketDomain(str, Enum):
    """
    Packet domains for categorization.

    Domains group related packets together.
    """

    INFRA = "INFRA"
    DATA = "DATA"
    TRAIN = "TRAIN"
    EVAL = "EVAL"
    BUDGET = "BUDGET"
    SAFETY = "SAFETY"
    OPS = "OPS"


class PacketPriority(str, Enum):
    """
    Packet priorities.

    Priority determines execution order and review requirements.
    """

    P0_CRITICAL = "P0"
    P1_HIGH = "P1"
    P2_MEDIUM = "P2"
    P3_LOW = "P3"


class PacketStatus(str, Enum):
    """
    Packet execution status.

    Tracks packet progress through the execution pipeline.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PacketTest:
    """
    A test for packet completion verification.

    Attributes:
        name: Test name
        command: Command to run
        expected: Expected outcome
    """

    name: str
    command: str
    expected: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "command": self.command,
            "expected": self.expected,
        }


@dataclass
class TaskPacket:
    """
    A self-contained task packet.

    Attributes:
        packet_id: Unique identifier (e.g., "PKT-INFRA-001")
        title: Human-readable title
        priority: Packet priority
        domain: Packet domain
        estimated_effort: Estimated effort (e.g., "1d", "2d")
        depends_on: List of dependency packet IDs
        objective: Single measurable outcome
        inputs: Required inputs and prerequisites
        commands: Ordered list of commands to execute
        tests: Tests for completion verification
        done_definition: Unambiguous completion criteria
        stop_condition: Condition to abort without completing
        source_artifacts: Source markdown artifacts
        status: Current execution status
        created_at: Creation timestamp
        completed_at: Completion timestamp
    """

    packet_id: str
    title: str
    priority: PacketPriority
    domain: PacketDomain
    estimated_effort: str
    depends_on: list[str] = field(default_factory=list)
    objective: str = ""
    inputs: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    tests: list[PacketTest] = field(default_factory=list)
    done_definition: str = ""
    stop_condition: str = ""
    source_artifacts: list[str] = field(default_factory=list)
    status: PacketStatus = PacketStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    notes: str = ""

    def is_executable(self, completed_packets: set[str]) -> bool:
        """
        Check if packet is executable (all dependencies met).

        Args:
            completed_packets: Set of completed packet IDs

        Returns:
            True if all dependencies are complete
        """
        return all(dep in completed_packets for dep in self.depends_on)

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate packet completeness.

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        if not self.objective:
            issues.append("Missing objective")

        if not self.commands:
            issues.append("Missing commands")

        if not self.tests:
            issues.append("Missing tests")

        if not self.done_definition:
            issues.append("Missing done definition")

        if not self.stop_condition:
            issues.append("Missing stop condition")

        return (len(issues) == 0, issues)

    def mark_complete(self) -> None:
        """Mark packet as complete."""
        self.status = PacketStatus.DONE
        self.completed_at = datetime.now()

    def mark_in_progress(self) -> None:
        """Mark packet as in progress."""
        self.status = PacketStatus.IN_PROGRESS

    def mark_blocked(self, reason: str = "") -> None:
        """Mark packet as blocked."""
        self.status = PacketStatus.BLOCKED
        if reason:
            self.notes = f"Blocked: {reason}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "packet_id": self.packet_id,
            "title": self.title,
            "priority": self.priority.value,
            "domain": self.domain.value,
            "estimated_effort": self.estimated_effort,
            "depends_on": self.depends_on,
            "objective": self.objective,
            "inputs": self.inputs,
            "commands": self.commands,
            "tests": [t.to_dict() for t in self.tests],
            "done_definition": self.done_definition,
            "stop_condition": self.stop_condition,
            "source_artifacts": self.source_artifacts,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskPacket:
        """Create from dictionary."""
        return cls(
            packet_id=data["packet_id"],
            title=data["title"],
            priority=PacketPriority(data["priority"]),
            domain=PacketDomain(data["domain"]),
            estimated_effort=data["estimated_effort"],
            depends_on=data.get("depends_on", []),
            objective=data.get("objective", ""),
            inputs=data.get("inputs", []),
            commands=data.get("commands", []),
            tests=[PacketTest(**t) for t in data.get("tests", [])],
            done_definition=data.get("done_definition", ""),
            stop_condition=data.get("stop_condition", ""),
            source_artifacts=data.get("source_artifacts", []),
            status=PacketStatus(data.get("status", "pending")),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data.get("completed_at")
                else None
            ),
            notes=data.get("notes", ""),
        )
