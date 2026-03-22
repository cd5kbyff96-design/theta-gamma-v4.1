"""
Evaluation module — Metrics, gates, eval harness, and failure signals.

This module implements the evaluation system for the Theta-Gamma pipeline,
including metric definitions, gate evaluations, eval harness orchestration,
failure signal detection, and dataset management.
"""

from theta_gamma.evaluation.metrics import (
    Metric,
    MetricDictionary,
    MetricDomain,
    MetricType,
)
from theta_gamma.evaluation.gates import (
    Gate,
    GateEvaluator,
    GateStatus,
    GateCriterion,
    GateResult,
    StatisticalConfidence,
)
from theta_gamma.evaluation.harness import (
    EvalHarness,
    EvalSuite,
    EvalSuiteType,
    EvalMode,
    EvalResult,
)
from theta_gamma.evaluation.failure_signals import (
    FailureSignal,
    SignalSeverity,
    FailureSignalRegistry,
    TrainingFailureSignals,
    CrossModalFailureSignals,
    LatencyFailureSignals,
    SafetyFailureSignals,
)
from theta_gamma.evaluation.datasets import (
    EvalDataset,
    DatasetManifest,
    DatasetIntegrityChecker,
)

__all__ = [
    # Metrics
    "Metric",
    "MetricDictionary",
    "MetricDomain",
    "MetricType",
    # Gates
    "Gate",
    "GateEvaluator",
    "GateStatus",
    "GateCriterion",
    "GateResult",
    "StatisticalConfidence",
    # Harness
    "EvalHarness",
    "EvalSuite",
    "EvalSuiteType",
    "EvalMode",
    "EvalResult",
    # Failure Signals
    "FailureSignal",
    "SignalSeverity",
    "FailureSignalRegistry",
    "TrainingFailureSignals",
    "CrossModalFailureSignals",
    "LatencyFailureSignals",
    "SafetyFailureSignals",
    # Datasets
    "EvalDataset",
    "DatasetManifest",
    "DatasetIntegrityChecker",
]
