"""Tests for the autonomy module."""

import pytest
from datetime import datetime

from theta_gamma.autonomy.contract import (
    AutonomyContract,
    DecisionTier,
    DecisionClass,
    ReversibilityClassification,
    DecisionLogEntry,
)
from theta_gamma.autonomy.risk_profile import (
    RiskAppetiteProfile,
    RiskAppetiteLevel,
    FinancialRiskConfig,
    DataEnvironment,
)
from theta_gamma.autonomy.failure_modes import (
    FailureMode,
    FailureModeRegistry,
    FailureModeLikelihood,
    FailureModeImpact,
)
from theta_gamma.autonomy.limits import (
    OperatingLimits,
    KillSwitchType,
)


class TestDecisionTier:
    """Tests for DecisionTier enum."""

    def test_tier_requires_approval(self):
        """Test tier approval requirements."""
        assert DecisionTier.T3.requires_approval is True
        assert DecisionTier.T4.requires_approval is True
        assert DecisionTier.T0.requires_approval is False
        assert DecisionTier.T1.requires_approval is False
        assert DecisionTier.T2.requires_approval is False

    def test_tier_is_prohibited(self):
        """Test tier prohibition."""
        assert DecisionTier.T4.is_prohibited is True
        assert DecisionTier.T3.is_prohibited is False


class TestAutonomyContract:
    """Tests for AutonomyContract."""

    def test_default_initialization(self):
        """Test default contract initialization."""
        contract = AutonomyContract()
        assert contract.version == "1.0.0"
        assert len(contract.get_all_decision_classes()) > 0

    def test_get_tier_for_action(self):
        """Test getting tier for action types."""
        contract = AutonomyContract()

        # File creation should be T0
        tier = contract.get_tier_for_action("file_creation")
        assert tier in (DecisionTier.T0, DecisionTier.T1)

    def test_classify_action(self):
        """Test action classification."""
        contract = AutonomyContract()

        tier, reversibility = contract.classify_action("file_creation", cost_usd=10.0)
        assert tier in (DecisionTier.T0, DecisionTier.T1)

        # High cost should escalate to T3
        tier, _ = contract.classify_action("file_creation", cost_usd=250.0)
        assert tier == DecisionTier.T3

    def test_log_decision(self, tmp_path):
        """Test decision logging."""
        log_path = tmp_path / "decision_log.md"
        contract = AutonomyContract(log_path=log_path)

        entry = DecisionLogEntry(
            timestamp=datetime.now(),
            decision_class="DC-001",
            tier=DecisionTier.T0,
            choice_made="default",
            rationale="Test decision",
            reversible=True,
            artifacts_affected=["test.txt"],
        )

        contract.log_decision(entry)

        content = log_path.read_text()
        assert "DC-001" in content
        assert "Test decision" in content


class TestRiskAppetiteProfile:
    """Tests for RiskAppetiteProfile."""

    def test_default_initialization(self):
        """Test default profile initialization."""
        profile = RiskAppetiteProfile()
        assert profile.version == "1.0.0"
        assert profile.financial.monthly_cap_usd == 500.0
        assert profile.financial.daily_cap_usd == 50.0

    def test_get_appetite_level(self):
        """Test getting appetite level for dimensions."""
        profile = RiskAppetiteProfile()

        assert profile.get_appetite_level("financial") in [
            RiskAppetiteLevel.LOW,
            RiskAppetiteLevel.MODERATE,
        ]
        assert profile.get_appetite_level("security") == RiskAppetiteLevel.ZERO
        assert profile.get_appetite_level("compliance") == RiskAppetiteLevel.ZERO

    def test_is_decision_irreversible(self):
        """Test irreversible decision detection."""
        profile = RiskAppetiteProfile()

        assert profile.is_decision_irreversible("Production deployment") is True
        assert profile.is_decision_irreversible("File creation") is False

    def test_get_data_policy(self):
        """Test data policy retrieval."""
        profile = RiskAppetiteProfile()

        assert profile.get_data_policy(DataEnvironment.DEV) == "freely_mutable"
        assert profile.get_data_policy(DataEnvironment.PRODUCTION) == "immutable_without_approval"

    def test_get_patching_sla(self):
        """Test patching SLA retrieval."""
        profile = RiskAppetiteProfile()

        assert profile.get_patching_sla("critical") == 24
        assert profile.get_patching_sla("high") == 168


