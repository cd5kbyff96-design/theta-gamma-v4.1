"""
Operating Limits — Defines hard limits and kill-switches for autonomous operation.

This module implements the operating limits that govern compute spend,
alert thresholds, and kill-switch mechanisms for the Theta-Gamma pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class KillSwitchType(str, Enum):
    """
    Kill-switch types for autonomous operation.

    Kill-switches are non-negotiable hard stops that cannot be
    overridden autonomously.
    """

    DAILY = "KS-DAILY"
    MONTHLY = "KS-MONTHLY"
    RUNAWAY = "KS-RUNAWAY"
    DURATION = "KS-DURATION"
    REGRESSION = "KS-REGRESSION"
    ORPHAN = "KS-ORPHAN"


@dataclass
class CostAlertThreshold:
    """
    A cost alert threshold configuration.

    Attributes:
        level: Alert level (info, warning, critical, kill)
        trigger_pct: Percentage of cap that triggers the alert
        action: Action to take when triggered
    """

    level: str
    trigger_pct: float
    action: str


@dataclass
class KillSwitch:
    """
    A kill-switch configuration.

    Attributes:
        type: Kill-switch type
        trigger: Condition that triggers the kill-switch
        effect: What happens when triggered
        restart_requires: What is required to restart
    """

    type: KillSwitchType
    trigger: str
    effect: str
    restart_requires: str
    is_active: bool = True
    tripped_at: datetime | None = None

    def trip(self) -> None:
        """Trip the kill-switch."""
        self.is_active = False
        self.tripped_at = datetime.now()

    def reset(self) -> None:
        """Reset the kill-switch."""
        self.is_active = True
        self.tripped_at = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "type": self.type.value,
            "trigger": self.trigger,
            "effect": self.effect,
            "restart_requires": self.restart_requires,
            "is_active": self.is_active,
            "tripped_at": self.tripped_at.isoformat() if self.tripped_at else None,
        }


class OperatingLimits:
    """
    Operating limits for the Theta-Gamma pipeline.

    The limits define:
    - Budget envelope (monthly, daily, single-action caps)
    - Alert thresholds (info, warning, critical, kill)
    - Kill-switches (hard stops that cannot be overridden autonomously)
    - Experiment governance (max runtime, cost attribution)

    Example:
        >>> limits = OperatingLimits()
        >>> if limits.is_kill_switch_triggered("KS-DAILY"):
        ...     halt_all_compute()
    """

    def __init__(
        self,
        monthly_compute_cap_usd: float = 500.0,
        daily_compute_cap_usd: float = 50.0,
        single_action_cap_usd: float = 50.0,
        alert_threshold_pct: float = 80.0,
        max_experiment_runtime_hours: float = 24.0,
        ephemeral_env_max_lifetime_hours: float = 8.0,
        ephemeral_env_idle_timeout_hours: float = 4.0,
        max_internal_notifications_per_hour: int = 20,
        max_ci_retries_per_job: int = 3,
    ) -> None:
        """
        Initialize operating limits.

        Args:
            monthly_compute_cap_usd: Monthly compute budget cap
            daily_compute_cap_usd: Daily compute budget cap
            single_action_cap_usd: Maximum cost for single autonomous action
            alert_threshold_pct: Percentage of cap that triggers alert
            max_experiment_runtime_hours: Maximum experiment runtime
            ephemeral_env_max_lifetime_hours: Max lifetime for ephemeral environments
            ephemeral_env_idle_timeout_hours: Idle timeout for ephemeral environments
            max_internal_notifications_per_hour: Max notifications per hour
            max_ci_retries_per_job: Max CI retries per job
        """
        self.monthly_compute_cap_usd = monthly_compute_cap_usd
        self.daily_compute_cap_usd = daily_compute_cap_usd
        self.single_action_cap_usd = single_action_cap_usd
        self.alert_threshold_pct = alert_threshold_pct
        self.max_experiment_runtime_hours = max_experiment_runtime_hours
        self.ephemeral_env_max_lifetime_hours = ephemeral_env_max_lifetime_hours
        self.ephemeral_env_idle_timeout_hours = ephemeral_env_idle_timeout_hours
        self.max_internal_notifications_per_hour = max_internal_notifications_per_hour
        self.max_ci_retries_per_job = max_ci_retries_per_job

        # Alert thresholds
        self._daily_alerts: list[CostAlertThreshold] = [
            CostAlertThreshold(
                level="info",
                trigger_pct=60.0,
                action="Log to dashboard",
            ),
            CostAlertThreshold(
                level="warning",
                trigger_pct=80.0,
                action="Notify team channel",
            ),
            CostAlertThreshold(
                level="critical",
                trigger_pct=96.0,
                action="Auto-pause non-essential jobs",
            ),
            CostAlertThreshold(
                level="kill",
                trigger_pct=100.0,
                action="Hard-stop ALL compute",
            ),
        ]

        self._monthly_alerts: list[CostAlertThreshold] = [
            CostAlertThreshold(
                level="info",
                trigger_pct=60.0,
                action="Log to dashboard",
            ),
            CostAlertThreshold(
                level="warning",
                trigger_pct=80.0,
                action="Notify team + trigger downgrade eval",
            ),
            CostAlertThreshold(
                level="critical",
                trigger_pct=95.0,
                action="Auto-downgrade to cheapest tier",
            ),
            CostAlertThreshold(
                level="kill",
                trigger_pct=100.0,
                action="Hard-stop ALL compute for month",
            ),
        ]

        # Kill-switches
        self._kill_switches: dict[KillSwitchType, KillSwitch] = {}
        self._initialize_kill_switches()

    def _initialize_kill_switches(self) -> None:
        """Initialize default kill-switches."""
        switches = [
            KillSwitch(
                type=KillSwitchType.DAILY,
                trigger="Daily spend >= $50",
                effect="Terminate all running jobs, block new launches",
                restart_requires="Human approval + next calendar day",
            ),
            KillSwitch(
                type=KillSwitchType.MONTHLY,
                trigger="Monthly spend >= $500",
                effect="Terminate all running jobs for remainder of month",
                restart_requires="Human approval + budget amendment",
            ),
            KillSwitch(
                type=KillSwitchType.RUNAWAY,
                trigger="Single experiment > $50",
                effect="Terminate that experiment",
                restart_requires="Human approval + cost justification",
            ),
            KillSwitch(
                type=KillSwitchType.DURATION,
                trigger="Any job running > 24h",
                effect="Terminate that job",
                restart_requires="Human approval + runtime extension justification",
            ),
            KillSwitch(
                type=KillSwitchType.REGRESSION,
                trigger="Cost per gate-progress-point > 3x historical average",
                effect="Pause training pipeline",
                restart_requires="Human review of training efficiency",
            ),
            KillSwitch(
                type=KillSwitchType.ORPHAN,
                trigger="> $20 cumulative orphan compute in a day",
                effect="Block new unattributed jobs",
                restart_requires="Assign experiment_ids to orphaned jobs",
            ),
        ]

        for switch in switches:
            self._kill_switches[switch.type] = switch

    def get_daily_alert_action(self, spend_usd: float) -> str:
        """
        Get the alert action for current daily spend.

        Args:
            spend_usd: Current daily spend in USD

        Returns:
            Alert action string
        """
        pct = (spend_usd / self.daily_compute_cap_usd) * 100

        for threshold in reversed(self._daily_alerts):
            if pct >= threshold.trigger_pct:
                return threshold.action

        return "No action"

    def get_monthly_alert_action(self, spend_usd: float) -> str:
        """
        Get the alert action for current monthly spend.

        Args:
            spend_usd: Current monthly spend in USD

        Returns:
            Alert action string
        """
        pct = (spend_usd / self.monthly_compute_cap_usd) * 100

        for threshold in reversed(self._monthly_alerts):
            if pct >= threshold.trigger_pct:
                return threshold.action

        return "No action"

    def is_kill_switch_triggered(self, switch_type: KillSwitchType) -> bool:
        """
        Check if a kill-switch is triggered.

        Args:
            switch_type: The kill-switch type to check

        Returns:
            True if the kill-switch is triggered
        """
        switch = self._kill_switches.get(switch_type)
        return switch is not None and not switch.is_active

    def trip_kill_switch(self, switch_type: KillSwitchType) -> None:
        """
        Trip a kill-switch.

        Args:
            switch_type: The kill-switch type to trip
        """
        switch = self._kill_switches.get(switch_type)
        if switch:
            switch.trip()

    def reset_kill_switch(self, switch_type: KillSwitchType) -> None:
        """
        Reset a kill-switch.

        Args:
            switch_type: The kill-switch type to reset
        """
        switch = self._kill_switches.get(switch_type)
        if switch:
            switch.reset()

    def get_all_kill_switches(self) -> list[KillSwitch]:
        """Get all kill-switches."""
        return list(self._kill_switches.values())

    def check_experiment_budget(
        self, estimated_cost_usd: float, estimated_runtime_hours: float
    ) -> tuple[bool, str]:
        """
        Check if an experiment is within budget limits.

        Args:
            estimated_cost_usd: Estimated cost of the experiment
            estimated_runtime_hours: Estimated runtime in hours

        Returns:
            Tuple of (is_within_budget, reason)
        """
        if estimated_cost_usd > self.single_action_cap_usd:
            return (
                False,
                f"Estimated cost ${estimated_cost_usd:.2f} exceeds single action cap ${self.single_action_cap_usd:.2f}",
            )

        if estimated_runtime_hours > self.max_experiment_runtime_hours:
            return (
                False,
                f"Estimated runtime {estimated_runtime_hours}h exceeds max {self.max_experiment_runtime_hours}h",
            )

        return (True, "Within budget limits")

    def get_kill_switch_status(self) -> dict[str, Any]:
        """Get status of all kill-switches."""
        return {
            switch.type.value: {
                "is_active": switch.is_active,
                "tripped_at": switch.tripped_at.isoformat() if switch.tripped_at else None,
            }
            for switch in self._kill_switches.values()
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "monthly_compute_cap_usd": self.monthly_compute_cap_usd,
            "daily_compute_cap_usd": self.daily_compute_cap_usd,
            "single_action_cap_usd": self.single_action_cap_usd,
            "alert_threshold_pct": self.alert_threshold_pct,
            "max_experiment_runtime_hours": self.max_experiment_runtime_hours,
            "ephemeral_env_max_lifetime_hours": self.ephemeral_env_max_lifetime_hours,
            "ephemeral_env_idle_timeout_hours": self.ephemeral_env_idle_timeout_hours,
            "max_internal_notifications_per_hour": self.max_internal_notifications_per_hour,
            "max_ci_retries_per_job": self.max_ci_retries_per_job,
            "daily_alerts": [
                {"level": a.level, "trigger_pct": a.trigger_pct, "action": a.action}
                for a in self._daily_alerts
            ],
            "monthly_alerts": [
                {"level": a.level, "trigger_pct": a.trigger_pct, "action": a.action}
                for a in self._monthly_alerts
            ],
            "kill_switches": [switch.to_dict() for switch in self._kill_switches.values()],
        }

    @classmethod
    def load_default(cls) -> "OperatingLimits":
        """Load the default operating limits."""
        return cls()

    @classmethod
    def load_from_yaml(cls, path: Path | str) -> "OperatingLimits":
        """
        Load operating limits from YAML file.

        Args:
            path: Path to YAML file (e.g., A0/02_operating_limits.yaml)

        Returns:
            OperatingLimits instance
        """
        path = Path(path)
        with open(path) as f:
            data = yaml.safe_load(f)

        return cls(
            monthly_compute_cap_usd=data.get("monthly_compute_cap_usd", 500.0),
            daily_compute_cap_usd=data.get("daily_compute_cap_usd", 50.0),
            single_action_cap_usd=data.get("single_action_cap_usd", 50.0),
            alert_threshold_pct=data.get("cost_alert_threshold_pct", 80.0),
            max_experiment_runtime_hours=data.get("max_experiment_runtime_hours", 24.0),
            ephemeral_env_max_lifetime_hours=data.get("ephemeral_env_max_lifetime_hours", 8.0),
            ephemeral_env_idle_timeout_hours=data.get("ephemeral_env_idle_timeout_hours", 4.0),
            max_internal_notifications_per_hour=data.get("max_internal_notifications_per_hour", 20),
            max_ci_retries_per_job=data.get("max_ci_retries_per_job", 3),
        )
