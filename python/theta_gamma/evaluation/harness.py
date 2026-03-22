"""
Evaluation Harness — Orchestrates eval suites and collects metrics.

This module implements the evaluation harness that runs benchmark suites,
collects metrics, and produces structured reports for gate evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from theta_gamma.evaluation.metrics import MetricDictionary


class EvalMode(str, Enum):
    """
    Evaluation execution modes.

    Different modes run different subsets of eval suites.
    """

    FULL = "full"
    QUICK = "quick"
    PERF_ONLY = "perf_only"
    SAFETY_ONLY = "safety_only"
    REGRESSION = "regression"


class EvalSuiteType(str, Enum):
    """
    Evaluation suite types.

    Each suite type runs a specific category of evaluations.
    """

    CROSS_MODAL = "cross_modal"
    PER_MODALITY = "per_modality"
    LATENCY_PERF = "latency_perf"
    SAFETY_ROBUSTNESS = "safety_robustness"


@dataclass
class EvalResult:
    """
    Result of an evaluation run.

    Attributes:
        run_id: Unique run identifier
        checkpoint_id: Checkpoint that was evaluated
        mode: Evaluation mode used
        suite_type: Suite type
        metrics: Dictionary of metric ID to value
        started_at: Start timestamp
        completed_at: Completion timestamp
        runtime_seconds: Total runtime
        success: Whether eval completed successfully
        error_message: Error message if failed
    """

    run_id: str
    checkpoint_id: str
    mode: EvalMode
    suite_type: EvalSuiteType
    metrics: dict[str, float]
    started_at: datetime
    completed_at: datetime
    runtime_seconds: float
    success: bool = True
    error_message: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "run_id": self.run_id,
            "checkpoint_id": self.checkpoint_id,
            "mode": self.mode.value,
            "suite_type": self.suite_type.value,
            "metrics": self.metrics,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "runtime_seconds": self.runtime_seconds,
            "success": self.success,
            "error_message": self.error_message,
        }


@dataclass
class EvalSuite:
    """
    An evaluation suite configuration.

    Attributes:
        suite_type: Type of suite
        name: Human-readable name
        eval_ids: List of evaluation IDs to run
        runtime_budget_minutes: Maximum runtime
        dataset_size: Number of samples
        trigger: When this suite should run
    """

    suite_type: EvalSuiteType
    name: str
    eval_ids: list[str]
    runtime_budget_minutes: int
    dataset_size: int
    trigger: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "suite_type": self.suite_type.value,
            "name": self.name,
            "eval_ids": self.eval_ids,
            "runtime_budget_minutes": self.runtime_budget_minutes,
            "dataset_size": self.dataset_size,
            "trigger": self.trigger,
        }


class EvalHarness:
    """
    Main evaluation harness orchestrator.

    The harness coordinates eval suite execution, manages dependencies
    between suites, collects metrics, and produces reports.

    Example:
        >>> harness = EvalHarness()
        >>> result = await harness.run_eval(
        ...     mode=EvalMode.FULL,
        ...     checkpoint_id="ckpt-001",
        ... )
        >>> print(f"Metrics: {result.metrics}")
    """

    def __init__(
        self,
        metric_dictionary: MetricDictionary | None = None,
        results_dir: Path | None = None,
    ) -> None:
        """
        Initialize the evaluation harness.

        Args:
            metric_dictionary: Dictionary of metric definitions
            results_dir: Directory for eval results
        """
        self._metrics = metric_dictionary or MetricDictionary()
        self._results_dir = results_dir or Path("results/eval")
        self._suites: dict[EvalSuiteType, EvalSuite] = {}
        self._results: list[EvalResult] = []

        self._initialize_default_suites()

    def _initialize_default_suites(self) -> None:
        """Initialize default eval suites from the specification."""
        suites = [
            EvalSuite(
                suite_type=EvalSuiteType.CROSS_MODAL,
                name="Cross-Modal Suite",
                eval_ids=[
                    "M-CM-001",
                    "M-CM-002",
                    "M-CM-003",
                    "M-CM-004",
                ],
                runtime_budget_minutes=60,
                dataset_size=10000,
                trigger="end_of_training_run",
            ),
            EvalSuite(
                suite_type=EvalSuiteType.PER_MODALITY,
                name="Per-Modality Suite",
                eval_ids=[
                    "M-MOD-001",
                    "M-MOD-002",
                    "M-MOD-003",
                    "M-MOD-004",
                ],
                runtime_budget_minutes=30,
                dataset_size=5000,
                trigger="end_of_training_run",
            ),
            EvalSuite(
                suite_type=EvalSuiteType.LATENCY_PERF,
                name="Latency & Performance Suite",
                eval_ids=[
                    "M-LAT-001",
                    "M-LAT-002",
                    "M-LAT-003",
                    "M-THR-001",
                    "M-RES-001",
                ],
                runtime_budget_minutes=45,
                dataset_size=10000,
                trigger="per_build",
            ),
            EvalSuite(
                suite_type=EvalSuiteType.SAFETY_ROBUSTNESS,
                name="Safety & Robustness Suite",
                eval_ids=[
                    "M-ROB-001",
                    "M-ROB-002",
                    "M-ROB-003",
                    "M-SAF-001",
                ],
                runtime_budget_minutes=90,
                dataset_size=5000,
                trigger="end_of_training_run",
            ),
        ]

        for suite in suites:
            self._suites[suite.suite_type] = suite

    def get_suite_for_mode(self, mode: EvalMode) -> list[EvalSuiteType]:
        """
        Get suite types to run for a given mode.

        Args:
            mode: Evaluation mode

        Returns:
            List of suite types to run
        """
        mode_mapping = {
            EvalMode.FULL: list(EvalSuiteType),
            EvalMode.QUICK: [EvalSuiteType.CROSS_MODAL, EvalSuiteType.PER_MODALITY],
            EvalMode.PERF_ONLY: [EvalSuiteType.LATENCY_PERF],
            EvalMode.SAFETY_ONLY: [EvalSuiteType.SAFETY_ROBUSTNESS],
            EvalMode.REGRESSION: list(EvalSuiteType),
        }
        return mode_mapping.get(mode, [])

    async def run_eval(
        self,
        mode: EvalMode,
        checkpoint_id: str,
        run_id: str | None = None,
    ) -> list[EvalResult]:
        """
        Run evaluation for a checkpoint.

        Args:
            mode: Evaluation mode
            checkpoint_id: Checkpoint to evaluate
            run_id: Optional run ID (generated if not provided)

        Returns:
            List of EvalResult for each suite
        """
        if run_id is None:
            run_id = f"eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        suite_types = self.get_suite_for_mode(mode)
        results: list[EvalResult] = []

        for suite_type in suite_types:
            suite = self._suites.get(suite_type)
            if not suite:
                continue

            result = await self._run_suite(
                suite=suite,
                checkpoint_id=checkpoint_id,
                run_id=run_id,
                mode=mode,
            )
            results.append(result)
            self._results.append(result)

        return results

    async def _run_suite(
        self,
        suite: EvalSuite,
        checkpoint_id: str,
        run_id: str,
        mode: EvalMode,
    ) -> EvalResult:
        """
        Run a single eval suite.

        Args:
            suite: Suite to run
            checkpoint_id: Checkpoint to evaluate
            run_id: Run identifier
            mode: Evaluation mode

        Returns:
            EvalResult for the suite
        """
        started_at = datetime.now()
        metrics: dict[str, float] = {}
        success = True
        error_message = ""

        try:
            # Simulate running each evaluation in the suite
            for eval_id in suite.eval_ids:
                metric = self._metrics.get_by_id(eval_id)
                if metric:
                    # In production, this would call the actual eval function
                    # For now, we simulate with placeholder values
                    metrics[eval_id] = self._simulate_eval(eval_id)
        except Exception as e:
            success = False
            error_message = str(e)

        completed_at = datetime.now()
        runtime_seconds = (completed_at - started_at).total_seconds()

        return EvalResult(
            run_id=run_id,
            checkpoint_id=checkpoint_id,
            mode=mode,
            suite_type=suite.suite_type,
            metrics=metrics,
            started_at=started_at,
            completed_at=completed_at,
            runtime_seconds=runtime_seconds,
            success=success,
            error_message=error_message,
        )

    def _simulate_eval(self, eval_id: str) -> float:
        """
        Simulate an evaluation (placeholder for actual eval logic).

        Args:
            eval_id: Evaluation ID

        Returns:
            Simulated metric value
        """
        # Placeholder values - in production, these would come from actual evals
        placeholder_values = {
            "M-CM-001": 45.0,  # Cross-modal accuracy
            "M-CM-002": 0.42,  # Cross-modal F1
            "M-CM-003": 35.0,  # Cross-modal consistency
            "M-CM-004": 40.0,  # Retrieval Recall@10
            "M-MOD-001": 50.0,  # Text accuracy
            "M-MOD-002": 48.0,  # Image accuracy
            "M-MOD-003": 45.0,  # Audio accuracy
            "M-MOD-004": 15.0,  # Modality gap
            "M-LAT-001": 45.0,  # p50 latency
            "M-LAT-002": 85.0,  # p95 latency
            "M-LAT-003": 120.0,  # p99 latency
            "M-THR-001": 120.0,  # Throughput
            "M-RES-001": 65.0,  # GPU memory
            "M-ROB-001": 32.0,  # Adversarial robustness
            "M-ROB-002": 0.78,  # OOD AUROC
            "M-ROB-003": 0.04,  # Calibration ECE
            "M-SAF-001": 0.05,  # Safety violation rate
        }
        return placeholder_values.get(eval_id, 0.0)

    def get_results(self, run_id: str | None = None) -> list[EvalResult]:
        """
        Get eval results.

        Args:
            run_id: Optional filter by run ID

        Returns:
            List of EvalResult
        """
        if run_id:
            return [r for r in self._results if r.run_id == run_id]
        return self._results.copy()

    def get_latest_metrics(self) -> dict[str, float]:
        """
        Get latest metrics from all eval results.

        Returns:
            Dictionary of metric ID to latest value
        """
        if not self._results:
            return {}

        metrics: dict[str, float] = {}
        for result in reversed(self._results):
            for metric_id, value in result.metrics.items():
                if metric_id not in metrics:
                    metrics[metric_id] = value
        return metrics

    def generate_report(self, run_id: str) -> dict[str, Any]:
        """
        Generate a report for an eval run.

        Args:
            run_id: Run ID to report on

        Returns:
            Report dictionary
        """
        results = self.get_results(run_id)

        return {
            "run_id": run_id,
            "generated_at": datetime.now().isoformat(),
            "suites_run": [r.suite_type.value for r in results],
            "total_runtime_seconds": sum(r.runtime_seconds for r in results),
            "metrics": {
                metric_id: value
                for result in results
                for metric_id, value in result.metrics.items()
            },
            "success": all(r.success for r in results),
            "errors": [
                {"suite": r.suite_type.value, "error": r.error_message}
                for r in results
                if r.error_message
            ],
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "suites": [s.to_dict() for s in self._suites.values()],
            "results_dir": str(self._results_dir),
            "total_results": len(self._results),
        }
