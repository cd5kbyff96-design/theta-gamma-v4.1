"""
Auto-Prioritization Rules — Deterministic packet backlog ranking.

This module implements the auto-prioritization rules that score and
rank packets for weekly execution planning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from theta_gamma.compiler.packets import TaskPacket, PacketPriority


@dataclass
class PrioritizationWeights:
    """
    Weights for prioritization scoring.

    Attributes:
        gate_blocking: Weight for gate-blocking score
        deadline_pressure: Weight for deadline pressure score
        dependency_readiness: Weight for dependency readiness score
        priority: Weight for original priority score
        cost_efficiency: Weight for cost efficiency score
        risk_reduction: Weight for risk reduction score
    """

    gate_blocking: float = 0.30
    deadline_pressure: float = 0.20
    dependency_readiness: float = 0.20
    priority: float = 0.15
    cost_efficiency: float = 0.10
    risk_reduction: float = 0.05

    def validate(self) -> bool:
        """Validate weights sum to 1.0."""
        total = (
            self.gate_blocking
            + self.deadline_pressure
            + self.dependency_readiness
            + self.priority
            + self.cost_efficiency
            + self.risk_reduction
        )
        return abs(total - 1.0) < 0.01


@dataclass
class PrioritizationScore:
    """
    Prioritization score for a packet.

    Attributes:
        packet_id: Packet identifier
        composite_score: Overall composite score
        gate_blocking_score: Score for gate-blocking
        deadline_pressure_score: Score for deadline pressure
        dependency_readiness_score: Score for dependency readiness
        priority_score: Score for priority
        cost_efficiency_score: Score for cost efficiency
        risk_reduction_score: Score for risk reduction
        rationale: Human-readable rationale
    """

    packet_id: str
    composite_score: float
    gate_blocking_score: float = 0.0
    deadline_pressure_score: float = 0.0
    dependency_readiness_score: float = 0.0
    priority_score: float = 0.0
    cost_efficiency_score: float = 0.0
    risk_reduction_score: float = 0.0
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "packet_id": self.packet_id,
            "composite_score": self.composite_score,
            "gate_blocking_score": self.gate_blocking_score,
            "deadline_pressure_score": self.deadline_pressure_score,
            "dependency_readiness_score": self.dependency_readiness_score,
            "priority_score": self.priority_score,
            "cost_efficiency_score": self.cost_efficiency_score,
            "risk_reduction_score": self.risk_reduction_score,
            "rationale": self.rationale,
        }


class AutoPrioritization:
    """
    Auto-prioritization engine for packet backlog.

    Scores and ranks packets using weighted scoring formula.

    Example:
        >>> prioritization = AutoPrioritization()
        >>> scores = prioritization.score_packets(packets)
        >>> top_5 = prioritization.select_top_packets(scores, n=5)
    """

    def __init__(self, weights: PrioritizationWeights | None = None) -> None:
        """
        Initialize auto-prioritization.

        Args:
            weights: Prioritization weights
        """
        self.weights = weights or PrioritizationWeights()
        self._completed_packets: set[str] = set()
        self._open_incidents: list[dict[str, Any]] = []

    def set_completed_packets(self, packet_ids: set[str]) -> None:
        """Set of completed packet IDs."""
        self._completed_packets = packet_ids

    def set_open_incidents(self, incidents: list[dict[str, Any]]) -> None:
        """Set open incidents for risk scoring."""
        self._open_incidents = incidents

    def score_packet(
        self,
        packet: TaskPacket,
        gate_context: dict[str, Any] | None = None,
        deadline_context: dict[str, Any] | None = None,
        cost_context: dict[str, Any] | None = None,
    ) -> PrioritizationScore:
        """
        Score a single packet.

        Args:
            packet: Packet to score
            gate_context: Gate context for scoring
            deadline_context: Deadline context
            cost_context: Cost context

        Returns:
            PrioritizationScore
        """
        gate_score = self._score_gate_blocking(packet, gate_context or {})
        deadline_score = self._score_deadline_pressure(packet, deadline_context or {})
        dependency_score = self._score_dependency_readiness(packet)
        priority_score = self._score_priority(packet)
        cost_score = self._score_cost_efficiency(packet, cost_context or {})
        risk_score = self._score_risk_reduction(packet)

        composite = (
            self.weights.gate_blocking * gate_score
            + self.weights.deadline_pressure * deadline_score
            + self.weights.dependency_readiness * dependency_score
            + self.weights.priority * priority_score
            + self.weights.cost_efficiency * cost_score
            + self.weights.risk_reduction * risk_score
        )

        rationale = self._generate_rationale(
            packet, gate_score, deadline_score, dependency_score
        )

        return PrioritizationScore(
            packet_id=packet.packet_id,
            composite_score=composite,
            gate_blocking_score=gate_score,
            deadline_pressure_score=deadline_score,
            dependency_readiness_score=dependency_score,
            priority_score=priority_score,
            cost_efficiency_score=cost_score,
            risk_reduction_score=risk_score,
            rationale=rationale,
        )

    def _score_gate_blocking(
        self, packet: TaskPacket, context: dict[str, Any]
    ) -> float:
        """Score gate-blocking (0-100)."""
        # Check if packet blocks current gate
        if context.get("blocks_current_gate"):
            return 100.0
        if context.get("blocks_next_gate"):
            return 75.0
        if context.get("supports_current_gate"):
            return 50.0
        if context.get("supports_future_gate"):
            return 25.0
        return 10.0

    def _score_deadline_pressure(
        self, packet: TaskPacket, context: dict[str, Any]
    ) -> float:
        """Score deadline pressure (0-100)."""
        days_until_deadline = context.get("days_until_deadline", 30)

        if days_until_deadline < 0:
            return 100.0  # Overdue
        elif days_until_deadline <= 3:
            return 80.0
        elif days_until_deadline <= 7:
            return 60.0
        elif days_until_deadline <= 14:
            return 40.0
        elif days_until_deadline <= 30:
            return 20.0
        return 5.0

    def _score_dependency_readiness(self, packet: TaskPacket) -> float:
        """Score dependency readiness (0-100)."""
        if not packet.depends_on:
            return 100.0

        ready_deps = sum(
            1 for dep in packet.depends_on if dep in self._completed_packets
        )
        return (ready_deps / len(packet.depends_on)) * 100

    def _score_priority(self, packet: TaskPacket) -> float:
        """Score priority (0-100)."""
        priority_scores = {
            PacketPriority.P0_CRITICAL: 100.0,
            PacketPriority.P1_HIGH: 70.0,
            PacketPriority.P2_MEDIUM: 40.0,
            PacketPriority.P3_LOW: 10.0,
        }
        return priority_scores.get(packet.priority, 10.0)

    def _score_cost_efficiency(
        self, packet: TaskPacket, context: dict[str, Any]
    ) -> float:
        """Score cost efficiency (0-100)."""
        estimated_cost = context.get("estimated_cost_usd", 25.0)

        if estimated_cost <= 10:
            return 100.0
        elif estimated_cost <= 25:
            return 75.0
        elif estimated_cost <= 50:
            return 50.0
        return 25.0

    def _score_risk_reduction(self, packet: TaskPacket) -> float:
        """Score risk reduction (0-100)."""
        # Check if packet resolves open incidents
        for incident in self._open_incidents:
            if packet.packet_id in incident.get("resolution_packets", []):
                if incident.get("severity") == "S1":
                    return 100.0
                elif incident.get("severity") == "S2":
                    return 75.0

        # Check if packet implements safety controls
        if packet.domain.value in ("SAFETY", "BUDGET"):
            return 60.0

        return 0.0

    def _generate_rationale(
        self,
        packet: TaskPacket,
        gate_score: float,
        deadline_score: float,
        dependency_score: float,
    ) -> str:
        """Generate human-readable rationale."""
        parts = []

        if gate_score >= 75:
            parts.append("Critical path")
        if dependency_score == 100:
            parts.append("all deps met")
        if packet.priority == PacketPriority.P0_CRITICAL:
            parts.append("P0")

        return ", ".join(parts) if parts else "Standard priority"

    def score_packets(
        self,
        packets: list[TaskPacket],
        gate_context: dict[str, Any] | None = None,
    ) -> list[PrioritizationScore]:
        """
        Score multiple packets.

        Args:
            packets: Packets to score
            gate_context: Gate context

        Returns:
            List of PrioritizationScore sorted by composite score
        """
        scores = [
            self.score_packet(p, gate_context or {})
            for p in packets
            if p.status.value == "pending"
        ]
        return sorted(scores, key=lambda s: s.composite_score, reverse=True)

    def select_top_packets(
        self,
        scores: list[PrioritizationScore],
        n: int = 5,
        budget_constraint: float | None = None,
    ) -> list[PrioritizationScore]:
        """
        Select top N packets with optional budget constraint.

        Args:
            scores: Scored packets
            n: Number to select
            budget_constraint: Optional budget constraint

        Returns:
            Selected top packets
        """
        selected = []
        total_cost = 0.0

        for score in scores:
            if len(selected) >= n:
                break

            # Check budget constraint if provided
            if budget_constraint:
                packet_cost = 25.0  # Would get from context
                if total_cost + packet_cost > budget_constraint:
                    continue

            selected.append(score)
            total_cost += 25.0

        return selected

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "weights": {
                "gate_blocking": self.weights.gate_blocking,
                "deadline_pressure": self.weights.deadline_pressure,
                "dependency_readiness": self.weights.dependency_readiness,
                "priority": self.weights.priority,
                "cost_efficiency": self.weights.cost_efficiency,
                "risk_reduction": self.weights.risk_reduction,
            },
            "completed_packets_count": len(self._completed_packets),
            "open_incidents_count": len(self._open_incidents),
        }
