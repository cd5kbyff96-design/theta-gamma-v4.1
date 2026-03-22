"""
Failure Signals — Detection and classification of pipeline failures.

This module implements the failure signal system that detects problems
during training, evaluation, and deployment, with severity levels and
recommended responses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable


class SignalSeverity(str, Enum):
    """
    Failure signal severity levels.

    Determines response time and escalation path.
    """

    S1_CRITICAL = "S1"
    S2_HIGH = "S2"
    S3_MEDIUM = "S3"
    S4_LOW = "S4"


@dataclass
class FailureSignal:
    """
    A failure signal indicating a problem.

    Attributes:
        id: Unique identifier (e.g., "FS-TR-01")
        name: Human-readable name
        description: Detailed description
        severity: Signal severity
        category: Failure category
        detection_fn: Function to detect the signal
        response_time: Required response time
        root_causes: List of potential root causes
        response: Recommended response action
        escalation_target: Who to escalate to
    """

    id: str
    name: str
    description: str
    severity: SignalSeverity
    category: str
    detection_fn: Callable[..., tuple[bool, str]] | None = None
    response_time: str = ""
    root_causes: list[str] = field(default_factory=list)
    response: str = ""
    escalation_target: str = ""
    triggered_at: datetime | None = None
    resolved_at: datetime | None = None

    def detect(self, **kwargs: Any) -> tuple[bool, str]:
        """
        Run detection logic for this signal.

        Args:
            **kwargs: Detection parameters

        Returns:
            Tuple of (is_triggered, message)
        """
        if self.detection_fn:
            return self.detection_fn(**kwargs)
        return (False, "No detection function defined")

    def trigger(self) -> None:
        """Mark the signal as triggered."""
        self.triggered_at = datetime.now()

    def resolve(self) -> None:
        """Mark the signal as resolved."""
        self.resolved_at = datetime.now()

    def is_active(self) -> bool:
        """Check if signal is currently active."""
        return self.triggered_at is not None and self.resolved_at is None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "severity": self.severity.value,
            "category": self.category,
            "response_time": self.response_time,
            "root_causes": self.root_causes,
            "response": self.response,
            "escalation_target": self.escalation_target,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "is_active": self.is_active(),
        }


class FailureSignalRegistry:
    """
    Registry of all failure signals.

    Provides lookup, filtering, and signal management.
    """

    def __init__(self) -> None:
        """Initialize the failure signal registry."""
        self._signals: dict[str, FailureSignal] = {}
        self._active_signals: list[FailureSignal] = []

    def register(self, signal: FailureSignal) -> None:
        """Register a failure signal."""
        self._signals[signal.id] = signal

    def get_by_id(self, signal_id: str) -> FailureSignal | None:
        """Get a signal by ID."""
        return self._signals.get(signal_id)

    def get_by_severity(self, severity: SignalSeverity) -> list[FailureSignal]:
        """Get all signals with a given severity."""
        return [s for s in self._signals.values() if s.severity == severity]

    def get_by_category(self, category: str) -> list[FailureSignal]:
        """Get all signals in a category."""
        return [s for s in self._signals.values() if s.category == category]

    def get_active_signals(self) -> list[FailureSignal]:
        """Get all currently active signals."""
        return self._active_signals.copy()

    def get_critical_signals(self) -> list[FailureSignal]:
        """Get all critical (S1) signals."""
        return self.get_by_severity(SignalSeverity.S1_CRITICAL)

    def activate_signal(self, signal_id: str) -> FailureSignal | None:
        """Activate a signal."""
        signal = self.get_by_id(signal_id)
        if signal:
            signal.trigger()
            if signal not in self._active_signals:
                self._active_signals.append(signal)
        return signal

    def resolve_signal(self, signal_id: str) -> FailureSignal | None:
        """Resolve a signal."""
        signal = self.get_by_id(signal_id)
        if signal:
            signal.resolve()
            self._active_signals = [s for s in self._active_signals if s.id != signal_id]
        return signal

    def get_all_signals(self) -> list[FailureSignal]:
        """Get all registered signals."""
        return list(self._signals.values())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "signals": [s.to_dict() for s in self._signals.values()],
            "active_count": len(self._active_signals),
            "critical_count": len(self.get_critical_signals()),
        }


class TrainingFailureSignals:
    """Training-specific failure signals."""

    @staticmethod
    def loss_divergence() -> FailureSignal:
        """Loss divergence signal (S1)."""
        return FailureSignal(
            id="FS-TR-01",
            name="Loss Divergence",
            description="Training loss increases by > 50% over 100 steps",
            severity=SignalSeverity.S1_CRITICAL,
            category="training",
            response_time="Immediate",
            root_causes=[
                "Learning rate too high",
                "Data corruption",
                "Gradient explosion",
            ],
            response="Halt training, revert to last stable checkpoint, reduce learning rate by 50%",
            escalation_target="ML Engineer",
        )

    @staticmethod
    def validation_plateau() -> FailureSignal:
        """Validation loss plateau signal (S2)."""
        return FailureSignal(
            id="FS-TR-02",
            name="Validation Loss Plateau",
            description="Validation loss does not improve for 10 consecutive epochs",
            severity=SignalSeverity.S2_HIGH,
            category="training",
            response_time="< 4 hours",
            root_causes=[
                "Insufficient model capacity",
                "Learning rate needs scheduling",
                "Data saturation",
            ],
            response="Trigger learning rate decay, evaluate data augmentation options",
            escalation_target="ML Engineer",
        )

    @staticmethod
    def overfitting() -> FailureSignal:
        """Overfitting signal (S2)."""
        return FailureSignal(
            id="FS-TR-03",
            name="Overfitting",
            description="Overfitting gap exceeds 0.5 nats and is increasing",
            severity=SignalSeverity.S2_HIGH,
            category="training",
            response_time="< 4 hours",
            root_causes=[
                "Insufficient regularization",
                "Training data too small",
                "Data leakage",
            ],
            response="Increase dropout, add weight decay, check for train/eval overlap",
            escalation_target="ML Engineer",
        )

    @staticmethod
    def gradient_explosion() -> FailureSignal:
        """Gradient explosion signal (S1)."""
        return FailureSignal(
            id="FS-TR-04",
            name="Gradient Explosion",
            description="Gradient norm exceeds 100x the running average",
            severity=SignalSeverity.S1_CRITICAL,
            category="training",
            response_time="Immediate",
            root_causes=[
                "Numerical instability",
                "Bad data batch",
                "Learning rate spike",
            ],
            response="Halt training, skip current batch, apply gradient clipping",
            escalation_target="ML Engineer",
        )

    @staticmethod
    def gradient_vanishing() -> FailureSignal:
        """Gradient vanishing signal (S2)."""
        return FailureSignal(
            id="FS-TR-05",
            name="Gradient Vanishing",
            description="Gradient norm drops below 1e-7 for 500 consecutive steps",
            severity=SignalSeverity.S2_HIGH,
            category="training",
            response_time="< 4 hours",
            root_causes=[
                "Dead neurons",
                "Poor initialization",
                "Activation function saturation",
            ],
            response="Check activation distributions, consider re-initialization",
            escalation_target="ML Engineer",
        )

    @staticmethod
    def nan_loss() -> FailureSignal:
        """NaN/Inf in loss signal (S1)."""
        return FailureSignal(
            id="FS-TR-06",
            name="NaN/Inf in Loss",
            description="Training or validation loss contains NaN or Inf values",
            severity=SignalSeverity.S1_CRITICAL,
            category="training",
            response_time="Immediate",
            root_causes=[
                "Numerical overflow",
                "Division by zero",
                "Corrupted data",
            ],
            response="Immediate halt, revert to last clean checkpoint, enable safeguards",
            escalation_target="ML Engineer",
        )


class CrossModalFailureSignals:
    """Cross-modal evaluation failure signals."""

    @staticmethod
    def accuracy_regression() -> FailureSignal:
        """Cross-modal accuracy regression signal (S2)."""
        return FailureSignal(
            id="FS-CM-01",
            name="Cross-Modal Accuracy Regression",
            description="Cross-modal accuracy drops by > 5pp compared to previous",
            severity=SignalSeverity.S2_HIGH,
            category="cross_modal",
            response_time="< 4 hours",
            root_causes=[
                "Catastrophic forgetting",
                "Data distribution shift",
                "Training instability",
            ],
            response="Revert to previous checkpoint, investigate training data changes",
            escalation_target="ML Engineer",
        )

    @staticmethod
    def modality_imbalance() -> FailureSignal:
        """Modality imbalance signal (S2)."""
        return FailureSignal(
            id="FS-CM-02",
            name="Modality Imbalance",
            description="Max modality gap exceeds 20pp",
            severity=SignalSeverity.S2_HIGH,
            category="cross_modal",
            response_time="< 4 hours",
            root_causes=[
                "Unbalanced training data",
                "One modality encoder undertrained",
            ],
            response="Adjust modality sampling ratios, check per-modality data quality",
            escalation_target="Data Engineer",
        )

    @staticmethod
    def consistency_collapse() -> FailureSignal:
        """Cross-modal consistency collapse signal (S1)."""
        return FailureSignal(
            id="FS-CM-03",
            name="Consistency Collapse",
            description="Cross-modal consistency drops below 30%",
            severity=SignalSeverity.S1_CRITICAL,
            category="cross_modal",
            response_time="Immediate",
            root_causes=[
                "Shared representation space collapsed",
                "Contrastive loss not working",
            ],
            response="Halt training, investigate representation space, check loss function",
            escalation_target="ML Engineer",
        )


class LatencyFailureSignals:
    """Latency and performance failure signals."""

    @staticmethod
    def latency_spike() -> FailureSignal:
        """Latency spike signal (S2)."""
        return FailureSignal(
            id="FS-LT-01",
            name="Latency Spike",
            description="p95 latency exceeds 150ms (50% above threshold)",
            severity=SignalSeverity.S2_HIGH,
            category="latency",
            response_time="< 4 hours",
            root_causes=[
                "Model size increase",
                "Inefficient operator",
                "Memory pressure",
                "Hardware degradation",
            ],
            response="Profile inference path, check for unoptimized operations",
            escalation_target="Infra Engineer",
        )

    @staticmethod
    def throughput_collapse() -> FailureSignal:
        """Throughput collapse signal (S1)."""
        return FailureSignal(
            id="FS-LT-02",
            name="Throughput Collapse",
            description="Throughput drops below 50 QPS",
            severity=SignalSeverity.S1_CRITICAL,
            category="latency",
            response_time="Immediate",
            root_causes=[
                "Memory leak",
                "Deadlock",
                "Resource contention",
                "Infrastructure failure",
            ],
            response="Immediate investigation, check GPU utilization and memory",
            escalation_target="Infra Engineer",
        )

    @staticmethod
    def gpu_memory_overflow() -> FailureSignal:
        """GPU memory overflow signal (S2)."""
        return FailureSignal(
            id="FS-LT-03",
            name="GPU Memory Overflow",
            description="GPU memory exceeds 90% of available",
            severity=SignalSeverity.S2_HIGH,
            category="latency",
            response_time="< 4 hours",
            root_causes=[
                "Batch size too large",
                "Memory leak",
                "Model size increase",
            ],
            response="Reduce batch size, check for memory leaks, evaluate pruning",
            escalation_target="Infra Engineer",
        )


class SafetyFailureSignals:
    """Safety and robustness failure signals."""

    @staticmethod
    def safety_violation_spike() -> FailureSignal:
        """Safety violation spike signal (S1)."""
        return FailureSignal(
            id="FS-SF-01",
            name="Safety Violation Spike",
            description="Safety violation rate exceeds 1.0% (10x threshold)",
            severity=SignalSeverity.S1_CRITICAL,
            category="safety",
            response_time="Immediate",
            root_causes=[
                "Training data contamination",
                "Safety fine-tuning regression",
                "Adversarial data",
            ],
            response="Halt all deployment, quarantine checkpoint, investigate data",
            escalation_target="Safety Lead",
        )

    @staticmethod
    def robustness_drop() -> FailureSignal:
        """Adversarial robustness drop signal (S2)."""
        return FailureSignal(
            id="FS-SF-02",
            name="Adversarial Robustness Drop",
            description="Adversarial robustness drops below 25%",
            severity=SignalSeverity.S2_HIGH,
            category="safety",
            response_time="< 4 hours",
            root_causes=[
                "Overfitting to clean data",
                "Adversarial training weight too low",
            ],
            response="Increase adversarial training ratio, add stronger perturbations",
            escalation_target="ML Engineer",
        )

    @staticmethod
    def calibration_degradation() -> FailureSignal:
        """Calibration degradation signal (S3)."""
        return FailureSignal(
            id="FS-SF-03",
            name="Calibration Degradation",
            description="Calibration ECE exceeds 0.10 (2x threshold)",
            severity=SignalSeverity.S3_MEDIUM,
            category="safety",
            response_time="< 24 hours",
            root_causes=[
                "Temperature scaling drift",
                "Distribution shift",
                "Overconfident predictions",
            ],
            response="Re-calibrate with temperature scaling, check confidence distributions",
            escalation_target="ML Engineer",
        )
