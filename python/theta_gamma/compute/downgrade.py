"""
Auto-Downgrade Rules — Automated tier transitions based on budget pressure.

This module implements the auto-downgrade cascade that reduces training
costs when budget pressure approaches cap limits.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from theta_gamma.compute.tiers import TrainingTier, TierManager


class TransitionDirection(str, Enum):
    """Direction of tier transition."""

    DOWNGRADE = "downgrade"
    UPGRADE = "upgrade"


@dataclass
class TierTransition:
    """
    A tier transition event.

    Attributes:
        direction: Transition direction
        from_tier: Source tier
        to_tier: Target tier
        rule_id: Rule that triggered the transition
        trigger_reason: Reason for the transition
        timestamp: Transition timestamp
        monthly_spend_at_trigger: Monthly spend at trigger
        daily_spend_at_trigger: Daily spend at trigger
        checkpoint_id: Checkpoint saved before transition
        rollback_guard_active: Whether rollback guard is active
    """

    direction: TransitionDirection
    from_tier: TrainingTier
    to_tier: TrainingTier
    rule_id: str
    trigger_reason: str
    timestamp: datetime
    monthly_spend_at_trigger: float
    daily_spend_at_trigger: float
    checkpoint_id: str = ""
    rollback_guard_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "direction": self.direction.value,
            "from_tier": self.from_tier.value,
            "to_tier": self.to_tier.value,
            "rule_id": self.rule_id,
            "trigger_reason": self.trigger_reason,
            "timestamp": self.timestamp.isoformat(),
            "monthly_spend_at_trigger": self.monthly_spend_at_trigger,
            "daily_spend_at_trigger": self.daily_spend_at_trigger,
            "checkpoint_id": self.checkpoint_id,
            "rollback_guard_active": self.rollback_guard_active,
        }


@dataclass
class DowngradeRule:
    """
    A downgrade rule definition.

    Attributes:
        rule_id: Rule identifier (D1, D2, D3, D4)
        name: Human-readable name
        from_tier: Source tier
        to_tier: Target tier
        triggers: List of trigger conditions
        execution_steps: Steps to execute during downgrade
        rollback_guard: Condition to trigger rollback
        autonomy_tier: Autonomy tier for execution
    """

    rule_id: str
    name: str
    from_tier: TrainingTier
    to_tier: TrainingTier
    triggers: list[Callable[[dict[str, Any]], bool]]
    execution_steps: list[str]
    rollback_guard: Callable[[dict[str, Any]], bool]
    autonomy_tier: str = "T1"

    def check_triggers(self, context: dict[str, Any]) -> tuple[bool, str]:
        """
        Check if any trigger conditions are met.

        Args:
            context: Context dictionary with spend, cost-per-point, etc.

        Returns:
            Tuple of (is_triggered, trigger_reason)
        """
        for trigger in self.triggers:
            if trigger(context):
                return (True, self._get_trigger_description(context))
        return (False, "")

    def _get_trigger_description(self, context: dict[str, Any]) -> str:
        """Get human-readable trigger description."""
        parts = []
        if "monthly_spend" in context and context["monthly_spend"] is not None:
            parts.append(f"monthly spend at {context['monthly_spend']:.0%}")
        if "daily_spend" in context and context["daily_spend"] is not None:
            parts.append(f"daily spend at ${context['daily_spend']:.2f}")
        if "cost_per_point" in context and context["cost_per_point"] is not None:
            parts.append(f"cost-per-point ${context['cost_per_point']:.2f}/pp")
        return ", ".join(parts) if parts else "Unknown trigger"

    def check_rollback_guard(self, context: dict[str, Any]) -> bool:
        """
        Check if rollback guard should trigger.

        Args:
            context: Context dictionary

        Returns:
            True if rollback should be triggered
        """
        return self.rollback_guard(context)


@dataclass
class UpgradeRule:
    """
    An upgrade rule definition.

    Attributes:
        rule_id: Rule identifier (U1, U2, U3)
        name: Human-readable name
        from_tier: Source tier
        to_tier: Target tier
        conditions: List of conditions that must all be met
        execution_steps: Steps to execute during upgrade
    """

    rule_id: str
    name: str
    from_tier: TrainingTier
    to_tier: TrainingTier
    conditions: list[Callable[[dict[str, Any]], bool]]
    execution_steps: list[str]

    def check_conditions(self, context: dict[str, Any]) -> tuple[bool, str]:
        """
        Check if all upgrade conditions are met.

        Args:
            context: Context dictionary

        Returns:
            Tuple of (all_met, message)
        """
        for condition in self.conditions:
            if not condition(context):
                return (False, "Condition not met")
        return (True, "All conditions met")


class DowngradeCascade:
    """
    Manages the auto-downgrade cascade.

    Monitors budget pressure and triggers tier downgrades according
    to defined rules.

    Example:
        >>> cascade = DowngradeCascade()
        >>> transition = cascade.evaluate_downgrade(
        ...     monthly_spend_pct=0.85,
        ...     daily_spend=45.0,
        ... )
        >>> if transition:
        ...     execute_downgrade(transition)
    """

    def __init__(self, tier_manager: TierManager | None = None) -> None:
        """
        Initialize the downgrade cascade.

        Args:
            tier_manager: Tier manager instance
        """
        self._tier_manager = tier_manager or TierManager()
        self._transitions: list[TierTransition] = []
        self._rules: dict[str, DowngradeRule] = {}
        self._upgrade_rules: dict[str, UpgradeRule] = {}

        self._initialize_rules()

    def _initialize_rules(self) -> None:
        """Initialize default downgrade and upgrade rules."""
        # Downgrade Rules
        self._rules = {
            "D1": DowngradeRule(
                rule_id="D1",
                name="T1 -> T2 (Full -> Efficient)",
                from_tier=TrainingTier.T1_FULL_FSDP,
                to_tier=TrainingTier.T2_EFFICIENT,
                triggers=[
                    lambda ctx: (ctx.get("monthly_spend_pct") or 0) >= 0.80,
                    lambda ctx: (ctx.get("daily_spend") or 0) >= 40.0,
                    lambda ctx: (ctx.get("cost_per_point") or 0) > 15.0,
                    lambda ctx: (ctx.get("gpu_utilization") or 1.0) < 0.40,
                ],
                execution_steps=[
                    "Complete current training step",
                    "Save checkpoint with full optimizer state",
                    "Log downgrade event",
                    "Reconfigure: 4 -> 2 GPUs",
                    "Switch to DeepSpeed ZeRO-2",
                    "Reduce batch size to 75%",
                    "Adjust learning rate",
                    "Resume from checkpoint",
                    "Run quick eval after 100 steps",
                ],
                rollback_guard=lambda ctx: (ctx.get("accuracy_drop_pp") or 0) > 5.0,
                autonomy_tier="T1",
            ),
            "D2": DowngradeRule(
                rule_id="D2",
                name="T2 -> T3 (Efficient -> Compressed)",
                from_tier=TrainingTier.T2_EFFICIENT,
                to_tier=TrainingTier.T3_COMPRESSED,
                triggers=[
                    lambda ctx: (ctx.get("monthly_spend_pct") or 0) >= 0.90,
                    lambda ctx: (ctx.get("daily_spend") or 0) >= 45.0,
                    lambda ctx: (ctx.get("cost_per_point") or 0) > 25.0,
                ],
                execution_steps=[
                    "Complete current training step",
                    "Save checkpoint with full optimizer state",
                    "Log downgrade event",
                    "Apply QLoRA quantization (4-bit NF4)",
                    "Add LoRA adapters (rank 64, alpha 128)",
                    "Reconfigure: 2 -> 1 GPUs",
                    "Reduce batch size to 50%",
                    "Reduce learning rate by 50%",
                    "Resume from checkpoint",
                    "Run quick eval after 200 steps",
                ],
                rollback_guard=lambda ctx: (ctx.get("accuracy_drop_pp") or 0) > 10.0,
                autonomy_tier="T2",
            ),
            "D3": DowngradeRule(
                rule_id="D3",
                name="T3 -> T4 (Compressed -> Eval-Only)",
                from_tier=TrainingTier.T3_COMPRESSED,
                to_tier=TrainingTier.T4_EVAL_ONLY,
                triggers=[
                    lambda ctx: (ctx.get("monthly_spend_pct") or 0) >= 0.95,
                    lambda ctx: ctx.get("training_budget_exhausted", False),
                    lambda ctx: (ctx.get("consecutive_no_progress") or 0) >= 3,
                ],
                execution_steps=[
                    "Save final checkpoint",
                    "Terminate all training jobs",
                    "Log downgrade event",
                    "Switch to eval-only mode",
                    "Run eval harness on existing checkpoints",
                    "Identify best checkpoint per gate",
                    "Generate cost-efficiency report",
                ],
                rollback_guard=lambda ctx: False,  # No rollback from T4
                autonomy_tier="T2",
            ),
            "D4": DowngradeRule(
                rule_id="D4",
                name="T4 -> T5 (Eval-Only -> Full Stop)",
                from_tier=TrainingTier.T4_EVAL_ONLY,
                to_tier=TrainingTier.T5_FULL_STOP,
                triggers=[
                    lambda ctx: (ctx.get("monthly_spend_pct") or 0) >= 1.0,
                ],
                execution_steps=[
                    "Terminate ALL running jobs immediately",
                    "Save any in-progress eval results",
                    "Log downgrade event",
                    "Block all new compute launches",
                ],
                rollback_guard=lambda ctx: False,  # No rollback from T5
                autonomy_tier="Automatic",
            ),
        }

        # Upgrade Rules
        self._upgrade_rules = {
            "U1": UpgradeRule(
                rule_id="U1",
                name="T2 -> T1 (Efficient -> Full)",
                from_tier=TrainingTier.T2_EFFICIENT,
                to_tier=TrainingTier.T1_FULL_FSDP,
                conditions=[
                    lambda ctx: (ctx.get("monthly_spend_pct") or 1.0) < 0.50,
                    lambda ctx: (ctx.get("days_remaining") or 0) >= 10,
                    lambda ctx: not ctx.get("active_budget_alerts", False),
                    lambda ctx: not ctx.get("gate_passed", False),
                ],
                execution_steps=[
                    "Save checkpoint",
                    "Log upgrade event",
                    "Reconfigure to T1 settings (4 GPU, full batch)",
                    "Resume from checkpoint",
                    "Monitor spend rate for 24h",
                ],
            ),
            "U2": UpgradeRule(
                rule_id="U2",
                name="T3 -> T2 (Compressed -> Efficient)",
                from_tier=TrainingTier.T3_COMPRESSED,
                to_tier=TrainingTier.T2_EFFICIENT,
                conditions=[
                    lambda ctx: (ctx.get("monthly_spend_pct") or 1.0) < 0.60,
                    lambda ctx: (ctx.get("days_remaining") or 0) >= 10,
                    lambda ctx: not ctx.get("active_budget_alerts", False),
                    lambda ctx: (ctx.get("cost_per_point_t3") or 0) > 20.0,
                ],
                execution_steps=[
                    "Merge LoRA adapters",
                    "Save merged checkpoint",
                    "Log upgrade event",
                    "Reconfigure to T2 settings",
                    "Resume from merged checkpoint",
                ],
            ),
            "U3": UpgradeRule(
                rule_id="U3",
                name="T4/T5 -> Training Tier",
                from_tier=TrainingTier.T4_EVAL_ONLY,
                to_tier=TrainingTier.T1_FULL_FSDP,
                conditions=[
                    lambda ctx: ctx.get("new_budget_month", False),
                ],
                execution_steps=[
                    "Evaluate remaining monthly budget",
                    "Select highest affordable tier",
                    "Resume from best known checkpoint",
                    "Log upgrade event",
                ],
            ),
        }

    def evaluate_downgrade(
        self,
        monthly_spend_pct: float,
        daily_spend: float,
        cost_per_point: float | None = None,
        gpu_utilization: float | None = None,
        checkpoint_id: str = "",
    ) -> TierTransition | None:
        """
        Evaluate if a downgrade should be triggered.

        Args:
            monthly_spend_pct: Monthly spend as percentage of cap
            daily_spend: Current daily spend in USD
            cost_per_point: Cost per accuracy point (optional)
            gpu_utilization: GPU utilization (optional)
            checkpoint_id: Current checkpoint ID

        Returns:
            TierTransition if downgrade triggered, None otherwise
        """
        current_tier = self._tier_manager.get_current_tier()

        context = {
            "monthly_spend_pct": monthly_spend_pct,
            "daily_spend": daily_spend,
            "cost_per_point": cost_per_point,
            "gpu_utilization": gpu_utilization,
        }

        # Find applicable rule
        for rule in self._rules.values():
            if rule.from_tier != current_tier:
                continue

            is_triggered, trigger_reason = rule.check_triggers(context)
            if is_triggered:
                transition = TierTransition(
                    direction=TransitionDirection.DOWNGRADE,
                    from_tier=current_tier,
                    to_tier=rule.to_tier,
                    rule_id=rule.rule_id,
                    trigger_reason=trigger_reason,
                    timestamp=datetime.now(),
                    monthly_spend_at_trigger=monthly_spend_pct * 500,  # Assuming $500 cap
                    daily_spend_at_trigger=daily_spend,
                    checkpoint_id=checkpoint_id,
                    rollback_guard_active=True,
                )
                self._transitions.append(transition)
                return transition

        return None

    def evaluate_upgrade(
        self,
        monthly_spend_pct: float,
        days_remaining: int,
        active_alerts: bool = False,
        gate_passed: bool = False,
    ) -> TierTransition | None:
        """
        Evaluate if an upgrade should be triggered.

        Args:
            monthly_spend_pct: Monthly spend as percentage of cap
            days_remaining: Days remaining in budget month
            active_alerts: Whether there are active budget alerts
            gate_passed: Whether current gate has passed

        Returns:
            TierTransition if upgrade triggered, None otherwise
        """
        current_tier = self._tier_manager.get_current_tier()

        context = {
            "monthly_spend_pct": monthly_spend_pct,
            "days_remaining": days_remaining,
            "active_budget_alerts": active_alerts,
            "gate_passed": gate_passed,
            "new_budget_month": days_remaining >= 28,
        }

        # Find applicable rule
        for rule in self._upgrade_rules.values():
            if rule.from_tier != current_tier:
                continue

            all_met, _ = rule.check_conditions(context)
            if all_met:
                transition = TierTransition(
                    direction=TransitionDirection.UPGRADE,
                    from_tier=current_tier,
                    to_tier=rule.to_tier,
                    rule_id=rule.rule_id,
                    trigger_reason="Budget pressure subsided",
                    timestamp=datetime.now(),
                    monthly_spend_at_trigger=monthly_spend_pct * 500,
                    daily_spend_at_trigger=0.0,
                    rollback_guard_active=False,
                )
                self._transitions.append(transition)
                return transition

        return None

    def execute_transition(self, transition: TierTransition) -> tuple[bool, str]:
        """
        Execute a tier transition.

        Args:
            transition: Transition to execute

        Returns:
            Tuple of (success, message)
        """
        success, message = self._tier_manager.transition_to(transition.to_tier)
        if success:
            # Update transition record
            transition.checkpoint_id = f"ckpt-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        return (success, message)

    def check_rollback_guard(self, transition: TierTransition, accuracy_drop_pp: float) -> bool:
        """
        Check if rollback guard should trigger after a downgrade.

        Args:
            transition: The downgrade transition
            accuracy_drop_pp: Accuracy drop in percentage points

        Returns:
            True if rollback should be triggered
        """
        if transition.direction != TransitionDirection.DOWNGRADE:
            return False

        rule = self._rules.get(transition.rule_id)
        if not rule:
            return False

        context = {"accuracy_drop_pp": accuracy_drop_pp}
        return rule.check_rollback_guard(context)

    def get_transitions(self) -> list[TierTransition]:
        """Get all transitions."""
        return self._transitions.copy()

    def get_transition_history(self) -> list[dict[str, Any]]:
        """Get transition history."""
        return [t.to_dict() for t in self._transitions]

    def get_current_tier(self) -> TrainingTier:
        """Get current tier."""
        return self._tier_manager.get_current_tier()

    def get_downgrade_path(self) -> list[TrainingTier]:
        """Get downgrade path from current tier."""
        return self._tier_manager.get_downgrade_path()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "current_tier": self._tier_manager.get_current_tier().value,
            "rules": {k: v.rule_id for k, v in self._rules.items()},
            "upgrade_rules": {k: v.rule_id for k, v in self._upgrade_rules.items()},
            "transitions": [t.to_dict() for t in self._transitions],
        }
