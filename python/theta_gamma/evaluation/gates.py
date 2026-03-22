"""
Gate Definitions and Evaluation — Milestone gates for pipeline progression.

This module implements the gate system that controls progression through
training milestones (G1-G4) with metric thresholds, statistical confidence
requirements, and rollback mechanisms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from theta_gamma.evaluation.metrics import Metric, MetricDictionary


class GateStatus(str, Enum):
    """
    Gate status indicating progression state.

    Gates progress through these states as criteria are evaluated.
    """

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"  # Waiting on dependency gate


class RollbackTrigger(str, Enum):
    """Triggers for gate rollback."""

    TWO_CONSECUTIVE_FAILURES = "two_consecutive_failures"
    THREE_CONSECUTIVE_FAILURES = "three_consecutive_failures"
    MANUAL = "manual"


@dataclass
class StatisticalConfidence:
    """
    Statistical confidence requirements for gate evaluation.

    Attributes:
        confidence_level: Confidence level (e.g., 0.95 for 95%)
        test_type: Type of statistical test
        min_samples: Minimum samples required
        max_stddev: Maximum allowed standard deviation
    """

    confidence_level: float = 0.95
    test_type: str = "one_sided_t_test"
    min_samples: int = 3
    max_stddev: float | None = None

    def meets_confidence(
        self, values: list[float], threshold: float, higher_is_better: bool = True
    ) -> tuple[bool, str]:
        """
        Check if values meet threshold with statistical confidence.

        Args:
            values: List of metric values
            threshold: Threshold to compare against
            higher_is_better: Whether higher values are better

        Returns:
            Tuple of (meets_confidence, message)
        """
        import statistics

        if len(values) < self.min_samples:
            return (
                False,
                f"Insufficient samples: {len(values)} < {self.min_samples}",
            )

        mean = statistics.mean(values)
        stddev = statistics.stdev(values) if len(values) > 1 else 0.0

        # Check stddev constraint if defined
        if self.max_stddev is not None and stddev > self.max_stddev:
            return (
                False,
                f"Standard deviation {stddev:.4f} exceeds max {self.max_stddev}",
            )

        # Simple t-test approximation
        if higher_is_better:
            meets = mean >= threshold
            direction = ">="
        else:
            meets = mean <= threshold
            direction = "<="

        return (
            meets,
            f"Mean {mean:.4f} {direction} {threshold} (stddev={stddev:.4f}, n={len(values)})",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "confidence_level": self.confidence_level,
            "test_type": self.test_type,
            "min_samples": self.min_samples,
            "max_stddev": self.max_stddev,
        }


@dataclass
class GateCriterion:
    """
    A single criterion within a gate.

    Attributes:
        metric_id: Reference to metric in dictionary
        operator: Comparison operator (>=, <=, ==, etc.)
        threshold: Threshold value
        window: Evaluation window specification
        pass_rule: Description of pass condition
        fail_rule: Description of fail condition
    """

    metric_id: str
    operator: str
    threshold: float
    window: dict[str, Any]
    pass_rule: str
    fail_rule: str
    floor_guard: float | None = None  # Per-run floor guard
    spike_guard: float | None = None  # Per-run spike guard

    def evaluate(
        self,
        values: list[float],
        metric: Metric,
        confidence: StatisticalConfidence | None = None,
    ) -> tuple[bool, str]:
        """
        Evaluate the criterion against metric values.

        Args:
            values: List of metric values in the window
            metric: The metric definition
            confidence: Optional statistical confidence requirements

        Returns:
            Tuple of (passes, message)
        """
        if not values:
            return (False, "No values to evaluate")

        # Check floor guard (per-run)
        if self.floor_guard is not None:
            if metric.higher_is_better:
                min_value = min(values)
                if min_value < self.floor_guard:
                    return (
                        False,
                        f"Floor guard violated: min {min_value} < {self.floor_guard}",
                    )
            else:
                max_value = max(values)
                if max_value > self.floor_guard:
                    return (
                        False,
                        f"Floor guard violated: max {max_value} > {self.floor_guard}",
                    )

        # Check spike guard (per-run)
        if self.spike_guard is not None and len(values) >= 2:
            latest = values[-1]
            previous = values[-2]
            delta = abs(latest - previous)
            if delta > self.spike_guard:
                return (
                    False,
                    f"Spike guard violated: delta {delta} > {self.spike_guard}",
                )

        # Apply statistical confidence if specified
        if confidence:
            return confidence.meets_confidence(
                values, self.threshold, metric.higher_is_better
            )

        # Simple threshold comparison
        mean_value = sum(values) / len(values)

        if self.operator == ">=":
            passes = mean_value >= self.threshold
            comparison = ">="
        elif self.operator == "<=":
            passes = mean_value <= self.threshold
            comparison = "<="
        elif self.operator == ">":
            passes = mean_value > self.threshold
            comparison = ">"
        elif self.operator == "<":
            passes = mean_value < self.threshold
            comparison = "<"
        elif self.operator == "==":
            passes = abs(mean_value - self.threshold) < 0.001
            comparison = "=="
        else:
            passes = False
            comparison = self.operator

        return (
            passes,
            f"{mean_value:.4f} {comparison} {self.threshold}: {'PASS' if passes else 'FAIL'}",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metric_id": self.metric_id,
            "operator": self.operator,
            "threshold": self.threshold,
            "window": self.window,
            "pass_rule": self.pass_rule,
            "fail_rule": self.fail_rule,
            "floor_guard": self.floor_guard,
            "spike_guard": self.spike_guard,
        }


@dataclass
class RollbackAction:
    """
    Rollback action configuration.

    Attributes:
        trigger: What triggers the rollback
        actions: List of actions to take
    """

    trigger: RollbackTrigger
    actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trigger": self.trigger.value,
            "actions": self.actions,
        }


class Gate(BaseModel):
    """
    A milestone gate for pipeline progression.

    Gates define criteria that must be met to progress to the next
    phase of training or deployment.

    Attributes:
        id: Gate identifier (G1, G2, G3, G4)
        name: Human-readable name
        description: Detailed description
        phase: Training phase this gate belongs to
        criteria: List of criteria that must all pass
        statistical_confidence: Confidence requirements
        rollback: Rollback configuration
        dependencies: Gates that must pass before this gate
    """

    id: str = Field(..., description="Gate identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Detailed description")
    phase: str = Field(..., description="Training phase")
    criteria: list[GateCriterion] = Field(default_factory=list)
    statistical_confidence: StatisticalConfidence = Field(
        default_factory=StatisticalConfidence
    )
    rollback: RollbackAction | None = None
    dependencies: list[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    def get_required_metrics(self) -> list[str]:
        """Get list of required metric IDs for this gate."""
        return [c.metric_id for c in self.criteria]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "phase": self.phase,
            "criteria": [c.to_dict() for c in self.criteria],
            "statistical_confidence": self.statistical_confidence.to_dict(),
            "rollback": self.rollback.to_dict() if self.rollback else None,
            "dependencies": self.dependencies,
        }


@dataclass
class CriterionResult:
    """
    Result of evaluating a single criterion.

    Attributes:
        criterion: The criterion that was evaluated
        metric_name: Name of the metric
        values: Values used in evaluation
        threshold: Threshold that was compared
        passed: Whether the criterion passed
        message: Evaluation message
    """

    criterion: GateCriterion
    metric_name: str
    values: list[float]
    threshold: float
    passed: bool
    message: str


@dataclass
class GateResult:
    """
    Result of evaluating a gate.

    Attributes:
        gate_id: Gate that was evaluated
        status: Pass/fail status
        evaluated_at: Evaluation timestamp
        criterion_results: Results for each criterion
        all_passed: Whether all criteria passed
        message: Summary message
        consecutive_failures: Count of consecutive failures
    """

    gate_id: str
    status: GateStatus
    evaluated_at: datetime
    criterion_results: list[CriterionResult]
    all_passed: bool
    message: str
    consecutive_failures: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "gate_id": self.gate_id,
            "status": self.status.value,
            "evaluated_at": self.evaluated_at.isoformat(),
            "criterion_results": [
                {
                    "metric_name": cr.metric_name,
                    "passed": cr.passed,
                    "message": cr.message,
                }
                for cr in self.criterion_results
            ],
            "all_passed": self.all_passed,
            "message": self.message,
            "consecutive_failures": self.consecutive_failures,
        }


class GateEvaluator:
    """
    Evaluator for milestone gates.

    The evaluator checks gate criteria against metric values,
    tracks consecutive failures, and determines rollback triggers.

    Example:
        >>> evaluator = GateEvaluator()
        >>> result = evaluator.evaluate_gate("G1", metrics={"M-CM-001": [0.45, 0.42, 0.48]})
        >>> if result.all_passed:
        ...     proceed_to_next_phase()
    """

    def __init__(
        self,
        metric_dictionary: MetricDictionary | None = None,
        gates: list[Gate] | None = None,
    ) -> None:
        """
        Initialize the gate evaluator.

        Args:
            metric_dictionary: Dictionary of metric definitions
            gates: List of gate definitions
        """
        self._metrics = metric_dictionary or MetricDictionary()
        self._gates: dict[str, Gate] = {}
        self._failure_counts: dict[str, int] = {}
        self._pass_history: dict[str, list[datetime]] = {}

        if gates:
            for gate in gates:
                self._gates[gate.id] = gate
        else:
            self._initialize_default_gates()

    def _initialize_default_gates(self) -> None:
        """Initialize default gates from the specification."""
        gates = [
            # G1: Baseline Readiness
            Gate(
                id="G1",
                name="Baseline Readiness",
                description="Initial baseline cross-modal performance",
                phase="baseline",
                criteria=[
                    GateCriterion(
                        metric_id="M-CM-001",
                        operator=">=",
                        threshold=40.0,
                        window={"type": "rolling", "size": 3, "size_unit": "eval_runs"},
                        pass_rule="Cross-modal accuracy >= 40% over 3 eval runs",
                        fail_rule="Cross-modal accuracy < 40%",
                        floor_guard=35.0,
                    ),
                    GateCriterion(
                        metric_id="M-MQ-002",
                        operator="<=",
                        threshold=2.0,
                        window={"type": "rolling", "size": 3, "size_unit": "epochs"},
                        pass_rule="Validation loss <= 2.0 over 3 epochs",
                        fail_rule="Validation loss > 2.0",
                    ),
                    GateCriterion(
                        metric_id="M-CM-003",
                        operator=">=",
                        threshold=25.0,
                        window={"type": "latest", "size": 1},
                        pass_rule="Cross-modal consistency >= 25%",
                        fail_rule="Cross-modal consistency < 25%",
                    ),
                ],
                statistical_confidence=StatisticalConfidence(
                    confidence_level=0.95, min_samples=3
                ),
                rollback=RollbackAction(
                    trigger=RollbackTrigger.TWO_CONSECUTIVE_FAILURES,
                    actions=[
                        "Revert to last stable checkpoint",
                        "Hyperparameter review",
                    ],
                ),
                dependencies=[],
            ),
            # G2: Mid Training
            Gate(
                id="G2",
                name="Mid Training",
                description="Mid-training cross-modal performance with modality balance",
                phase="mid_training",
                criteria=[
                    GateCriterion(
                        metric_id="M-CM-001",
                        operator=">=",
                        threshold=60.0,
                        window={"type": "rolling", "size": 3, "size_unit": "eval_runs"},
                        pass_rule="Cross-modal accuracy >= 60%",
                        fail_rule="Cross-modal accuracy < 60%",
                        floor_guard=55.0,
                    ),
                    GateCriterion(
                        metric_id="M-MOD-004",
                        operator="<=",
                        threshold=20.0,
                        window={"type": "latest", "size": 1},
                        pass_rule="Max modality gap <= 20pp",
                        fail_rule="Max modality gap > 20pp",
                    ),
                    GateCriterion(
                        metric_id="M-CM-002",
                        operator=">=",
                        threshold=0.55,
                        window={"type": "rolling", "size": 3},
                        pass_rule="Cross-modal F1 >= 0.55",
                        fail_rule="Cross-modal F1 < 0.55",
                    ),
                    GateCriterion(
                        metric_id="M-ROB-001",
                        operator=">=",
                        threshold=25.0,
                        window={"type": "latest", "size": 1},
                        pass_rule="Adversarial robustness >= 25%",
                        fail_rule="Adversarial robustness < 25%",
                    ),
                    GateCriterion(
                        metric_id="M-ROB-002",
                        operator=">=",
                        threshold=0.70,
                        window={"type": "latest", "size": 1},
                        pass_rule="OOD AUROC >= 0.70",
                        fail_rule="OOD AUROC < 0.70",
                    ),
                ],
                statistical_confidence=StatisticalConfidence(
                    confidence_level=0.95, min_samples=3
                ),
                rollback=RollbackAction(
                    trigger=RollbackTrigger.TWO_CONSECUTIVE_FAILURES,
                    actions=[
                        "Revert to best G1 checkpoint",
                        "Modality balance diagnostic",
                    ],
                ),
                dependencies=["G1"],
            ),
            # G3: Pilot Readiness
            Gate(
                id="G3",
                name="Pilot Readiness",
                description="Pilot-ready performance with safety checks",
                phase="pilot_readiness",
                criteria=[
                    GateCriterion(
                        metric_id="M-CM-001",
                        operator=">=",
                        threshold=70.0,
                        window={"type": "rolling", "size": 5, "size_unit": "eval_runs"},
                        pass_rule="Cross-modal accuracy >= 70% over 5 eval runs",
                        fail_rule="Cross-modal accuracy < 70%",
                        floor_guard=65.0,
                        spike_guard=5.0,
                    ),
                    GateCriterion(
                        metric_id="M-CM-004",
                        operator=">=",
                        threshold=50.0,
                        window={"type": "latest", "size": 1},
                        pass_rule="Retrieval Recall@10 >= 50%",
                        fail_rule="Retrieval Recall@10 < 50%",
                    ),
                    GateCriterion(
                        metric_id="M-ROB-003",
                        operator="<=",
                        threshold=0.05,
                        window={"type": "latest", "size": 1},
                        pass_rule="Calibration ECE <= 0.05",
                        fail_rule="Calibration ECE > 0.05",
                    ),
                    GateCriterion(
                        metric_id="M-SAF-001",
                        operator="<=",
                        threshold=0.001,
                        window={"type": "latest", "size": 1},
                        pass_rule="Safety violation rate <= 0.1%",
                        fail_rule="Safety violation rate > 0.1%",
                    ),
                    GateCriterion(
                        metric_id="M-MOD-004",
                        operator="<=",
                        threshold=15.0,
                        window={"type": "rolling", "size": 3},
                        pass_rule="Max modality gap <= 15pp",
                        fail_rule="Max modality gap > 15pp",
                    ),
                    GateCriterion(
                        metric_id="M-CM-003",
                        operator=">=",
                        threshold=60.0,
                        window={"type": "rolling", "size": 3},
                        pass_rule="Cross-modal consistency >= 60%",
                        fail_rule="Cross-modal consistency < 60%",
                    ),
                    GateCriterion(
                        metric_id="M-ROB-001",
                        operator=">=",
                        threshold=30.0,
                        window={"type": "latest", "size": 1},
                        pass_rule="Adversarial robustness >= 30%",
                        fail_rule="Adversarial robustness < 30%",
                    ),
                    GateCriterion(
                        metric_id="M-ROB-002",
                        operator=">=",
                        threshold=0.75,
                        window={"type": "latest", "size": 1},
                        pass_rule="OOD AUROC >= 0.75",
                        fail_rule="OOD AUROC < 0.75",
                    ),
                    GateCriterion(
                        metric_id="M-CM-001",
                        operator=">=",
                        threshold=3.0,
                        window={"type": "stddev", "size": 5},
                        pass_rule="Accuracy stddev <= 3pp over 5 runs",
                        fail_rule="Accuracy stddev > 3pp",
                    ),
                ],
                statistical_confidence=StatisticalConfidence(
                    confidence_level=0.95, min_samples=5, max_stddev=0.03
                ),
                rollback=RollbackAction(
                    trigger=RollbackTrigger.TWO_CONSECUTIVE_FAILURES,
                    actions=[
                        "Revert to best G2 checkpoint",
                        "Full diagnostic suite",
                        "Architecture review meeting",
                    ],
                ),
                dependencies=["G2"],
            ),
            # G4: Latency/Performance (independent of G1-G3)
            Gate(
                id="G4",
                name="Latency & Performance",
                description="Production-ready latency and throughput",
                phase="performance",
                criteria=[
                    GateCriterion(
                        metric_id="M-LAT-002",
                        operator="<=",
                        threshold=100.0,
                        window={"type": "latest", "size": 1},
                        pass_rule="p95 latency <= 100ms",
                        fail_rule="p95 latency > 100ms",
                        spike_guard=120.0,
                    ),
                    GateCriterion(
                        metric_id="M-THR-001",
                        operator=">=",
                        threshold=100.0,
                        window={"type": "latest", "size": 1},
                        pass_rule="Throughput >= 100 QPS",
                        fail_rule="Throughput < 100 QPS",
                    ),
                    GateCriterion(
                        metric_id="M-RES-001",
                        operator="<=",
                        threshold=70.0,
                        window={"type": "latest", "size": 1},
                        pass_rule="Peak GPU memory <= 70GB",
                        fail_rule="Peak GPU memory > 70GB",
                    ),
                    GateCriterion(
                        metric_id="M-LAT-001",
                        operator="<=",
                        threshold=50.0,
                        window={"type": "latest", "size": 1},
                        pass_rule="p50 latency <= 50ms",
                        fail_rule="p50 latency > 50ms",
                    ),
                    GateCriterion(
                        metric_id="M-LAT-003",
                        operator="<=",
                        threshold=150.0,
                        window={"type": "latest", "size": 1},
                        pass_rule="p99 latency <= 150ms",
                        fail_rule="p99 latency > 150ms",
                    ),
                ],
                statistical_confidence=StatisticalConfidence(
                    confidence_level=0.95, min_samples=3
                ),
                rollback=RollbackAction(
                    trigger=RollbackTrigger.TWO_CONSECUTIVE_FAILURES,
                    actions=[
                        "Revert to last passing build",
                        "Profiling and optimization",
                        "Quantization evaluation",
                    ],
                ),
                dependencies=[],  # Independent of G1-G3
            ),
        ]

        for gate in gates:
            self._gates[gate.id] = gate

    def get_gate(self, gate_id: str) -> Gate | None:
        """Get a gate by ID."""
        return self._gates.get(gate_id)

    def get_all_gates(self) -> list[Gate]:
        """Get all gates."""
        return list(self._gates.values())

    def evaluate_gate(
        self,
        gate_id: str,
        metrics: dict[str, list[float]],
    ) -> GateResult:
        """
        Evaluate a gate against metric values.

        Args:
            gate_id: Gate to evaluate
            metrics: Dictionary mapping metric IDs to lists of values

        Returns:
            GateResult with evaluation outcome
        """
        gate = self.get_gate(gate_id)
        if not gate:
            return GateResult(
                gate_id=gate_id,
                status=GateStatus.BLOCKED,
                evaluated_at=datetime.now(),
                criterion_results=[],
                all_passed=False,
                message=f"Unknown gate: {gate_id}",
            )

        # Check dependencies
        for dep_id in gate.dependencies:
            if dep_id not in self._pass_history or not self._pass_history[dep_id]:
                return GateResult(
                    gate_id=gate_id,
                    status=GateStatus.BLOCKED,
                    evaluated_at=datetime.now(),
                    criterion_results=[],
                    all_passed=False,
                    message=f"Blocked on dependency: {dep_id}",
                )

        criterion_results: list[CriterionResult] = []
        all_passed = True

        for criterion in gate.criteria:
            metric = self._metrics.get_by_id(criterion.metric_id)
            values = metrics.get(criterion.metric_id, [])

            if not metric:
                criterion_results.append(
                    CriterionResult(
                        criterion=criterion,
                        metric_name=criterion.metric_id,
                        values=values,
                        threshold=criterion.threshold,
                        passed=False,
                        message=f"Unknown metric: {criterion.metric_id}",
                    )
                )
                all_passed = False
                continue

            passed, message = criterion.evaluate(
                values, metric, gate.statistical_confidence
            )

            criterion_results.append(
                CriterionResult(
                    criterion=criterion,
                    metric_name=metric.name,
                    values=values,
                    threshold=criterion.threshold,
                    passed=passed,
                    message=message,
                )
            )

            if not passed:
                all_passed = False

        # Determine status
        if all_passed:
            status = GateStatus.PASSED
            self._pass_history[gate_id] = self._pass_history.get(gate_id, [])
            self._pass_history[gate_id].append(datetime.now())
            self._failure_counts[gate_id] = 0
            message = f"Gate {gate_id} PASSED: All {len(criterion_results)} criteria met"
        else:
            self._failure_counts[gate_id] = self._failure_counts.get(gate_id, 0) + 1
            failed_count = sum(1 for cr in criterion_results if not cr.passed)
            status = GateStatus.FAILED
            message = f"Gate {gate_id} FAILED: {failed_count}/{len(criterion_results)} criteria failed"

        return GateResult(
            gate_id=gate_id,
            status=status,
            evaluated_at=datetime.now(),
            criterion_results=criterion_results,
            all_passed=all_passed,
            message=message,
            consecutive_failures=self._failure_counts.get(gate_id, 0),
        )

    def should_rollback(self, gate_id: str) -> tuple[bool, RollbackAction | None]:
        """
        Check if a gate should trigger rollback.

        Args:
            gate_id: Gate to check

        Returns:
            Tuple of (should_rollback, rollback_action)
        """
        gate = self.get_gate(gate_id)
        if not gate or not gate.rollback:
            return (False, None)

        failure_count = self._failure_counts.get(gate_id, 0)

        if gate.rollback.trigger == RollbackTrigger.TWO_CONSECUTIVE_FAILURES:
            return (failure_count >= 2, gate.rollback)
        elif gate.rollback.trigger == RollbackTrigger.THREE_CONSECUTIVE_FAILURES:
            return (failure_count >= 3, gate.rollback)

        return (False, None)

    def get_gate_status(self, gate_id: str) -> GateStatus:
        """Get current status of a gate."""
        if gate_id not in self._gates:
            return GateStatus.BLOCKED

        if gate_id in self._pass_history and self._pass_history[gate_id]:
            return GateStatus.PASSED

        if self._failure_counts.get(gate_id, 0) > 0:
            return GateStatus.FAILED

        return GateStatus.NOT_STARTED

    def get_progression_order(self) -> list[str]:
        """Get gates in progression order."""
        # Simple topological sort based on dependencies
        ordered = []
        remaining = set(self._gates.keys())

        while remaining:
            for gate_id in list(remaining):
                gate = self._gates[gate_id]
                deps_met = all(dep in ordered for dep in gate.dependencies)
                if deps_met:
                    ordered.append(gate_id)
                    remaining.remove(gate_id)
                    break

        return ordered
