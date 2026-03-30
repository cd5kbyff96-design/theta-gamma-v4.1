"""
Training Tiers — Training tier definitions and management.

This module implements training tier configurations that define
GPU allocations, batch sizes, and strategies for different budget levels.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TierStrategy(str, Enum):
    """Training strategy types."""

    FSDP = "fsdp"
    DEEPSPEED_ZERO2 = "deepspeed_zero2"
    DEEPSPEED_ZERO3 = "deepspeed_zero3"
    Q_LORA = "qlora"
    PRUNED = "pruned"


@dataclass
class GPUConfig:
    """
    GPU configuration for a training tier.

    Attributes:
        gpu_type: GPU type (e.g., "A100-80GB")
        count: Number of GPUs
        memory_gb: Memory per GPU in GB
    """

    gpu_type: str
    count: int
    memory_gb: int

    @property
    def total_memory_gb(self) -> int:
        """Total GPU memory in GB."""
        return self.count * self.memory_gb

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "gpu_type": self.gpu_type,
            "count": self.count,
            "memory_gb": self.memory_gb,
            "total_memory_gb": self.total_memory_gb,
        }


@dataclass
class TierConfig:
    """
    Configuration for a training tier.

    Attributes:
        tier_id: Tier identifier (T1, T2, T3, T4, T5)
        name: Human-readable name
        description: Tier description
        gpu_config: GPU configuration
        strategy: Training strategy
        batch_size_pct: Batch size as percentage of T1
        learning_rate_scale: Learning rate scaling factor
        estimated_daily_cost_usd: Estimated daily cost range
        is_training_enabled: Whether training is enabled
    """

    tier_id: str
    name: str
    description: str
    gpu_config: GPUConfig
    strategy: TierStrategy
    batch_size_pct: float = 100.0
    learning_rate_scale: float = 1.0
    estimated_daily_cost_usd: tuple[float, float] = (0.0, 0.0)
    is_training_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "tier_id": self.tier_id,
            "name": self.name,
            "description": self.description,
            "gpu_config": self.gpu_config.to_dict(),
            "strategy": self.strategy.value,
            "batch_size_pct": self.batch_size_pct,
            "learning_rate_scale": self.learning_rate_scale,
            "estimated_daily_cost_usd": self.estimated_daily_cost_usd,
            "is_training_enabled": self.is_training_enabled,
        }


class TrainingTier(str, Enum):
    """
    Training tier identifiers.

    Tiers range from T1 (full performance) to T5 (full stop).
    """

    T1_FULL_FSDP = "T1-Full-FSDP"
    T1_FULL_DEEPSPEED = "T1-Full-DeepSpeed"
    T2_EFFICIENT = "T2-Efficient-ZeRO2"
    T3_COMPRESSED = "T3-Compressed"
    T4_EVAL_ONLY = "T4-Eval-Only"
    T5_FULL_STOP = "T5-Full-Stop"


class TierManager:
    """
    Manager for training tiers.

    Provides tier lookup, transition validation, and configuration management.

    Example:
        >>> manager = TierManager()
        >>> config = manager.get_tier_config(TrainingTier.T2_EFFICIENT)
        >>> print(f"GPU count: {config.gpu_config.count}")
    """

    def __init__(self) -> None:
        """Initialize the tier manager."""
        self._tiers: dict[TrainingTier, TierConfig] = {}
        self._current_tier: TrainingTier = TrainingTier.T1_FULL_FSDP
        self._tier_history: list[tuple[TrainingTier, TrainingTier]] = []

        self._initialize_default_tiers()

    def _initialize_default_tiers(self) -> None:
        """Initialize default training tiers from the specification."""
        tiers = [
            # T1 - Full Performance (Default)
            TierConfig(
                tier_id="T1-Full-FSDP",
                name="Full FSDP",
                description="4xA100-80GB with FSDP full sharding",
                gpu_config=GPUConfig(gpu_type="A100-80GB", count=4, memory_gb=80),
                strategy=TierStrategy.FSDP,
                batch_size_pct=100.0,
                learning_rate_scale=1.0,
                estimated_daily_cost_usd=(35.0, 50.0),
                is_training_enabled=True,
            ),
            TierConfig(
                tier_id="T1-Full-DeepSpeed",
                name="Full DeepSpeed",
                description="4xA100-80GB with DeepSpeed ZeRO-3",
                gpu_config=GPUConfig(gpu_type="A100-80GB", count=4, memory_gb=80),
                strategy=TierStrategy.DEEPSPEED_ZERO3,
                batch_size_pct=100.0,
                learning_rate_scale=1.0,
                estimated_daily_cost_usd=(35.0, 50.0),
                is_training_enabled=True,
            ),
            # T2 - Efficient
            TierConfig(
                tier_id="T2-Efficient-ZeRO2",
                name="Efficient ZeRO-2",
                description="2xA100-80GB with DeepSpeed ZeRO-2",
                gpu_config=GPUConfig(gpu_type="A100-80GB", count=2, memory_gb=80),
                strategy=TierStrategy.DEEPSPEED_ZERO2,
                batch_size_pct=75.0,
                learning_rate_scale=0.75,
                estimated_daily_cost_usd=(20.0, 35.0),
                is_training_enabled=True,
            ),
            # T3 - Compressed
            TierConfig(
                tier_id="T3-Compressed",
                name="Compressed (QLoRA)",
                description="1xA100-80GB with QLoRA or pruning",
                gpu_config=GPUConfig(gpu_type="A100-80GB", count=1, memory_gb=80),
                strategy=TierStrategy.Q_LORA,
                batch_size_pct=50.0,
                learning_rate_scale=0.5,
                estimated_daily_cost_usd=(8.0, 20.0),
                is_training_enabled=True,
            ),
            # T4 - Eval Only
            TierConfig(
                tier_id="T4-Eval-Only",
                name="Eval Only",
                description="1xA100-40GB/A10 for evaluation only",
                gpu_config=GPUConfig(gpu_type="A100-40GB", count=1, memory_gb=40),
                strategy=TierStrategy.FSDP,
                batch_size_pct=0.0,
                learning_rate_scale=0.0,
                estimated_daily_cost_usd=(2.0, 8.0),
                is_training_enabled=False,
            ),
            # T5 - Full Stop
            TierConfig(
                tier_id="T5-Full-Stop",
                name="Full Stop",
                description="All compute halted",
                gpu_config=GPUConfig(gpu_type="none", count=0, memory_gb=0),
                strategy=TierStrategy.FSDP,
                batch_size_pct=0.0,
                learning_rate_scale=0.0,
                estimated_daily_cost_usd=(0.0, 0.0),
                is_training_enabled=False,
            ),
        ]

        for tier_config in tiers:
            tier_enum = self._tier_id_to_enum(tier_config.tier_id)
            if tier_enum:
                self._tiers[tier_enum] = tier_config

    def _tier_id_to_enum(self, tier_id: str) -> TrainingTier | None:
        """Convert tier ID string to TrainingTier enum."""
        mapping = {
            "T1-Full-FSDP": TrainingTier.T1_FULL_FSDP,
            "T1-Full-DeepSpeed": TrainingTier.T1_FULL_DEEPSPEED,
            "T2-Efficient-ZeRO2": TrainingTier.T2_EFFICIENT,
            "T3-Compressed": TrainingTier.T3_COMPRESSED,
            "T4-Eval-Only": TrainingTier.T4_EVAL_ONLY,
            "T5-Full-Stop": TrainingTier.T5_FULL_STOP,
        }
        return mapping.get(tier_id)

    def get_tier_config(self, tier: TrainingTier) -> TierConfig | None:
        """Get configuration for a tier."""
        return self._tiers.get(tier)

    def get_current_tier(self) -> TrainingTier:
        """Get current training tier."""
        return self._current_tier

    def get_current_config(self) -> TierConfig:
        """Get configuration for current tier."""
        config = self._tiers.get(self._current_tier)
        if not config:
            raise ValueError(f"Unknown tier: {self._current_tier}")
        return config

    def can_transition(
        self, from_tier: TrainingTier, to_tier: TrainingTier
    ) -> tuple[bool, str]:
        """
        Check if a tier transition is valid.

        Args:
            from_tier: Current tier
            to_tier: Target tier

        Returns:
            Tuple of (is_valid, message)
        """
        # T5 (Full Stop) requires human approval to exit
        if from_tier == TrainingTier.T5_FULL_STOP:
            return (
                False,
                "T5-Full-Stop requires human approval to exit",
            )

        # T4 (Eval Only) can only transition to T1-T3 with approval
        if from_tier == TrainingTier.T4_EVAL_ONLY and to_tier not in (
            TrainingTier.T4_EVAL_ONLY,
            TrainingTier.T5_FULL_STOP,
        ):
            return (
                True,
                "Transition from T4 requires human approval",
            )

        # All other transitions are allowed
        return (True, "Transition allowed")

    def transition_to(self, tier: TrainingTier) -> tuple[bool, str]:
        """
        Transition to a new tier.

        Args:
            tier: Target tier

        Returns:
            Tuple of (success, message)
        """
        can_transition, message = self.can_transition(self._current_tier, tier)
        if not can_transition:
            return (False, message)

        self._tier_history.append((self._current_tier, tier))
        self._current_tier = tier
        return (True, f"Transitioned to {tier.value}")

    def get_downgrade_path(self) -> list[TrainingTier]:
        """
        Get the downgrade path from current tier.

        Returns:
            List of tiers in downgrade order
        """
        all_tiers = [
            TrainingTier.T1_FULL_FSDP,
            TrainingTier.T2_EFFICIENT,
            TrainingTier.T3_COMPRESSED,
            TrainingTier.T4_EVAL_ONLY,
            TrainingTier.T5_FULL_STOP,
        ]

        try:
            current_idx = all_tiers.index(self._current_tier)
        except ValueError:
            current_idx = 0

        return all_tiers[current_idx:]

    def get_upgrade_path(self) -> list[TrainingTier]:
        """
        Get the upgrade path from current tier.

        Returns:
            List of tiers in upgrade order
        """
        all_tiers = [
            TrainingTier.T5_FULL_STOP,
            TrainingTier.T4_EVAL_ONLY,
            TrainingTier.T3_COMPRESSED,
            TrainingTier.T2_EFFICIENT,
            TrainingTier.T1_FULL_FSDP,
        ]

        try:
            current_idx = all_tiers.index(self._current_tier)
        except ValueError:
            current_idx = 0

        return all_tiers[current_idx:]

    def get_tier_by_name(self, name: str) -> TrainingTier | None:
        """Get tier by name string."""
        for tier, config in self._tiers.items():
            if config.tier_id == name or config.name == name:
                return tier
        return None

    def get_training_enabled_tiers(self) -> list[TrainingTier]:
        """Get all tiers with training enabled."""
        return [
            tier
            for tier, config in self._tiers.items()
            if config.is_training_enabled
        ]

    def get_tier_history(self) -> list[tuple[TrainingTier, TrainingTier]]:
        """Get tier transition history."""
        return self._tier_history.copy()

    def get_estimated_daily_cost(self) -> tuple[float, float]:
        """Get estimated daily cost for current tier."""
        config = self.get_current_config()
        return config.estimated_daily_cost_usd

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "current_tier": self._current_tier.value,
            "tiers": {t.value: c.to_dict() for t, c in self._tiers.items()},
            "history": [
                {"from": f.value, "to": t.value} for f, t in self._tier_history
            ],
        }
