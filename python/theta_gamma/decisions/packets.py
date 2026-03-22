"""
Decision Packets — Weekly batched decisions with defaults.

This module implements decision packets that batch human decisions
with automatic defaults and hard deadlines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class DecisionStatus(str, Enum):
    """Decision status."""

    PENDING = "pending"
    ANSWERED = "answered"
    DEFAULTED = "defaulted"


class DecisionImpact(int, Enum):
    """Decision impact level."""

    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1


class DecisionUrgency(int, Enum):
    """Decision urgency level."""

    IMMEDIATE = 5
    THIS_WEEK = 4
    SOON = 3
    UPCOMING = 2
    LOW = 1


@dataclass
class DecisionOption:
    """
    A decision option.

    Attributes:
        label: Option label (A, B, C, etc.)
        description: Option description
        is_recommended: Whether this is the recommended default
    """

    label: str
    description: str
    is_recommended: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "label": self.label,
            "description": self.description,
            "is_recommended": self.is_recommended,
        }


@dataclass
class Decision:
    """
    A decision requiring human input.

    Attributes:
        decision_id: Unique identifier
        title: Decision title
        impact: Impact level (1-5)
        urgency: Urgency level (1-5)
        context: Decision context
        options: Available options
        recommended_default: Recommended default option
        deadline: Response deadline
        status: Decision status
        response: Human response if provided
    """

    decision_id: str
    title: str
    impact: DecisionImpact
    urgency: DecisionUrgency
    context: str
    options: list[DecisionOption]
    recommended_default: DecisionOption
    deadline: datetime
    status: DecisionStatus = DecisionStatus.PENDING
    response: str = ""
    source: str = ""

    @property
    def score(self) -> float:
        """Calculate decision score (impact × urgency)."""
        return self.impact.value * self.urgency.value

    def is_overdue(self) -> bool:
        """Check if decision is overdue."""
        return datetime.now() > self.deadline and self.status == DecisionStatus.PENDING

    def apply_default(self) -> None:
        """Apply recommended default."""
        self.status = DecisionStatus.DEFAULTED
        self.response = self.recommended_default.label

    def respond(self, option_label: str) -> None:
        """Record human response."""
        self.status = DecisionStatus.ANSWERED
        self.response = option_label

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "decision_id": self.decision_id,
            "title": self.title,
            "impact": self.impact.value,
            "urgency": self.urgency.value,
            "score": self.score,
            "context": self.context,
            "options": [o.to_dict() for o in self.options],
            "recommended_default": self.recommended_default.to_dict(),
            "deadline": self.deadline.isoformat(),
            "status": self.status.value,
            "response": self.response,
            "source": self.source,
            "is_overdue": self.is_overdue(),
        }


@dataclass
class DecisionPacket:
    """
    Weekly decision packet containing top 5 decisions.

    Attributes:
        packet_id: Packet identifier
        week: Week identifier
        generated_at: Generation timestamp
        deadline: Response deadline
        decisions: Top 5 decisions
        deferred_decisions: Decisions ranked 6+
    """

    packet_id: str
    week: str
    generated_at: datetime
    deadline: datetime
    decisions: list[Decision] = field(default_factory=list)
    deferred_decisions: list[Decision] = field(default_factory=list)

    def add_decision(self, decision: Decision) -> None:
        """Add a decision to the packet."""
        self.decisions.append(decision)
        # Keep only top 5
        self.decisions.sort(key=lambda d: d.score, reverse=True)
        if len(self.decisions) > 5:
            # Move lowest to deferred
            self.deferred_decisions.append(self.decisions.pop())

    def apply_defaults(self) -> list[Decision]:
        """Apply defaults to all unanswered decisions."""
        defaulted = []
        for decision in self.decisions:
            if decision.status == DecisionStatus.PENDING:
                decision.apply_default()
                defaulted.append(decision)
        return defaulted

    def process_response(self, responses: dict[str, str]) -> None:
        """
        Process human responses.

        Args:
            responses: Dictionary mapping decision_id to option label
        """
        for decision in self.decisions:
            if decision.decision_id in responses:
                decision.respond(responses[decision.decision_id])

        # Apply defaults to remaining
        self.apply_defaults()

    def get_summary(self) -> dict[str, Any]:
        """Get packet summary."""
        return {
            "packet_id": self.packet_id,
            "week": self.week,
            "generated_at": self.generated_at.isoformat(),
            "deadline": self.deadline.isoformat(),
            "total_decisions": len(self.decisions),
            "deferred_count": len(self.deferred_decisions),
            "answered": sum(1 for d in self.decisions if d.status == DecisionStatus.ANSWERED),
            "defaulted": sum(1 for d in self.decisions if d.status == DecisionStatus.DEFAULTED),
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            **self.get_summary(),
            "decisions": [d.to_dict() for d in self.decisions],
            "deferred_decisions": [d.to_dict() for d in self.deferred_decisions],
        }


class DecisionPacketGenerator:
    """
    Generator for weekly decision packets.

    Collects pending decisions, ranks them, and generates packets.
    """

    def __init__(self) -> None:
        """Initialize the generator."""
        self._pending_decisions: list[Decision] = []

    def add_pending_decision(self, decision: Decision) -> None:
        """Add a pending decision."""
        self._pending_decisions.append(decision)

    def generate_packet(
        self,
        week: str,
        deadline_hours: int = 32,
    ) -> DecisionPacket:
        """
        Generate a decision packet.

        Args:
            week: Week identifier
            deadline_hours: Hours until deadline

        Returns:
            DecisionPacket with top 5 decisions
        """
        packet_id = f"DP-{week}-{datetime.now().strftime('%Y%m%d')}"
        generated_at = datetime.now()
        deadline = generated_at + timedelta(hours=deadline_hours)

        packet = DecisionPacket(
            packet_id=packet_id,
            week=week,
            generated_at=generated_at,
            deadline=deadline,
        )

        # Sort by score and add top 5
        sorted_decisions = sorted(self._pending_decisions, key=lambda d: d.score, reverse=True)

        for decision in sorted_decisions[:5]:
            packet.add_decision(decision)

        # Remaining go to deferred
        for decision in sorted_decisions[5:]:
            packet.deferred_decisions.append(decision)

        # Clear pending
        self._pending_decisions = []

        return packet

    def get_pending_count(self) -> int:
        """Get count of pending decisions."""
        return len(self._pending_decisions)
