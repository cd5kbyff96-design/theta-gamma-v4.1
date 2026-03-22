"""Tests for the compute module."""

import pytest

from theta_gamma.compute.budget import (
    ComputeBudget,
    BudgetPolicy,
    BudgetCategory,
)
from theta_gamma.compute.tiers import (
    TrainingTier,
    TierManager,
    TierConfig,
    GPUConfig,
    TierStrategy,
)
from theta_gamma.compute.downgrade import (
    DowngradeCascade,
    TransitionDirection,
)
from theta_gamma.compute.dashboard import (
    RunwayDashboard,
    BudgetGauge,
)


class TestBudgetPolicy:
    """Tests for BudgetPolicy."""

    def test_default_initialization(self):
        """Test default policy initialization."""
        policy = BudgetPolicy()

        assert policy.monthly_cap_usd == 500.0
        assert policy.daily_cap_usd == 50.0
        assert policy.single_action_cap_usd == 50.0

    def test_get_allocation(self):
        """Test getting category allocation."""
        policy = BudgetPolicy()

        training_alloc = policy.get_allocation(BudgetCategory.TRAINING)
        assert training_alloc == 300.0  # 60% of $500

    def test_can_spend(self):
        """Test spend permission checking."""
        policy = BudgetPolicy()

        # Within single action cap
        assert policy.can_spend(25.0, BudgetCategory.TRAINING) is True

        # Over single action cap
        assert policy.can_spend(60.0, BudgetCategory.TRAINING) is False


class TestComputeBudget:
    """Tests for ComputeBudget."""

    def test_record_cost(self):
        """Test cost recording."""
        budget = ComputeBudget()

        event = budget.record_cost(
            cost_usd=25.0,
            action_type="training",
            experiment_id="exp-001",
            category=BudgetCategory.TRAINING,
        )

        assert event.estimated_cost_usd == 25.0
        assert budget._daily_spend == 25.0
        assert budget._monthly_spend == 25.0

    def test_is_over_daily_cap(self):
        """Test daily cap checking."""
        budget = ComputeBudget()

        # Under cap
        budget.record_cost(25.0, "training", "exp-001")
        assert budget.is_over_daily_cap() is False

        # Over cap
        budget.record_cost(30.0, "training", "exp-002")
        assert budget.is_over_daily_cap() is True

    def test_get_remaining(self):
        """Test remaining budget calculation."""
        budget = ComputeBudget()

        budget.record_cost(25.0, "training", "exp-001")

        assert budget.get_daily_remaining() == 25.0  # 50 - 25
        assert budget.get_monthly_remaining() == 475.0  # 500 - 25

    def test_get_runway_days(self):
        """Test runway calculation."""
        budget = ComputeBudget()

        # Spend $100 over 5 days = $20/day burn
        for i in range(5):
            budget.record_cost(20.0, "training", f"exp-{i}")

        runway = budget.get_runway_days()
        # $400 remaining / $20 per day = 20 days
        assert runway > 0

    def test_get_alerts(self):
        """Test alert generation."""
        budget = ComputeBudget()

        # Spend enough to trigger warning (80% of daily = $40)
        budget.record_cost(45.0, "training", "exp-001")

        alerts = budget.get_alerts()
        assert len(alerts) > 0


class TestTrainingTier:
    """Tests for TrainingTier enum."""

    def test_tier_values(self):
        """Test tier enum values."""
        assert TrainingTier.T1_FULL_FSDP.value == "T1-Full-FSDP"
        assert TrainingTier.T5_FULL_STOP.value == "T5-Full-Stop"


class TestTierManager:
    """Tests for TierManager."""

    def test_default_tiers(self):
        """Test default tiers are initialized."""
        manager = TierManager()

        current = manager.get_current_tier()
        assert current == TrainingTier.T1_FULL_FSDP

    def test_get_tier_config(self):
        """Test getting tier configuration."""
        manager = TierManager()

        config = manager.get_tier_config(TrainingTier.T1_FULL_FSDP)
        assert config is not None
        assert config.gpu_config.count == 4

    def test_transition_to(self):
        """Test tier transitions."""
        manager = TierManager()

        # Transition from T1 to T2
        success, message = manager.transition_to(TrainingTier.T2_EFFICIENT)
        assert success is True
        assert manager.get_current_tier() == TrainingTier.T2_EFFICIENT

    def test_transition_blocked(self):
        """Test blocked tier transitions."""
        manager = TierManager()

        # Try to exit T5 (Full Stop) - should require human approval
        manager.transition_to(TrainingTier.T5_FULL_STOP)
        success, message = manager.transition_to(TrainingTier.T1_FULL_FSDP)
        assert success is False

    def test_get_downgrade_path(self):
        """Test downgrade path retrieval."""
        manager = TierManager()

        path = manager.get_downgrade_path()

        # T1 should downgrade to T2, T3, T4, T5
        assert TrainingTier.T2_EFFICIENT in path
        assert TrainingTier.T5_FULL_STOP in path


