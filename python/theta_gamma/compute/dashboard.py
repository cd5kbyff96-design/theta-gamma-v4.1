"""
Runway & Burn Dashboard — Real-time budget visibility.

This module implements the runway and burn dashboard that provides
real-time visibility into compute spend, projected runway, and gate progress.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class PanelType(str, Enum):
    """Dashboard panel types."""

    BUDGET_GAUGE = "budget_gauge"
    BURN_RATE_CHART = "burn_rate_chart"
    RUNWAY_COUNTER = "runway_counter"
    GATE_PROGRESS = "gate_progress"
    TIER_STATUS = "tier_status"
    KILL_SWITCH_STATUS = "kill_switch_status"
    ALERT_FEED = "alert_feed"


@dataclass
class DashboardPanel:
    """
    A dashboard panel configuration.

    Attributes:
        panel_type: Type of panel
        name: Panel name
        refresh_rate_seconds: How often to refresh
        data: Panel data
    """

    panel_type: PanelType
    name: str
    refresh_rate_seconds: int
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "panel_type": self.panel_type.value,
            "name": self.name,
            "refresh_rate_seconds": self.refresh_rate_seconds,
            "data": self.data,
        }


@dataclass
class BudgetGauge:
    """
    Budget gauge panel data.

    Attributes:
        monthly_spend: Current monthly spend
        monthly_cap: Monthly budget cap
        daily_spend: Current daily spend
        daily_cap: Daily budget cap
        category_breakdown: Spend by category
    """

    monthly_spend: float
    monthly_cap: float
    daily_spend: float
    daily_cap: float
    category_breakdown: dict[str, float]

    def get_monthly_pct(self) -> float:
        """Get monthly percentage used."""
        return (self.monthly_spend / self.monthly_cap) * 100 if self.monthly_cap > 0 else 0

    def get_daily_pct(self) -> float:
        """Get daily percentage used."""
        return (self.daily_spend / self.daily_cap) * 100 if self.daily_cap > 0 else 0

    def get_color_zone(self, pct: float) -> str:
        """Get color zone for percentage."""
        if pct < 60:
            return "green"
        elif pct < 80:
            return "yellow"
        elif pct < 95:
            return "orange"
        else:
            return "red"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "monthly": {
                "spend": self.monthly_spend,
                "cap": self.monthly_cap,
                "pct": self.get_monthly_pct(),
                "zone": self.get_color_zone(self.get_monthly_pct()),
            },
            "daily": {
                "spend": self.daily_spend,
                "cap": self.daily_cap,
                "pct": self.get_daily_pct(),
                "zone": self.get_color_zone(self.get_daily_pct()),
            },
            "category_breakdown": self.category_breakdown,
        }


@dataclass
class BurnRateChart:
    """
    Burn rate chart panel data.

    Attributes:
        daily_spends: List of daily spend values
        projected_month_end: Projected month-end spend
        threshold_lines: Budget threshold lines
    """

    daily_spends: list[float]
    projected_month_end: float
    threshold_lines: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "daily_spends": self.daily_spends,
            "projected_month_end": self.projected_month_end,
            "threshold_lines": self.threshold_lines,
        }


@dataclass
class RunwayCounter:
    """
    Runway counter panel data.

    Attributes:
        days_remaining: Days of runway remaining
        burn_rate_7d: 7-day average burn rate
        projected_exhaustion_date: Date when budget will be exhausted
        tier_adjusted_runway: Runway at different tiers
    """

    days_remaining: float
    burn_rate_7d: float
    projected_exhaustion_date: datetime | None
    tier_adjusted_runway: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "days_remaining": self.days_remaining,
            "burn_rate_7d": self.burn_rate_7d,
            "projected_exhaustion_date": (
                self.projected_exhaustion_date.isoformat()
                if self.projected_exhaustion_date
                else None
            ),
            "tier_adjusted_runway": self.tier_adjusted_runway,
        }


class RunwayDashboard:
    """
    Main runway and burn dashboard.

    Provides real-time visibility into compute spend, runway, and
    gate progress.

    Example:
        >>> dashboard = RunwayDashboard()
        >>> dashboard.update_spend(350.0, 42.0)
        >>> gauge = dashboard.get_budget_gauge()
        >>> print(f"Monthly: {gauge.get_monthly_pct():.1f}%")
    """

    def __init__(
        self,
        monthly_cap_usd: float = 500.0,
        daily_cap_usd: float = 50.0,
        month_start: datetime | None = None,
    ) -> None:
        """
        Initialize the dashboard.

        Args:
            monthly_cap_usd: Monthly budget cap
            daily_cap_usd: Daily budget cap
            month_start: Start of current budget month
        """
        self.monthly_cap_usd = monthly_cap_usd
        self.daily_cap_usd = daily_cap_usd
        self._month_start = month_start or datetime.now().replace(day=1)

        self._monthly_spend: float = 0.0
        self._daily_spend: float = 0.0
        self._daily_history: list[tuple[datetime, float]] = []
        self._category_spend: dict[str, float] = {}
        self._alerts: list[dict[str, Any]] = []
        self._tier_status: str = "T1-Full-FSDP"
        self._kill_switches: dict[str, dict[str, Any]] = {}
        self._gate_progress: dict[str, dict[str, Any]] = {}

        self._initialize_kill_switches()

    def _initialize_kill_switches(self) -> None:
        """Initialize kill-switch status tracking."""
        switch_types = [
            "KS-DAILY",
            "KS-MONTHLY",
            "KS-RUNAWAY",
            "KS-DURATION",
            "KS-REGRESSION",
            "KS-ORPHAN",
        ]
        for switch_type in switch_types:
            self._kill_switches[switch_type] = {
                "is_active": True,
                "tripped_at": None,
                "proximity_pct": 0,
            }

    def update_spend(
        self,
        monthly_spend: float,
        daily_spend: float,
        category_spend: dict[str, float] | None = None,
    ) -> None:
        """
        Update spend tracking.

        Args:
            monthly_spend: Monthly spend in USD
            daily_spend: Daily spend in USD
            category_spend: Spend by category
        """
        self._monthly_spend = monthly_spend
        self._daily_spend = daily_spend

        if category_spend:
            self._category_spend = category_spend

        # Track daily history
        self._daily_history.append((datetime.now(), daily_spend))

        # Keep last 30 days
        if len(self._daily_history) > 30:
            self._daily_history = self._daily_history[-30:]

        # Update kill-switch proximity
        self._update_kill_switch_proximity()

    def _update_kill_switch_proximity(self) -> None:
        """Update kill-switch proximity indicators."""
        monthly_pct = (self._monthly_spend / self.monthly_cap_usd) * 100
        daily_pct = (self._daily_spend / self.daily_cap_usd) * 100

        self._kill_switches["KS-MONTHLY"]["proximity_pct"] = monthly_pct
        self._kill_switches["KS-DAILY"]["proximity_pct"] = daily_pct

    def add_alert(
        self, level: str, message: str, category: str = "budget"
    ) -> None:
        """
        Add an alert to the feed.

        Args:
            level: Alert level (info, warning, critical, kill)
            message: Alert message
            category: Alert category
        """
        self._alerts.append({
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "category": category,
            "message": message,
        })

        # Keep last 50 alerts
        if len(self._alerts) > 50:
            self._alerts = self._alerts[-50:]

    def update_gate_progress(
        self,
        gate_id: str,
        status: str,
        primary_metric: str,
        current_value: float,
        threshold: float,
    ) -> None:
        """
        Update gate progress.

        Args:
            gate_id: Gate identifier
            status: Gate status
            primary_metric: Primary metric name
            current_value: Current metric value
            threshold: Gate threshold
        """
        self._gate_progress[gate_id] = {
            "status": status,
            "primary_metric": primary_metric,
            "current_value": current_value,
            "threshold": threshold,
            "progress_pct": (current_value / threshold) * 100 if threshold > 0 else 0,
        }

    def update_tier_status(self, tier: str) -> None:
        """Update current tier status."""
        self._tier_status = tier

    def trip_kill_switch(self, switch_type: str) -> None:
        """Trip a kill-switch."""
        if switch_type in self._kill_switches:
            self._kill_switches[switch_type]["is_active"] = False
            self._kill_switches[switch_type]["tripped_at"] = datetime.now().isoformat()

    def get_budget_gauge(self) -> BudgetGauge:
        """Get budget gauge panel data."""
        return BudgetGauge(
            monthly_spend=self._monthly_spend,
            monthly_cap=self.monthly_cap_usd,
            daily_spend=self._daily_spend,
            daily_cap=self.daily_cap_usd,
            category_breakdown=self._category_spend.copy(),
        )

    def get_burn_rate_chart(self) -> BurnRateChart:
        """Get burn rate chart panel data."""
        daily_values = [spend for _, spend in self._daily_history]

        # Calculate projection
        if len(daily_values) >= 7:
            avg_burn = sum(daily_values[-7:]) / 7
        elif daily_values:
            avg_burn = sum(daily_values) / len(daily_values)
        else:
            avg_burn = 0

        days_in_month = (
            datetime.now().replace(day=1, month=datetime.now().month + 1) - datetime.now().replace(day=1)
        ).days
        days_elapsed = (datetime.now() - self._month_start).days + 1
        projected_month_end = self._monthly_spend + (avg_burn * (days_in_month - days_elapsed))

        threshold_lines = [
            {"value": self.monthly_cap_usd * 0.60, "label": "60%", "color": "green"},
            {"value": self.monthly_cap_usd * 0.80, "label": "80%", "color": "yellow"},
            {"value": self.monthly_cap_usd * 0.90, "label": "90%", "color": "orange"},
            {"value": self.monthly_cap_usd * 0.95, "label": "95%", "color": "red"},
            {"value": self.monthly_cap_usd, "label": "100%", "color": "dark_red"},
        ]

        return BurnRateChart(
            daily_spends=daily_values,
            projected_month_end=projected_month_end,
            threshold_lines=threshold_lines,
        )

    def get_runway_counter(self) -> RunwayCounter:
        """Get runway counter panel data."""
        # Calculate 7-day average burn
        if len(self._daily_history) >= 7:
            recent_spends = [s for _, s in self._daily_history[-7:]]
            burn_rate_7d = sum(recent_spends) / 7
        elif self._daily_history:
            burn_rate_7d = sum(s for _, s in self._daily_history) / len(
                self._daily_history
            )
        else:
            burn_rate_7d = 0

        # Calculate runway
        remaining = self.monthly_cap_usd - self._monthly_spend
        if burn_rate_7d > 0:
            days_remaining = remaining / burn_rate_7d
            projected_exhaustion = datetime.now() + timedelta(days=days_remaining)
        else:
            days_remaining = float("inf")
            projected_exhaustion = None

        # Tier-adjusted runway estimates
        tier_burn_rates = {
            "T1": burn_rate_7d,
            "T2": burn_rate_7d * 0.6,  # ~40% reduction
            "T3": burn_rate_7d * 0.3,  # ~70% reduction
            "T4": burn_rate_7d * 0.1,  # ~90% reduction
        }

        tier_adjusted = {
            tier: remaining / rate if rate > 0 else float("inf")
            for tier, rate in tier_burn_rates.items()
        }

        return RunwayCounter(
            days_remaining=days_remaining if days_remaining != float("inf") else 999,
            burn_rate_7d=burn_rate_7d,
            projected_exhaustion_date=projected_exhaustion,
            tier_adjusted_runway=tier_adjusted,
        )

    def get_tier_status_panel(self) -> dict[str, Any]:
        """Get tier status panel data."""
        return {
            "current_tier": self._tier_status,
            "time_in_tier": "Unknown",  # Would track in production
            "history": [],  # Would track in production
        }

    def get_kill_switch_panel(self) -> dict[str, Any]:
        """Get kill-switch status panel data."""
        return {"switches": self._kill_switches.copy()}

    def get_alert_feed(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent alerts."""
        return self._alerts[-limit:]

    def get_all_panels(self) -> list[DashboardPanel]:
        """Get all dashboard panels."""
        panels = [
            DashboardPanel(
                panel_type=PanelType.BUDGET_GAUGE,
                name="Budget Gauges",
                refresh_rate_seconds=60,
                data=self.get_budget_gauge().to_dict(),
            ),
            DashboardPanel(
                panel_type=PanelType.BURN_RATE_CHART,
                name="Burn Rate Chart",
                refresh_rate_seconds=300,
                data=self.get_burn_rate_chart().to_dict(),
            ),
            DashboardPanel(
                panel_type=PanelType.RUNWAY_COUNTER,
                name="Runway Counter",
                refresh_rate_seconds=300,
                data=self.get_runway_counter().to_dict(),
            ),
            DashboardPanel(
                panel_type=PanelType.TIER_STATUS,
                name="Tier Status",
                refresh_rate_seconds=60,
                data=self.get_tier_status_panel(),
            ),
            DashboardPanel(
                panel_type=PanelType.KILL_SWITCH_STATUS,
                name="Kill-Switch Status",
                refresh_rate_seconds=60,
                data=self.get_kill_switch_panel(),
            ),
            DashboardPanel(
                panel_type=PanelType.ALERT_FEED,
                name="Alert Feed",
                refresh_rate_seconds=10,
                data={"alerts": self.get_alert_feed()},
            ),
        ]

        # Add gate progress if available
        if self._gate_progress:
            panels.append(
                DashboardPanel(
                    panel_type=PanelType.GATE_PROGRESS,
                    name="Gate Progress vs Cost",
                    refresh_rate_seconds=60,
                    data={"gates": self._gate_progress},
                )
            )

        return panels

    def get_dashboard_summary(self) -> dict[str, Any]:
        """Get dashboard summary."""
        gauge = self.get_budget_gauge()
        runway = self.get_runway_counter()

        return {
            "budget": gauge.to_dict(),
            "runway": runway.to_dict(),
            "tier": self._tier_status,
            "alerts_count": len(self._alerts),
            "kill_switches": self.get_kill_switch_panel(),
            "gates": self._gate_progress,
            "generated_at": datetime.now().isoformat(),
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "monthly_cap_usd": self.monthly_cap_usd,
            "daily_cap_usd": self.daily_cap_usd,
            "summary": self.get_dashboard_summary(),
            "panels": [p.to_dict() for p in self.get_all_panels()],
        }
