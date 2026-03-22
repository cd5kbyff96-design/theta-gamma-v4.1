"""
Pilot Statement of Work — Pilot engagement templates.

This module provides templates for pilot engagements with partners.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class PilotDeliverable:
    """
    Pilot deliverable definition.

    Attributes:
        id: Deliverable identifier
        description: Deliverable description
        owner: Responsible party
        due_week: Week number due
        acceptance_criteria: Acceptance criteria
    """

    id: str
    description: str
    owner: str
    due_week: int
    acceptance_criteria: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "owner": self.owner,
            "due_week": self.due_week,
            "acceptance_criteria": self.acceptance_criteria,
        }


@dataclass
class PilotSuccessCriteria:
    """
    Pilot success criteria.

    Attributes:
        criterion: Criterion name
        metric: Metric to measure
        target: Target value
        measurement_method: How to measure
    """

    criterion: str
    metric: str
    target: str
    measurement_method: str
    passed: bool = False
    actual_value: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "criterion": self.criterion,
            "metric": self.metric,
            "target": self.target,
            "measurement_method": self.measurement_method,
            "passed": self.passed,
            "actual_value": self.actual_value,
        }


class PilotPhase:
    """Pilot phase definitions."""

    SETUP = "setup"
    INTEGRATION = "integration"
    MONITORED_OPERATION = "monitored_operation"
    EVALUATION = "evaluation"


@dataclass
class PilotSOW:
    """
    Pilot Statement of Work.

    Attributes:
        sow_id: SOW identifier
        provider: Provider organization
        partner: Partner organization
        effective_date: Effective date
        duration_weeks: Total duration in weeks
        deliverables: List of deliverables
        success_criteria: Success criteria
        phases: Pilot phases
    """

    sow_id: str
    provider: str
    partner: str
    effective_date: datetime
    duration_weeks: int = 10
    deliverables: list[PilotDeliverable] = field(default_factory=list)
    success_criteria: list[PilotSuccessCriteria] = field(default_factory=list)
    phases: dict[str, dict[str, Any]] = field(default_factory=dict)

    def add_deliverable(self, deliverable: PilotDeliverable) -> None:
        """Add a deliverable."""
        self.deliverables.append(deliverable)

    def add_success_criterion(self, criterion: PilotSuccessCriteria) -> None:
        """Add a success criterion."""
        self.success_criteria.append(criterion)

    def evaluate_success(self) -> tuple[bool, str]:
        """
        Evaluate pilot success.

        Returns:
            Tuple of (passed, summary)
        """
        passed_count = sum(1 for c in self.success_criteria if c.passed)
        total = len(self.success_criteria)

        # Check critical criteria
        accuracy_passed = any(
            c.criterion == "Cross-modal accuracy" and c.passed
            for c in self.success_criteria
        )
        latency_passed = any(
            c.criterion == "Inference latency (p95)" and c.passed
            for c in self.success_criteria
        )

        if passed_count >= 6 and accuracy_passed and latency_passed:
            return (True, f"PASS: {passed_count}/{total} criteria met, including accuracy and latency")
        elif passed_count >= 5:
            return (False, f"CONDITIONAL PASS: {passed_count}/{total} criteria met")
        else:
            return (False, f"FAIL: {passed_count}/{total} criteria met")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "sow_id": self.sow_id,
            "provider": self.provider,
            "partner": self.partner,
            "effective_date": self.effective_date.isoformat(),
            "duration_weeks": self.duration_weeks,
            "deliverables": [d.to_dict() for d in self.deliverables],
            "success_criteria": [c.to_dict() for c in self.success_criteria],
            "phases": self.phases,
            "success_evaluation": self.evaluate_success(),
        }

    @classmethod
    def create_template(cls, partner_name: str) -> PilotSOW:
        """
        Create a pilot SOW template.

        Args:
            partner_name: Partner organization name

        Returns:
            PilotSOW template
        """
        sow = cls(
            sow_id=f"SOW-TG-{datetime.now().year}-001",
            provider="[YOUR_ORGANIZATION]",
            partner=partner_name,
            effective_date=datetime.now(),
            duration_weeks=10,
        )

        # Add default deliverables
        default_deliverables = [
            PilotDeliverable(
                id="D1",
                description="Deployed model endpoint",
                owner="Provider",
                due_week=2,
                acceptance_criteria="Endpoint responds with < 100ms p95 latency",
            ),
            PilotDeliverable(
                id="D2",
                description="Integration guide",
                owner="Provider",
                due_week=2,
                acceptance_criteria="Document covers authentication, API schema, error handling",
            ),
            PilotDeliverable(
                id="D3",
                description="Integration implementation",
                owner="Partner",
                due_week=4,
                acceptance_criteria="Partner system sends queries to endpoint",
            ),
            PilotDeliverable(
                id="D4",
                description="Benchmark dataset",
                owner="Partner",
                due_week=4,
                acceptance_criteria="1000+ labeled samples covering use cases",
            ),
            PilotDeliverable(
                id="D5",
                description="Benchmark results report",
                owner="Provider",
                due_week=8,
                acceptance_criteria="Cross-modal accuracy, latency, and throughput",
            ),
            PilotDeliverable(
                id="D7",
                description="Final pilot report",
                owner="Provider",
                due_week=10,
                acceptance_criteria="Full scorecard, recommendations, next steps",
            ),
        ]

        for d in default_deliverables:
            sow.add_deliverable(d)

        # Add default success criteria
        default_criteria = [
            PilotSuccessCriteria(
                criterion="Cross-modal accuracy",
                metric="M-CM-001",
                target=">= 70%",
                measurement_method="Eval harness on benchmark data",
            ),
            PilotSuccessCriteria(
                criterion="Inference latency (p95)",
                metric="M-LAT-002",
                target="<= 100ms",
                measurement_method="Load test during monitored operation",
            ),
            PilotSuccessCriteria(
                criterion="Throughput",
                metric="M-THR-001",
                target=">= 100 QPS",
                measurement_method="Load test during monitored operation",
            ),
            PilotSuccessCriteria(
                criterion="Uptime",
                metric="availability",
                target=">= 99.0%",
                measurement_method="Monitoring dashboard",
            ),
            PilotSuccessCriteria(
                criterion="Safety",
                metric="M-SAF-001",
                target="<= 0.1% violation rate",
                measurement_method="Safety classifier",
            ),
        ]

        for c in default_criteria:
            sow.add_success_criterion(c)

        # Add phases
        sow.phases = {
            PilotPhase.SETUP: {
                "weeks": "1-2",
                "activities": ["Deployment", "Integration guide", "Environment configuration"],
            },
            PilotPhase.INTEGRATION: {
                "weeks": "3-4",
                "activities": ["Partner integration", "Testing", "Benchmark dataset preparation"],
            },
            PilotPhase.MONITORED_OPERATION: {
                "weeks": "5-8",
                "activities": ["Live operation", "Performance monitoring", "Weekly reports"],
            },
            PilotPhase.EVALUATION: {
                "weeks": "9-10",
                "activities": ["Final benchmarking", "Scorecard completion", "Pilot report"],
            },
        }

        return sow
