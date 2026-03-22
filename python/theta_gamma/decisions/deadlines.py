"""
Decision Deadlines — Deadline policies for human decisions.

This module implements deadline policies that ensure no decision
blocks the pipeline indefinitely.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class DecisionType(str, Enum):
    """
    Decision types with standard deadlines.

    Each type has a standard deadline and default action.
    """

    WEEKLY_PACKET = "weekly_packet"
    MID_WEEK_S1 = "mid_week_s1"
    MID_WEEK_S2 = "mid_week_s2"
    GATE_TRANSITION = "gate_transition"
    BUDGET_AMENDMENT = "budget_amendment"
    RECOVERY_RESTART = "recovery_restart"


@dataclass
class DeadlinePolicy:
    """
    Deadline policy configuration.

    Attributes:
        decision_type: Type of decision
        deadline_hours: Hours until deadline
        default_action: Default action if no response
        can_extend: Whether extension is allowed
        max_extension_hours: Maximum extension hours
    """

    decision_type: DecisionType
    deadline_hours: int
    default_action: str
    can_extend: bool = True
    max_extension_hours: int = 0

    def calculate_deadline(
        self, from_time: datetime | None = None
    ) -> datetime:
        """
        Calculate deadline from a given time.

        Args:
            from_time: Start time (defaults to now)

        Returns:
            Deadline datetime
        """
        start = from_time or datetime.now()
        return start + timedelta(hours=self.deadline_hours)

    def calculate_extended_deadline(
        self, original_deadline: datetime
    ) -> datetime:
        """
        Calculate extended deadline.

        Args:
            original_deadline: Original deadline

        Returns:
            Extended deadline datetime
        """
        if not self.can_extend:
            return original_deadline
        return original_deadline + timedelta(hours=self.max_extension_hours)


class StandardDeadlines:
    """
    Standard deadline configurations.

    Provides pre-configured deadlines for common decision types.
    """

    @staticmethod
    def weekly_packet() -> DeadlinePolicy:
        """Weekly decision packet deadline (Tuesday 18:00 UTC)."""
        return DeadlinePolicy(
            decision_type=DecisionType.WEEKLY_PACKET,
            deadline_hours=32,  # Monday 09:30 to Tuesday 18:00
            default_action="Apply recommended defaults",
            can_extend=True,
            max_extension_hours=24,
        )

    @staticmethod
    def mid_week_s1() -> DeadlinePolicy:
        """Mid-week S1 incident deadline."""
        return DeadlinePolicy(
            decision_type=DecisionType.MID_WEEK_S1,
            deadline_hours=4,
            default_action="Apply safest option: hold pipeline",
            can_extend=True,
            max_extension_hours=4,
        )

    @staticmethod
    def mid_week_s2() -> DeadlinePolicy:
        """Mid-week S2 incident deadline."""
        return DeadlinePolicy(
            decision_type=DecisionType.MID_WEEK_S2,
            deadline_hours=8,
            default_action="Apply recommended recovery action",
            can_extend=True,
            max_extension_hours=8,
        )

    @staticmethod
    def gate_transition() -> DeadlinePolicy:
        """Gate transition deadline."""
        return DeadlinePolicy(
            decision_type=DecisionType.GATE_TRANSITION,
            deadline_hours=48,
            default_action="Proceed with generated plan",
            can_extend=True,
            max_extension_hours=48,
        )

    @staticmethod
    def budget_amendment() -> DeadlinePolicy:
        """Budget amendment deadline."""
        return DeadlinePolicy(
            decision_type=DecisionType.BUDGET_AMENDMENT,
            deadline_hours=32,
            default_action="Hold at current tier",
            can_extend=False,
        )

    @staticmethod
    def get_policy(decision_type: DecisionType) -> DeadlinePolicy:
        """
        Get deadline policy for a decision type.

        Args:
            decision_type: Type of decision

        Returns:
            DeadlinePolicy
        """
        policies = {
            DecisionType.WEEKLY_PACKET: StandardDeadlines.weekly_packet(),
            DecisionType.MID_WEEK_S1: StandardDeadlines.mid_week_s1(),
            DecisionType.MID_WEEK_S2: StandardDeadlines.mid_week_s2(),
            DecisionType.GATE_TRANSITION: StandardDeadlines.gate_transition(),
            DecisionType.BUDGET_AMENDMENT: StandardDeadlines.budget_amendment(),
        }
        return policies.get(
            decision_type,
            StandardDeadlines.weekly_packet(),
        )

    @staticmethod
    def is_t3_decision(decision_type: DecisionType) -> bool:
        """
        Check if decision requires T3 (human approval).

        Args:
            decision_type: Type of decision

        Returns:
            True if T3 required
        """
        # G3->Pilot and G4->Production are T3 with no default
        return decision_type in (
            DecisionType.GATE_TRANSITION,
            DecisionType.BUDGET_AMENDMENT,
        )