class TestDowngradeCascade:
    """Tests for DowngradeCascade."""

    def test_evaluate_downgrade_trigger(self):
        """Test downgrade trigger evaluation."""
        cascade = DowngradeCascade()

        # 85% monthly spend should trigger D1 downgrade from T1
        transition = cascade.evaluate_downgrade(
            monthly_spend_pct=0.85,
            daily_spend=45.0,
        )

        # Should trigger a downgrade
        assert transition is not None
        assert transition.direction == TransitionDirection.DOWNGRADE

    def test_no_downgrade_when_under_threshold(self):
        """Test no downgrade when under threshold."""
        cascade = DowngradeCascade()

        # 50% monthly spend should not trigger downgrade
        transition = cascade.evaluate_downgrade(
            monthly_spend_pct=0.50,
            daily_spend=20.0,
        )

        assert transition is None

    def test_execute_transition(self):
        """Test executing a transition."""
        cascade = DowngradeCascade()

        # Create a transition
        from theta_gamma.compute.downgrade import TierTransition
        from datetime import datetime

        transition = TierTransition(
            direction=TransitionDirection.DOWNGRADE,
            from_tier=TrainingTier.T1_FULL_FSDP,
            to_tier=TrainingTier.T2_EFFICIENT,
            rule_id="D1",
            trigger_reason="Test",
            timestamp=datetime.now(),
            monthly_spend_at_trigger=400.0,
            daily_spend_at_trigger=40.0,
        )

        success, message = cascade.execute_transition(transition)
        assert success is True


class TestRunwayDashboard:
    """Tests for RunwayDashboard."""

    def test_default_initialization(self):
        """Test default dashboard initialization."""
        dashboard = RunwayDashboard()

        assert dashboard.monthly_cap_usd == 500.0
        assert dashboard.daily_cap_usd == 50.0

    def test_update_spend(self):
        """Test spend updating."""
        dashboard = RunwayDashboard()

        dashboard.update_spend(
            monthly_spend=350.0,
            daily_spend=42.0,
        )

        gauge = dashboard.get_budget_gauge()
        assert gauge.monthly_spend == 350.0
        assert gauge.daily_spend == 42.0

    def test_get_budget_gauge(self):
        """Test budget gauge retrieval."""
        dashboard = RunwayDashboard()

        dashboard.update_spend(350.0, 35.0)

        gauge = dashboard.get_budget_gauge()

        assert gauge.get_monthly_pct() == 70.0
        assert gauge.get_daily_pct() == 70.0
        assert gauge.get_color_zone(70.0) == "yellow"
        assert gauge.get_color_zone(80.0) == "orange"
        assert gauge.get_color_zone(96.0) == "red"

    def test_get_runway_counter(self):
        """Test runway counter retrieval."""
        dashboard = RunwayDashboard()

        dashboard.update_spend(300.0, 30.0)

        runway = dashboard.get_runway_counter()

        assert runway.days_remaining > 0
        assert runway.burn_rate_7d > 0

    def test_add_alert(self):
        """Test alert adding."""
        dashboard = RunwayDashboard()

        dashboard.add_alert("warning", "Test alert")

        alerts = dashboard.get_alert_feed()
        assert len(alerts) > 0
        assert alerts[-1]["message"] == "Test alert"

    def test_trip_kill_switch(self):
        """Test kill-switch tripping."""
        dashboard = RunwayDashboard()

        # Initially active
        assert dashboard._kill_switches["KS-DAILY"]["is_active"] is True

        # Trip the switch
        dashboard.trip_kill_switch("KS-DAILY")

        assert dashboard._kill_switches["KS-DAILY"]["is_active"] is False

    def test_get_dashboard_summary(self):
        """Test dashboard summary retrieval."""
        dashboard = RunwayDashboard()

        dashboard.update_spend(350.0, 42.0)

        summary = dashboard.get_dashboard_summary()

        assert "budget" in summary
        assert "runway" in summary
        assert "tier" in summary
