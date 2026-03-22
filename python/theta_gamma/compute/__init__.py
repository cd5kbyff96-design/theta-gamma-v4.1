"""
Compute module — Budget tracking, training tiers, and auto-downgrade rules.

This module implements compute budget management, training tier definitions,
auto-downgrade rules, and the runway/burn dashboard for the Theta-Gamma pipeline.
"""

from theta_gamma.compute.budget import (
    ComputeBudget,
    BudgetPolicy,
    BudgetCategory,
    CostEvent,
    BudgetAlert,
)
from theta_gamma.compute.tiers import (
    TrainingTier,
    TierManager,
    TierConfig,
    GPUConfig,
)
from theta_gamma.compute.downgrade import (
    DowngradeRule,
    DowngradeCascade,
    UpgradeRule,
    TierTransition,
)
from theta_gamma.compute.dashboard import (
    RunwayDashboard,
    DashboardPanel,
    BudgetGauge,
    BurnRateChart,
)

__all__ = [
    # Budget
    "ComputeBudget",
    "BudgetPolicy",
    "BudgetCategory",
    "CostEvent",
    "BudgetAlert",
    # Tiers
    "TrainingTier",
    "TierManager",
    "TierConfig",
    "GPUConfig",
    # Downgrade
    "DowngradeRule",
    "DowngradeCascade",
    "UpgradeRule",
    "TierTransition",
    # Dashboard
    "RunwayDashboard",
    "DashboardPanel",
    "BudgetGauge",
    "BurnRateChart",
]