class TestFailureMode:
    """Tests for FailureMode."""

    def test_failure_mode_creation(self):
        """Test failure mode creation."""
        fm = FailureMode(
            id="FM-TEST-01",
            name="Test Failure",
            description="Test failure mode",
            likelihood=FailureModeLikelihood.HIGH,
            impact=FailureModeImpact.HIGH,
            detection="Test detection",
            mitigation="Test mitigation",
            recovery="Test recovery",
            category="test",
        )

        assert fm.id == "FM-TEST-01"
        assert fm.risk_level == "High"

    def test_risk_level_calculation(self):
        """Test risk level calculation."""
        # High likelihood × Critical impact = Critical
        fm = FailureMode(
            id="FM-TEST-02",
            name="Critical Failure",
            description="Critical failure",
            likelihood=FailureModeLikelihood.HIGH,
            impact=FailureModeImpact.CRITICAL,
            detection="Test",
            mitigation="Test",
            recovery="Test",
        )
        assert fm.risk_level == "Critical"


class TestFailureModeRegistry:
    """Tests for FailureModeRegistry."""

    def test_default_failure_modes(self):
        """Test default failure modes are registered."""
        registry = FailureModeRegistry()
        modes = registry.get_all_modes()

        assert len(modes) > 0

        # Check specific modes exist
        fm_01 = registry.get_by_id("FM-01")
        assert fm_01 is not None
        assert "Runaway Compute" in fm_01.name

    def test_get_by_category(self):
        """Test getting modes by category."""
        registry = FailureModeRegistry()

        compute_modes = registry.get_by_category("compute")
        assert len(compute_modes) > 0

    def test_get_high_risk_modes(self):
        """Test getting high risk modes."""
        registry = FailureModeRegistry()

        high_risk = registry.get_high_risk_modes()
        assert isinstance(high_risk, list)
        # All returned modes should have High or Critical risk level
        for fm in high_risk:
            assert fm.risk_level in ("High", "Critical")


class TestOperatingLimits:
    """Tests for OperatingLimits."""

    def test_default_initialization(self):
        """Test default limits initialization."""
        limits = OperatingLimits()

        assert limits.monthly_compute_cap_usd == 500.0
        assert limits.daily_compute_cap_usd == 50.0
        assert limits.max_experiment_runtime_hours == 24.0

    def test_get_daily_alert_action(self):
        """Test daily alert action retrieval."""
        limits = OperatingLimits()

        # Low spend - no action
        action = limits.get_daily_alert_action(20.0)
        assert "No action" in action or "info" in action.lower()

        # High spend - kill action
        action = limits.get_daily_alert_action(50.0)
        assert "Hard-stop" in action or "kill" in action.lower()

    def test_kill_switch_operations(self):
        """Test kill-switch operations."""
        limits = OperatingLimits()

        # Initially not triggered
        assert limits.is_kill_switch_triggered(KillSwitchType.DAILY) is False

        # Trip the switch
        limits.trip_kill_switch(KillSwitchType.DAILY)
        assert limits.is_kill_switch_triggered(KillSwitchType.DAILY) is True

        # Reset the switch
        limits.reset_kill_switch(KillSwitchType.DAILY)
        assert limits.is_kill_switch_triggered(KillSwitchType.DAILY) is False

    def test_check_experiment_budget(self):
        """Test experiment budget checking."""
        limits = OperatingLimits()

        # Within budget
        is_valid, _ = limits.check_experiment_budget(25.0, 12.0)
        assert is_valid is True

        # Over single action cap
        is_valid, reason = limits.check_experiment_budget(60.0, 12.0)
        assert is_valid is False
        assert "exceeds single action cap" in reason

        # Over max runtime
        is_valid, reason = limits.check_experiment_budget(25.0, 30.0)
        assert is_valid is False
        assert "exceeds max" in reason
