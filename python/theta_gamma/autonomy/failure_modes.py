"""
Failure Modes — Enumerates failure modes for autonomous agent operation.

This module defines the failure mode catalog with detection signals,
impact assessment, and prescribed mitigation strategies for each mode.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class FailureModeSeverity(str, Enum):
    """
    Severity levels for failure modes.

    - CRITICAL: Immediate action required, pipeline halt
    - HIGH: Block progression, notify team
    - MEDIUM: Log and investigate, continue cautiously
    - LOW: Log for trend analysis
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FailureModeLikelihood(str, Enum):
    """
    Likelihood levels for failure modes.

    - VERY_HIGH: Expected to occur frequently
    - HIGH: Expected to occur regularly
    - MEDIUM: Expected to occur occasionally
    - LOW: Expected to occur rarely
    - VERY_LOW: Expected to occur very rarely
    """

    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class FailureModeImpact(str, Enum):
    """
    Impact levels for failure modes.

    - CRITICAL: Existential threat to project
    - HIGH: Significant setback
    - MEDIUM: Moderate setback
    - LOW: Minor inconvenience
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class FailureMode:
    """
    A defined failure mode with detection and mitigation.

    Attributes:
        id: Unique identifier (e.g., "FM-01")
        name: Human-readable name
        description: Detailed description of the failure mode
        likelihood: How likely the failure is to occur
        impact: Impact level if the failure occurs
        detection: How to detect the failure
        mitigation: How to mitigate or prevent the failure
        recovery: How to recover from the failure
        category: Category of failure (e.g., "compute", "data", "security")
    """

    id: str
    name: str
    description: str
    likelihood: FailureModeLikelihood
    impact: FailureModeImpact
    detection: str
    mitigation: str
    recovery: str
    category: str = "general"

    @property
    def risk_level(self) -> str:
        """
        Calculate overall risk level from likelihood and impact.

        Returns:
            Risk level string (e.g., "High", "Medium")
        """
        likelihood_scores = {
            FailureModeLikelihood.VERY_HIGH: 5,
            FailureModeLikelihood.HIGH: 4,
            FailureModeLikelihood.MEDIUM: 3,
            FailureModeLikelihood.LOW: 2,
            FailureModeLikelihood.VERY_LOW: 1,
        }
        impact_scores = {
            FailureModeImpact.CRITICAL: 4,
            FailureModeImpact.HIGH: 3,
            FailureModeImpact.MEDIUM: 2,
            FailureModeImpact.LOW: 1,
        }

        score = likelihood_scores.get(self.likelihood, 3) * impact_scores.get(self.impact, 2)

        if score >= 15:
            return "Critical"
        elif score >= 10:
            return "High"
        elif score >= 6:
            return "Medium"
        else:
            return "Low"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "likelihood": self.likelihood.value,
            "impact": self.impact.value,
            "detection": self.detection,
            "mitigation": self.mitigation,
            "recovery": self.recovery,
            "category": self.category,
            "risk_level": self.risk_level,
        }


class FailureModeRegistry:
    """
    Registry of all defined failure modes.

    The registry provides lookup, filtering, and severity matrix generation
    for the failure mode catalog.

    Example:
        >>> registry = FailureModeRegistry()
        >>> fm = registry.get_by_id("FM-01")
        >>> if fm:
        ...     print(f"Risk level: {fm.risk_level}")
    """

    def __init__(self) -> None:
        """Initialize the failure mode registry."""
        self._failure_modes: dict[str, FailureMode] = {}
        self._initialize_default_failure_modes()

    def _initialize_default_failure_modes(self) -> None:
        """Initialize default failure modes from the specification."""
        modes = [
            # Compute/Financial Failures
            FailureMode(
                id="FM-01",
                name="Runaway Compute Spend",
                description=(
                    "Agent spawns parallel workloads or long-running processes that "
                    "exceed cost guardrails before alerts fire."
                ),
                likelihood=FailureModeLikelihood.MEDIUM,
                impact=FailureModeImpact.HIGH,
                detection=(
                    "Cost alert at 80% threshold; daily spend exceeds daily_compute_cap_usd"
                ),
                mitigation=("Hard circuit-breaker at 100% monthly cap; daily cap enforced"),
                recovery="Terminate ephemeral resources; review spending log",
                category="compute",
            ),
            FailureMode(
                id="FM-02",
                name="Silent Decision Drift",
                description=(
                    "Agent makes many individually-acceptable T0/T1 decisions that "
                    "cumulatively shift the project in an unintended direction."
                ),
                likelihood=FailureModeLikelihood.MEDIUM,
                impact=FailureModeImpact.MEDIUM,
                detection=(
                    "Weekly human review of decision log; anomaly detection on decision frequency"
                ),
                mitigation=("Daily automated digest of T1/T2 decisions; weekly pattern review"),
                recovery=("Revert affected changes via git history; recalibrate decision classes"),
                category="autonomy",
            ),
            FailureMode(
                id="FM-03",
                name="Cascading Retry Loops",
                description=(
                    "Transient failures trigger retries, which fail in the same way, "
                    "consuming resources and delaying pipeline progress."
                ),
                likelihood=FailureModeLikelihood.MEDIUM,
                impact=FailureModeImpact.LOW,
                detection="max_ci_retries_per_job exceeded; escalation trigger",
                mitigation=(
                    "Exponential backoff with max 3 retries; permanent error detection "
                    "halts retries"
                ),
                recovery="Log failure; halt affected pipeline stage; notify operator",
                category="pipeline",
            ),
            FailureMode(
                id="FM-04",
                name="Stale Lock / Orphaned Resource",
                description=(
                    "Agent provisions ephemeral environments or acquires locks that "
                    "are not properly released due to crash or timeout."
                ),
                likelihood=FailureModeLikelihood.MEDIUM,
                impact=FailureModeImpact.MEDIUM,
                detection=("Ephemeral env lifetime exceeds max lifetime; lock age monitoring"),
                mitigation=(
                    "Hard lifetime cap on ephemeral envs (8h); automatic teardown of "
                    "idle environments (4h)"
                ),
                recovery="Force-release orphaned locks; teardown stale environments",
                category="infrastructure",
            ),
            FailureMode(
                id="FM-05",
                name="Incorrect Reversibility Assessment",
                description=(
                    "Agent classifies a decision as reversible when it is actually "
                    "irreversible, bypassing required escalation."
                ),
                likelihood=FailureModeLikelihood.LOW,
                impact=FailureModeImpact.HIGH,
                detection="Post-hoc audit reveals decision was not actually reversible",
                mitigation=(
                    "Conservative reversibility definition; explicit irreversible registry"
                ),
                recovery=(
                    "Incident response; update decision matrix to reclassify; contract amendment"
                ),
                category="autonomy",
            ),
            FailureMode(
                id="FM-06",
                name="Escalation Fatigue",
                description=(
                    "Too many T3 escalations cause human operator to rubber-stamp "
                    "approvals, defeating the purpose of the escalation gate."
                ),
                likelihood=FailureModeLikelihood.MEDIUM,
                impact=FailureModeImpact.HIGH,
                detection=(
                    "Approval response time drops below 30 seconds consistently; "
                    "approval rate exceeds 98%"
                ),
                mitigation=(
                    "Batch non-urgent escalations; reduce unnecessary T3 classifications; "
                    "provide clear context"
                ),
                recovery=(
                    "Review and downgrade safe T3 decisions to T2; improve escalation "
                    "request quality"
                ),
                category="autonomy",
            ),
            FailureMode(
                id="FM-07",
                name="Dependency Supply Chain Compromise",
                description=(
                    "Agent auto-installs a compromised patch/minor dependency update "
                    "that passes automated security scans."
                ),
                likelihood=FailureModeLikelihood.LOW,
                impact=FailureModeImpact.CRITICAL,
                detection=(
                    "Daily security scans; anomalous behavior in tests; unexpected network calls"
                ),
                mitigation=(
                    "Only install from approved registries; lockfile pinning; license "
                    "audit on every change"
                ),
                recovery=(
                    "Revert dependency; rotate any exposed secrets; audit for data exfiltration"
                ),
                category="security",
            ),
            FailureMode(
                id="FM-08",
                name="Test Suite False Confidence",
                description=(
                    "Agent adds tests that pass but do not meaningfully validate "
                    "behavior, inflating coverage metrics without catching regressions."
                ),
                likelihood=FailureModeLikelihood.MEDIUM,
                impact=FailureModeImpact.MEDIUM,
                detection=(
                    "Mutation testing scores diverge from line coverage; regressions "
                    "found post-merge"
                ),
                mitigation=(
                    "Human review of test changes for security-critical paths; mutation "
                    "testing as supplementary gate"
                ),
                recovery=(
                    "Add targeted regression tests; tighten test review policy for critical paths"
                ),
                category="quality",
            ),
            FailureMode(
                id="FM-09",
                name="Partial Pipeline Failure with Implicit Continue",
                description=(
                    "A non-critical pipeline stage fails but the agent continues "
                    "execution, producing artifacts that depend on the failed output."
                ),
                likelihood=FailureModeLikelihood.MEDIUM,
                impact=FailureModeImpact.HIGH,
                detection=("Critical path error trigger; artifact validation checks"),
                mitigation=(
                    "Explicit dependency graph between pipeline stages; critical path "
                    "errors halt pipeline"
                ),
                recovery="Invalidate and regenerate dependent artifacts; re-run from failed stage",
                category="pipeline",
            ),
            FailureMode(
                id="FM-10",
                name="Notification Storm",
                description=(
                    "Rapid autonomous decisions generate excessive internal notifications, "
                    "overwhelming operators and burying important alerts."
                ),
                likelihood=FailureModeLikelihood.LOW,
                impact=FailureModeImpact.MEDIUM,
                detection="Notification rate exceeds max per hour",
                mitigation=(
                    "Rate limiting (20/hour); batched daily digest for T0/T1; priority "
                    "channel for T3+"
                ),
                recovery="Silence non-critical notifications; review notification thresholds",
                category="operations",
            ),
            FailureMode(
                id="FM-11",
                name="Secret Exposure in Logs or Artifacts",
                description=(
                    "Agent inadvertently logs, commits, or includes secrets in generated "
                    "artifacts, docs, or error messages."
                ),
                likelihood=FailureModeLikelihood.LOW,
                impact=FailureModeImpact.CRITICAL,
                detection=("Secret scanning in CI; pre-commit hooks; audit of generated artifacts"),
                mitigation=(
                    "Secret exposure is T4 prohibited; automated secret scanning; "
                    ".gitignore enforcement"
                ),
                recovery="Rotate exposed secrets immediately; scrub git history; incident response",
                category="security",
            ),
            FailureMode(
                id="FM-12",
                name="Contract Interpretation Ambiguity",
                description=(
                    "Agent encounters a decision that does not clearly map to any existing "
                    "decision class, and either misclassifies it or invents an ad-hoc classification."
                ),
                likelihood=FailureModeLikelihood.MEDIUM,
                impact=FailureModeImpact.MEDIUM,
                detection=("Decision log entry references unknown or improvised class"),
                mitigation=(
                    "Default to highest applicable tier when ambiguous; log ambiguity for review"
                ),
                recovery="Classify and add the new decision class to the matrix; contract amendment",
                category="autonomy",
            ),
        ]

        for mode in modes:
            self._failure_modes[mode.id] = mode

    def get_by_id(self, mode_id: str) -> FailureMode | None:
        """
        Get a failure mode by ID.

        Args:
            mode_id: The failure mode ID (e.g., "FM-01")

        Returns:
            FailureMode or None if not found
        """
        return self._failure_modes.get(mode_id)

    def get_by_category(self, category: str) -> list[FailureMode]:
        """
        Get all failure modes in a category.

        Args:
            category: The category to filter by

        Returns:
            List of FailureMode instances
        """
        return [fm for fm in self._failure_modes.values() if fm.category == category]

    def get_by_severity(self, severity: FailureModeSeverity) -> list[FailureMode]:
        """
        Get all failure modes with a given severity.

        Args:
            severity: The severity level to filter by

        Returns:
            List of FailureMode instances
        """
        return [fm for fm in self._failure_modes.values() if fm.impact == severity]

    def get_high_risk_modes(self) -> list[FailureMode]:
        """
        Get all failure modes with High or Critical risk level.

        Returns:
            List of high-risk FailureMode instances
        """
        return [fm for fm in self._failure_modes.values() if fm.risk_level in ("High", "Critical")]

    def get_all_modes(self) -> list[FailureMode]:
        """Get all registered failure modes."""
        return list(self._failure_modes.values())

    def get_severity_matrix(self) -> dict[str, dict[str, int]]:
        """
        Generate a severity matrix showing count of modes by category and severity.

        Returns:
            Dictionary mapping categories to severity counts
        """
        matrix: dict[str, dict[str, int]] = {}

        for fm in self._failure_modes.values():
            if fm.category not in matrix:
                matrix[fm.category] = {"critical": 0, "high": 0, "medium": 0, "low": 0}

            matrix[fm.category][fm.impact.value] += 1

        return matrix

    def register_mode(self, mode: FailureMode) -> None:
        """
        Register a new failure mode.

        Args:
            mode: The FailureMode to register
        """
        self._failure_modes[mode.id] = mode

    def to_dict(self) -> dict[str, Any]:
        """Convert registry to dictionary for serialization."""
        return {
            "failure_modes": [fm.to_dict() for fm in self._failure_modes.values()],
            "severity_matrix": self.get_severity_matrix(),
            "high_risk_count": len(self.get_high_risk_modes()),
            "total_count": len(self._failure_modes),
        }
