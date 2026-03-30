"""
Compute Budget — Budget tracking, alerts, and cost governance.

This module implements compute budget management with real-time tracking,
alert thresholds, and cost attribution for the Theta-Gamma pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class BudgetCategory(str, Enum):
    """
    Budget categories for cost attribution.

    Each compute action is attributed to a category for tracking.
    """

    TRAINING = "training"
    EVAL = "eval"
    PERF = "perf"
    INFRA = "infra"
    CI = "ci"
    RESERVE = "reserve"


@dataclass
class CostEvent:
    """
    A cost event for tracking compute spend.

    Attributes:
        timestamp: Event timestamp
        action_type: Type of compute action
        resource: Resource description (e.g., "gpu_type:count x hours")
        estimated_cost_usd: Estimated cost in USD
        cumulative_daily_usd: Cumulative daily spend after this event
        cumulative_monthly_usd: Cumulative monthly spend after this event
        experiment_id: Associated experiment ID
        budget_category: Budget category for attribution
    """

    timestamp: datetime
    action_type: str
    resource: str
    estimated_cost_usd: float
    cumulative_daily_usd: float
    cumulative_monthly_usd: float
    experiment_id: str
    budget_category: BudgetCategory

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "action_type": self.action_type,
            "resource": self.resource,
            "estimated_cost_usd": self.estimated_cost_usd,
            "cumulative_daily_usd": self.cumulative_daily_usd,
            "cumulative_monthly_usd": self.cumulative_monthly_usd,
            "experiment_id": self.experiment_id,
            "budget_category": self.budget_category.value,
        }


@dataclass
class BudgetAlert:
    """
    A budget alert.

    Attributes:
        level: Alert level (info, warning, critical, kill)
        trigger_pct: Percentage of cap that triggered
        message: Alert message
        triggered_at: Alert timestamp
        acknowledged: Whether alert was acknowledged
    """

    level: str
    trigger_pct: float
    message: str
    triggered_at: datetime
    acknowledged: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "level": self.level,
            "trigger_pct": self.trigger_pct,
            "message": self.message,
            "triggered_at": self.triggered_at.isoformat(),
            "acknowledged": self.acknowledged,
        }


class BudgetPolicy:
    """
    Budget policy configuration.

    Defines budget caps, alert thresholds, and allocation by category.
    """

    def __init__(
        self,
        monthly_cap_usd: float = 500.0,
        daily_cap_usd: float = 50.0,
        single_action_cap_usd: float = 50.0,
        alert_threshold_pct: float = 80.0,
    ) -> None:
        """
        Initialize budget policy.

        Args:
            monthly_cap_usd: Monthly compute budget cap
            daily_cap_usd: Daily compute budget cap
            single_action_cap_usd: Maximum cost for single action
            alert_threshold_pct: Percentage of cap for alerts
        """
        self.monthly_cap_usd = monthly_cap_usd
        self.daily_cap_usd = daily_cap_usd
        self.single_action_cap_usd = single_action_cap_usd
        self.alert_threshold_pct = alert_threshold_pct

        # Budget allocation by category
        self.allocations: dict[BudgetCategory, float] = {
            BudgetCategory.TRAINING: 300.0,  # 60%
            BudgetCategory.EVAL: 75.0,  # 15%
            BudgetCategory.PERF: 50.0,  # 10%
            BudgetCategory.INFRA: 40.0,  # 8%
            BudgetCategory.CI: 25.0,  # 5%
            BudgetCategory.RESERVE: 10.0,  # 2%
        }

    def get_allocation(self, category: BudgetCategory) -> float:
        """Get allocation for a category."""
        return self.allocations.get(category, 0.0)

    def can_spend(self, amount_usd: float, category: BudgetCategory) -> bool:
        """
        Check if spending is allowed.

        Args:
            amount_usd: Amount to spend
            category: Budget category

        Returns:
            True if spending is allowed
        """
        if amount_usd > self.single_action_cap_usd:
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "monthly_cap_usd": self.monthly_cap_usd,
            "daily_cap_usd": self.daily_cap_usd,
            "single_action_cap_usd": self.single_action_cap_usd,
            "alert_threshold_pct": self.alert_threshold_pct,
            "allocations": {k.value: v for k, v in self.allocations.items()},
        }

    @classmethod
    def load_default(cls) -> "BudgetPolicy":
        """Load the default budget policy."""
        return cls()

    @classmethod
    def load_from_yaml(cls, path: Path | str) -> "BudgetPolicy":
        """
        Load budget policy from YAML file.

        Args:
            path: Path to YAML file (e.g., A2/05_budget_guardrails.yaml)

        Returns:
            BudgetPolicy instance
        """
        path = Path(path)
        with open(path) as f:
            data = yaml.safe_load(f)

        return cls(
            monthly_cap_usd=data.get("monthly_cap_usd", 500.0),
            daily_cap_usd=data.get("daily_cap_usd", 50.0),
            single_action_cap_usd=data.get("single_action_cap_usd", 50.0),
            alert_threshold_pct=data.get("alert_thresholds", {}).get("monthly", [{}])[0].get("percent", 80.0) * 100 if isinstance(data.get("alert_thresholds"), dict) else 80.0,
        )


class ComputeBudget:
    """
    Compute budget tracker and governor.

    Tracks real-time spend, enforces caps, and generates alerts.

    Example:
        >>> budget = ComputeBudget()
        >>> budget.record_cost(25.0, "training", "exp-001")
        >>> if budget.is_over_daily_cap():
        ...     halt_all_compute()
    """

    def __init__(
        self,
        policy: BudgetPolicy | None = None,
        budget_month_start: datetime | None = None,
    ) -> None:
        """
        Initialize compute budget.

        Args:
            policy: Budget policy configuration
            budget_month_start: Start of current budget month
        """
        self.policy = policy or BudgetPolicy()
        self._month_start = budget_month_start or self._get_current_month_start()
        self._daily_spend: float = 0.0
        self._monthly_spend: float = 0.0
        self._category_spend: dict[BudgetCategory, float] = {cat: 0.0 for cat in BudgetCategory}
        self._events: list[CostEvent] = []
        self._alerts: list[BudgetAlert] = []
        self._experiment_costs: dict[str, float] = {}

    def _get_current_month_start(self) -> datetime:
        """Get the start of the current calendar month."""
        now = datetime.now()
        return datetime(now.year, now.month, 1)

    def record_cost(
        self,
        cost_usd: float,
        action_type: str,
        experiment_id: str,
        resource: str = "",
        category: BudgetCategory = BudgetCategory.TRAINING,
    ) -> CostEvent:
        """
        Record a cost event.

        Args:
            cost_usd: Cost in USD
            action_type: Type of action
            experiment_id: Experiment ID
            resource: Resource description
            category: Budget category

        Returns:
            Recorded CostEvent
        """
        # Check if we've crossed into a new month
        self._check_month_boundary()

        # Update spend tracking
        self._daily_spend += cost_usd
        self._monthly_spend += cost_usd
        self._category_spend[category] = self._category_spend.get(category, 0.0) + cost_usd
        self._experiment_costs[experiment_id] = (
            self._experiment_costs.get(experiment_id, 0.0) + cost_usd
        )

        # Create event
        event = CostEvent(
            timestamp=datetime.now(),
            action_type=action_type,
            resource=resource,
            estimated_cost_usd=cost_usd,
            cumulative_daily_usd=self._daily_spend,
            cumulative_monthly_usd=self._monthly_spend,
            experiment_id=experiment_id,
            budget_category=category,
        )
        self._events.append(event)

        # Check for alerts
        self._check_alerts()

        return event

    def _check_month_boundary(self) -> None:
        """Check if we've crossed into a new month and reset if needed."""
        current_month_start = self._get_current_month_start()
        if current_month_start > self._month_start:
            # New month - reset daily spend
            self._month_start = current_month_start
            self._daily_spend = 0.0

    def _check_alerts(self) -> None:
        """Check for budget alerts and generate if needed."""
        daily_pct = (self._daily_spend / self.policy.daily_cap_usd) * 100
        monthly_pct = (self._monthly_spend / self.policy.monthly_cap_usd) * 100

        self._generate_alerts(daily_pct, "daily", self.policy.daily_cap_usd)
        self._generate_alerts(monthly_pct, "monthly", self.policy.monthly_cap_usd)

    def _generate_alerts(
        self, pct: float, period: str, cap_usd: float
    ) -> None:
        """Generate alerts based on percentage of cap."""
        thresholds = [
            (60.0, "info"),
            (80.0, "warning"),
            (96.0, "critical"),
            (100.0, "kill"),
        ]

        for threshold_pct, level in thresholds:
            if pct >= threshold_pct:
                # Check if we already have this alert
                existing = any(
                    a.level == level
                    and a.trigger_pct == threshold_pct
                    and period in a.message.lower()
                    for a in self._alerts
                )
                if not existing:
                    spend = self._daily_spend if period == "daily" else self._monthly_spend
                    alert = BudgetAlert(
                        level=level,
                        trigger_pct=threshold_pct,
                        message=f"{period.capitalize()} spend ${spend:.2f}/{cap_usd:.2f} ({pct:.1f}%) - {level.upper()}",
                        triggered_at=datetime.now(),
                    )
                    self._alerts.append(alert)

    def is_over_daily_cap(self) -> bool:
        """Check if over daily cap."""
        return self._daily_spend >= self.policy.daily_cap_usd

    def is_over_monthly_cap(self) -> bool:
        """Check if over monthly cap."""
        return self._monthly_spend >= self.policy.monthly_cap_usd

    def get_daily_remaining(self) -> float:
        """Get remaining daily budget."""
        return max(0.0, self.policy.daily_cap_usd - self._daily_spend)

    def get_monthly_remaining(self) -> float:
        """Get remaining monthly budget."""
        return max(0.0, self.policy.monthly_cap_usd - self._monthly_spend)

    def get_daily_pct_used(self) -> float:
        """Get percentage of daily budget used."""
        return (self._daily_spend / self.policy.daily_cap_usd) * 100

    def get_monthly_pct_used(self) -> float:
        """Get percentage of monthly budget used."""
        return (self._monthly_spend / self.policy.monthly_cap_usd) * 100

    def get_runway_days(self) -> float:
        """
        Calculate runway in days at current burn rate.

        Returns:
            Days of runway remaining
        """
        if self._monthly_spend == 0:
            return float("inf")

        days_elapsed = (datetime.now() - self._month_start).days + 1
        if days_elapsed <= 0:
            days_elapsed = 1

        daily_burn = self._monthly_spend / days_elapsed
        remaining = self.get_monthly_remaining()

        if daily_burn <= 0:
            return float("inf")

        return remaining / daily_burn

    def get_experiment_cost(self, experiment_id: str) -> float:
        """Get total cost for an experiment."""
        return self._experiment_costs.get(experiment_id, 0.0)

    def get_category_spend(self, category: BudgetCategory) -> float:
        """Get spend for a category."""
        return self._category_spend.get(category, 0.0)

    def get_alerts(self, unacknowledged_only: bool = False) -> list[BudgetAlert]:
        """Get budget alerts."""
        if unacknowledged_only:
            return [a for a in self._alerts if not a.acknowledged]
        return self._alerts.copy()

    def acknowledge_alert(self, alert: BudgetAlert) -> None:
        """Acknowledge an alert."""
        alert.acknowledged = True

    def get_cost_per_point(
        self, experiment_id: str, accuracy_delta_pp: float
    ) -> float:
        """
        Calculate cost per percentage point of accuracy improvement.

        Args:
            experiment_id: Experiment ID
            accuracy_delta_pp: Accuracy delta in percentage points

        Returns:
            Cost per point
        """
        if accuracy_delta_pp <= 0:
            return float("inf")

        cost = self.get_experiment_cost(experiment_id)
        return cost / accuracy_delta_pp

    def get_events(
        self,
        experiment_id: str | None = None,
        category: BudgetCategory | None = None,
    ) -> list[CostEvent]:
        """Get cost events, optionally filtered."""
        events = self._events.copy()

        if experiment_id:
            events = [e for e in events if e.experiment_id == experiment_id]
        if category:
            events = [e for e in events if e.budget_category == category]

        return events

    def get_summary(self) -> dict[str, Any]:
        """Get budget summary."""
        return {
            "daily_spend": self._daily_spend,
            "monthly_spend": self._monthly_spend,
            "daily_cap": self.policy.daily_cap_usd,
            "monthly_cap": self.policy.monthly_cap_usd,
            "daily_pct_used": self.get_daily_pct_used(),
            "monthly_pct_used": self.get_monthly_pct_used(),
            "daily_remaining": self.get_daily_remaining(),
            "monthly_remaining": self.get_monthly_remaining(),
            "runway_days": self.get_runway_days(),
            "alerts_count": len(self._alerts),
            "unacknowledged_alerts": len(
                [a for a in self._alerts if not a.acknowledged]
            ),
            "category_spend": {k.value: v for k, v in self._category_spend.items()},
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "policy": self.policy.to_dict(),
            "summary": self.get_summary(),
            "recent_events": [e.to_dict() for e in self._events[-10:]],
            "alerts": [a.to_dict() for a in self._alerts],
        }
