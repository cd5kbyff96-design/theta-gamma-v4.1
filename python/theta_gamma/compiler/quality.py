"""
Quality Rubric — Packet quality assessment.

This module implements the quality rubric for assessing task packets
before execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from theta_gamma.compiler.packets import TaskPacket, PacketPriority


class QualityTier(str, Enum):
    """
    Quality tiers for packets.

    Determines readiness for execution.
    """

    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    REJECT = "reject"


class CompletenessCriterion(str, Enum):
    """
    Mandatory completeness criteria.

    All must pass for a packet to be accepted.
    """

    OBJECTIVE_PRESENT = "objective_present"
    INPUTS_LISTED = "inputs_listed"
    COMMANDS_SPECIFIED = "commands_specified"
    TESTS_DEFINED = "tests_defined"
    DONE_DEFINITION_PRESENT = "done_definition_present"
    STOP_CONDITION_PRESENT = "stop_condition_present"
    ROLLBACK_COMMAND_EXISTS = "rollback_command_exists"


@dataclass
class QualityScore:
    """
    Quality score for a packet.

    Attributes:
        completeness_passed: Whether all mandatory criteria pass
        specificity_score: Score 1-3 for specificity
        isolation_score: Score 1-3 for isolation
        reversibility_score: Score 1-3 for reversibility
        testability_score: Score 1-3 for testability
    """

    completeness_passed: bool
    specificity_score: int = 1
    isolation_score: int = 1
    reversibility_score: int = 1
    testability_score: int = 1

    @property
    def tier(self) -> QualityTier:
        """Calculate quality tier from scores."""
        if not self.completeness_passed:
            return QualityTier.REJECT

        min_score = min(
            self.specificity_score,
            self.isolation_score,
            self.reversibility_score,
            self.testability_score,
        )

        if min_score == 3:
            return QualityTier.GOLD
        elif min_score >= 2:
            return QualityTier.SILVER
        else:
            return QualityTier.BRONZE

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "completeness_passed": self.completeness_passed,
            "specificity_score": self.specificity_score,
            "isolation_score": self.isolation_score,
            "reversibility_score": self.reversibility_score,
            "testability_score": self.testability_score,
            "tier": self.tier.value,
        }


class QualityRubric:
    """
    Quality rubric for packet assessment.

    Assesses packets against completeness criteria and quality dimensions.

    Example:
        >>> rubric = QualityRubric()
        >>> score = rubric.assess(packet)
        >>> if score.tier == QualityTier.REJECT:
        ...     revise_packet(packet)
    """

    def __init__(self) -> None:
        """Initialize the quality rubric."""
        self._completeness_criteria = list(CompletenessCriterion)

    def assess(self, packet: TaskPacket) -> QualityScore:
        """
        Assess a packet's quality.

        Args:
            packet: Packet to assess

        Returns:
            QualityScore
        """
        completeness_passed = self._check_completeness(packet)
        specificity = self._assess_specificity(packet)
        isolation = self._assess_isolation(packet)
        reversibility = self._assess_reversibility(packet)
        testability = self._assess_testability(packet)

        return QualityScore(
            completeness_passed=completeness_passed,
            specificity_score=specificity,
            isolation_score=isolation,
            reversibility_score=reversibility,
            testability_score=testability,
        )

    def _check_completeness(self, packet: TaskPacket) -> bool:
        """Check all mandatory completeness criteria."""
        checks = {
            CompletenessCriterion.OBJECTIVE_PRESENT: bool(packet.objective),
            CompletenessCriterion.INPUTS_LISTED: len(packet.inputs) > 0,
            CompletenessCriterion.COMMANDS_SPECIFIED: len(packet.commands) > 0,
            CompletenessCriterion.TESTS_DEFINED: len(packet.tests) > 0,
            CompletenessCriterion.DONE_DEFINITION_PRESENT: bool(packet.done_definition),
            CompletenessCriterion.STOP_CONDITION_PRESENT: bool(packet.stop_condition),
        }
        return all(checks.values())

    def _assess_specificity(self, packet: TaskPacket) -> int:
        """Assess specificity (1-3)."""
        score = 1

        # Check if commands are executable as-is
        if packet.commands:
            # Check for concrete values vs placeholders
            concrete_commands = sum(
                1 for cmd in packet.commands if not cmd.startswith("Implement")
            )
            if concrete_commands >= len(packet.commands) * 0.8:
                score = 3
            elif concrete_commands >= len(packet.commands) * 0.5:
                score = 2

        return score

    def _assess_isolation(self, packet: TaskPacket) -> int:
        """Assess isolation (1-3)."""
        # Fully isolated if no dependencies or all deps are complete
        if not packet.depends_on:
            return 3

        # Loosely coupled if few dependencies
        if len(packet.depends_on) <= 2:
            return 2

        return 1

    def _assess_reversibility(self, packet: TaskPacket) -> int:
        """Assess reversibility (1-3)."""
        # Check for rollback/undo capability
        if packet.stop_condition and "revert" in packet.stop_condition.lower():
            return 3

        if packet.stop_condition:
            return 2

        return 1

    def _assess_testability(self, packet: TaskPacket) -> int:
        """Assess testability (1-3)."""
        if not packet.tests:
            return 1

        # Check if tests are automated
        automated_tests = sum(
            1 for t in packet.tests if "python" in t.command.lower() or "bash" in t.command.lower()
        )

        if automated_tests == len(packet.tests):
            return 3
        elif automated_tests > 0:
            return 2

        return 1

    def get_minimum_requirements(self, priority: PacketPriority) -> dict[str, int]:
        """
        Get minimum score requirements for a priority level.

        Args:
            priority: Packet priority

        Returns:
            Dictionary of minimum scores
        """
        requirements = {
            PacketPriority.P0_CRITICAL: {
                "specificity": 2,
                "isolation": 2,
                "reversibility": 2,
                "testability": 2,
            },
            PacketPriority.P1_HIGH: {
                "specificity": 1,
                "isolation": 2,
                "reversibility": 2,
                "testability": 1,
            },
            PacketPriority.P2_MEDIUM: {
                "specificity": 1,
                "isolation": 2,
                "reversibility": 1,
                "testability": 1,
            },
            PacketPriority.P3_LOW: {
                "specificity": 1,
                "isolation": 2,
                "reversibility": 1,
                "testability": 1,
            },
        }
        return requirements.get(priority, requirements[PacketPriority.P3_LOW])

    def meets_requirements(
        self, score: QualityScore, priority: PacketPriority
    ) -> tuple[bool, list[str]]:
        """
        Check if a score meets requirements for a priority level.

        Args:
            score: Quality score
            priority: Packet priority

        Returns:
            Tuple of (meets_requirements, list of unmet requirements)
        """
        if not score.completeness_passed:
            return (False, ["Completeness criteria not met"])

        mins = self.get_minimum_requirements(priority)
        unmet = []

        if score.specificity_score < mins["specificity"]:
            unmet.append(
                f"Specificity {score.specificity_score} < {mins['specificity']}"
            )
        if score.isolation_score < mins["isolation"]:
            unmet.append(f"Isolation {score.isolation_score} < {mins['isolation']}")
        if score.reversibility_score < mins["reversibility"]:
            unmet.append(
                f"Reversibility {score.reversibility_score} < {mins['reversibility']}"
            )
        if score.testability_score < mins["testability"]:
            unmet.append(f"Testability {score.testability_score} < {mins['testability']}")

        return (len(unmet) == 0, unmet)

    def assess_all(
        self, packets: list[TaskPacket]
    ) -> dict[str, QualityScore]:
        """
        Assess quality of multiple packets.

        Args:
            packets: List of packets

        Returns:
            Dictionary mapping packet ID to QualityScore
        """
        return {p.packet_id: self.assess(p) for p in packets}

    def get_quality_summary(
        self, packets: list[TaskPacket]
    ) -> dict[str, Any]:
        """
        Get quality summary for a set of packets.

        Args:
            packets: List of packets

        Returns:
            Summary dictionary
        """
        scores = self.assess_all(packets)

        tier_counts = {tier.value: 0 for tier in QualityTier}
        for score in scores.values():
            tier_counts[score.tier.value] += 1

        return {
            "total_packets": len(packets),
            "tier_counts": tier_counts,
            "gold_pct": (tier_counts["gold"] / len(packets)) * 100 if packets else 0,
            "reject_pct": (tier_counts["reject"] / len(packets)) * 100 if packets else 0,
            "average_scores": {
                "specificity": sum(s.specificity_score for s in scores.values())
                / len(scores)
                if scores
                else 0,
                "isolation": sum(s.isolation_score for s in scores.values())
                / len(scores)
                if scores
                else 0,
                "reversibility": sum(s.reversibility_score for s in scores.values())
                / len(scores)
                if scores
                else 0,
                "testability": sum(s.testability_score for s in scores.values())
                / len(scores)
                if scores
                else 0,
            },
        }
