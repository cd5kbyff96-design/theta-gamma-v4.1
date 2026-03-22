"""
Metric Dictionary — Defines all metrics tracked by the Theta-Gamma pipeline.

This module implements the metric dictionary that defines all metrics
tracked during training, evaluation, and deployment of the Theta-Gamma model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MetricDomain(str, Enum):
    """
    Metric domains for categorization.

    Domains group related metrics together for easier analysis.
    """

    CROSS_MODAL = "cross_modal"
    PER_MODALITY = "per_modality"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    RESOURCE = "resource"
    ROBUSTNESS = "robustness"
    SAFETY = "safety"
    DATA_QUALITY = "data_quality"
    MODEL_QUALITY = "model_quality"
    REGRESSION = "regression"


class MetricType(str, Enum):
    """
    Metric types indicating how values are interpreted.

    Types determine whether higher or lower values are better.
    """

    ACCURACY = "accuracy"  # Higher is better
    LOSS = "loss"  # Lower is better
    LATENCY = "latency"  # Lower is better
    THROUGHPUT = "throughput"  # Higher is better
    MEMORY = "memory"  # Lower is better
    RATE = "rate"  # Context-dependent
    SCORE = "score"  # Higher is better
    COUNT = "count"  # Context-dependent


@dataclass
class Metric:
    """
    A defined metric in the metric dictionary.

    Attributes:
        id: Unique identifier (e.g., "M-CM-001")
        name: Human-readable name
        description: Detailed description
        domain: Metric domain for categorization
        metric_type: Type indicating interpretation
        unit: Unit of measurement
        higher_is_better: Whether higher values are preferable
        threshold: Optional threshold for pass/fail evaluation
    """

    id: str
    name: str
    description: str
    domain: MetricDomain
    metric_type: MetricType
    unit: str = ""
    higher_is_better: bool = True
    threshold: float | None = None

    def evaluate(self, value: float) -> tuple[bool, str]:
        """
        Evaluate a metric value against its threshold.

        Args:
            value: The metric value to evaluate

        Returns:
            Tuple of (passes, message)
        """
        if self.threshold is None:
            return (True, "No threshold defined")

        if self.higher_is_better:
            passes = value >= self.threshold
            comparison = ">="
        else:
            passes = value <= self.threshold
            comparison = "<="

        return (
            passes,
            f"{value}{self.unit} {comparison} {self.threshold}{self.unit}: {'PASS' if passes else 'FAIL'}",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain.value,
            "metric_type": self.metric_type.value,
            "unit": self.unit,
            "higher_is_better": self.higher_is_better,
            "threshold": self.threshold,
        }


class MetricDictionary:
    """
    Registry of all metrics tracked by the pipeline.

    The dictionary provides lookup, filtering by domain, and
    validation of metric values.

    Example:
        >>> metrics = MetricDictionary()
        >>> metric = metrics.get_by_id("M-CM-001")
        >>> passes, msg = metric.evaluate(0.45)
    """

    def __init__(self) -> None:
        """Initialize the metric dictionary."""
        self._metrics: dict[str, Metric] = {}
        self._initialize_default_metrics()

    def _initialize_default_metrics(self) -> None:
        """Initialize default metrics from the specification."""
        metrics = [
            # Cross-Modal Metrics (M-CM-*)
            Metric(
                id="M-CM-001",
                name="Cross-Modal Accuracy",
                description="Top-1 classification accuracy across modality pairs",
                domain=MetricDomain.CROSS_MODAL,
                metric_type=MetricType.ACCURACY,
                unit="%",
                higher_is_better=True,
                threshold=40.0,  # G1 baseline
            ),
            Metric(
                id="M-CM-002",
                name="Cross-Modal F1",
                description="Weighted F1 score across modality pairs",
                domain=MetricDomain.CROSS_MODAL,
                metric_type=MetricType.SCORE,
                unit="",
                higher_is_better=True,
            ),
            Metric(
                id="M-CM-003",
                name="Cross-Modal Consistency",
                description="Agreement rate for same semantic content across modalities",
                domain=MetricDomain.CROSS_MODAL,
                metric_type=MetricType.ACCURACY,
                unit="%",
                higher_is_better=True,
                threshold=30.0,
            ),
            Metric(
                id="M-CM-004",
                name="Cross-Modal Retrieval Recall@10",
                description="Recall in top-10 retrieved items across modalities",
                domain=MetricDomain.CROSS_MODAL,
                metric_type=MetricType.ACCURACY,
                unit="%",
                higher_is_better=True,
            ),
            # Per-Modality Metrics (M-MOD-*)
            Metric(
                id="M-MOD-001",
                name="Text Accuracy",
                description="Standard classification accuracy for text-only samples",
                domain=MetricDomain.PER_MODALITY,
                metric_type=MetricType.ACCURACY,
                unit="%",
                higher_is_better=True,
            ),
            Metric(
                id="M-MOD-002",
                name="Image Accuracy",
                description="Standard classification accuracy for image-only samples",
                domain=MetricDomain.PER_MODALITY,
                metric_type=MetricType.ACCURACY,
                unit="%",
                higher_is_better=True,
            ),
            Metric(
                id="M-MOD-003",
                name="Audio Accuracy",
                description="Standard classification accuracy for audio-only samples",
                domain=MetricDomain.PER_MODALITY,
                metric_type=MetricType.ACCURACY,
                unit="%",
                higher_is_better=True,
            ),
            Metric(
                id="M-MOD-004",
                name="Modality Gap Max",
                description="Maximum pairwise difference between modality accuracies",
                domain=MetricDomain.PER_MODALITY,
                metric_type=MetricType.ACCURACY,
                unit="pp",
                higher_is_better=False,
                threshold=20.0,
            ),
            # Latency Metrics (M-LAT-*)
            Metric(
                id="M-LAT-001",
                name="Inference Latency p50",
                description="Median inference latency",
                domain=MetricDomain.LATENCY,
                metric_type=MetricType.LATENCY,
                unit="ms",
                higher_is_better=False,
            ),
            Metric(
                id="M-LAT-002",
                name="Inference Latency p95",
                description="95th percentile inference latency",
                domain=MetricDomain.LATENCY,
                metric_type=MetricType.LATENCY,
                unit="ms",
                higher_is_better=False,
                threshold=100.0,  # G4 threshold
            ),
            Metric(
                id="M-LAT-003",
                name="Inference Latency p99",
                description="99th percentile inference latency",
                domain=MetricDomain.LATENCY,
                metric_type=MetricType.LATENCY,
                unit="ms",
                higher_is_better=False,
            ),
            # Throughput Metrics (M-THR-*)
            Metric(
                id="M-THR-001",
                name="Sustained Throughput",
                description="Sustained queries per second at peak load",
                domain=MetricDomain.THROUGHPUT,
                metric_type=MetricType.THROUGHPUT,
                unit="QPS",
                higher_is_better=True,
                threshold=100.0,
            ),
            # Resource Metrics (M-RES-*)
            Metric(
                id="M-RES-001",
                name="Peak GPU Memory",
                description="Peak GPU memory usage during inference",
                domain=MetricDomain.RESOURCE,
                metric_type=MetricType.MEMORY,
                unit="GB",
                higher_is_better=False,
            ),
            Metric(
                id="M-RES-002",
                name="GPU Utilization",
                description="Average GPU utilization during training",
                domain=MetricDomain.RESOURCE,
                metric_type=MetricType.RATE,
                unit="%",
                higher_is_better=True,
            ),
            Metric(
                id="M-RES-003",
                name="Cumulative Compute Cost",
                description="Cumulative compute cost in USD",
                domain=MetricDomain.RESOURCE,
                metric_type=MetricType.COUNT,
                unit="USD",
                higher_is_better=False,
            ),
            # Robustness Metrics (M-ROB-*)
            Metric(
                id="M-ROB-001",
                name="Adversarial Robustness",
                description="Accuracy under adversarial perturbations",
                domain=MetricDomain.ROBUSTNESS,
                metric_type=MetricType.ACCURACY,
                unit="%",
                higher_is_better=True,
                threshold=30.0,
            ),
            Metric(
                id="M-ROB-002",
                name="OOD Detection AUROC",
                description="AUROC for out-of-distribution detection",
                domain=MetricDomain.ROBUSTNESS,
                metric_type=MetricType.SCORE,
                unit="",
                higher_is_better=True,
                threshold=0.75,
            ),
            Metric(
                id="M-ROB-003",
                name="Calibration ECE",
                description="Expected Calibration Error (15-bin)",
                domain=MetricDomain.ROBUSTNESS,
                metric_type=MetricType.LOSS,
                unit="",
                higher_is_better=False,
                threshold=0.05,
            ),
            # Safety Metrics (M-SAF-*)
            Metric(
                id="M-SAF-001",
                name="Safety Violation Rate",
                description="Rate of safety classifier flags",
                domain=MetricDomain.SAFETY,
                metric_type=MetricType.RATE,
                unit="%",
                higher_is_better=False,
                threshold=0.1,
            ),
            # Model Quality Metrics (M-MQ-*)
            Metric(
                id="M-MQ-001",
                name="Training Loss",
                description="Training loss per step",
                domain=MetricDomain.MODEL_QUALITY,
                metric_type=MetricType.LOSS,
                unit="",
                higher_is_better=False,
            ),
            Metric(
                id="M-MQ-002",
                name="Validation Loss",
                description="Validation loss per epoch",
                domain=MetricDomain.MODEL_QUALITY,
                metric_type=MetricType.LOSS,
                unit="",
                higher_is_better=False,
            ),
            Metric(
                id="M-MQ-003",
                name="Overfitting Gap",
                description="Gap between training and validation loss",
                domain=MetricDomain.MODEL_QUALITY,
                metric_type=MetricType.LOSS,
                unit="nats",
                higher_is_better=False,
            ),
            Metric(
                id="M-MQ-004",
                name="Gradient Norm",
                description="Norm of gradients during training",
                domain=MetricDomain.MODEL_QUALITY,
                metric_type=MetricType.COUNT,
                unit="",
                higher_is_better=False,
            ),
            # Data Quality Metrics (M-DQ-*)
            Metric(
                id="M-DQ-001",
                name="Modality Coverage",
                description="Coverage of modality pairs in dataset",
                domain=MetricDomain.DATA_QUALITY,
                metric_type=MetricType.RATE,
                unit="%",
                higher_is_better=True,
            ),
            Metric(
                id="M-DQ-002",
                name="Data Freshness",
                description="Age of data in days",
                domain=MetricDomain.DATA_QUALITY,
                metric_type=MetricType.COUNT,
                unit="days",
                higher_is_better=False,
            ),
            # Regression Metrics (M-REG-*)
            Metric(
                id="M-REG-001",
                name="Accuracy Delta",
                description="Change in accuracy from baseline",
                domain=MetricDomain.REGRESSION,
                metric_type=MetricType.ACCURACY,
                unit="pp",
                higher_is_better=True,
            ),
            Metric(
                id="M-REG-002",
                name="Latency Delta",
                description="Change in latency from baseline",
                domain=MetricDomain.REGRESSION,
                metric_type=MetricType.LATENCY,
                unit="ms",
                higher_is_better=False,
            ),
        ]

        for metric in metrics:
            self._metrics[metric.id] = metric

    def get_by_id(self, metric_id: str) -> Metric | None:
        """
        Get a metric by ID.

        Args:
            metric_id: The metric ID (e.g., "M-CM-001")

        Returns:
            Metric or None if not found
        """
        return self._metrics.get(metric_id)

    def get_by_domain(self, domain: MetricDomain) -> list[Metric]:
        """
        Get all metrics in a domain.

        Args:
            domain: The domain to filter by

        Returns:
            List of Metric instances
        """
        return [m for m in self._metrics.values() if m.domain == domain]

    def get_all_metrics(self) -> list[Metric]:
        """Get all registered metrics."""
        return list(self._metrics.values())

    def validate_metric_value(
        self, metric_id: str, value: float
    ) -> tuple[bool, str | None]:
        """
        Validate a metric value is within expected bounds.

        Args:
            metric_id: The metric ID
            value: The value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        metric = self.get_by_id(metric_id)
        if not metric:
            return (False, f"Unknown metric: {metric_id}")

        # Check for NaN/Inf
        import math

        if math.isnan(value) or math.isinf(value):
            return (False, f"Value must be finite: {value}")

        # Check against threshold if defined
        if metric.threshold is not None:
            passes, _ = metric.evaluate(value)
            if not passes:
                return (False, f"Value {value} does not meet threshold {metric.threshold}")

        return (True, None)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metrics": [m.to_dict() for m in self._metrics.values()],
            "domains": list(set(m.domain.value for m in self._metrics.values())),
            "total_count": len(self._metrics),
        }

    @classmethod
    def load_default(cls) -> MetricDictionary:
        """Load the default metric dictionary."""
        return cls()
