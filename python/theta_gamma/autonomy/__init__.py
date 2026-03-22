"""
Autonomy module — Decision authority, risk profiles, and failure modes.

This module implements the autonomy contract that governs all autonomous
decisions made during execution of the Theta-Gamma pipeline. It defines
decision authority tiers, risk appetite profiles, and failure mode handling.

Core Classes:
    - DecisionTier: Authority levels (T0-T4) for autonomous decisions
    - DecisionClass: Categorization of decisions with tier assignments
    - AutonomyContract: Main contract governing autonomous execution
    - RiskAppetiteProfile: Risk tolerance across multiple dimensions
    - FailureMode: Defined failure modes with detection and mitigation
"""

from theta_gamma.autonomy.contract import (
    AutonomyContract,
    DecisionTier,
    DecisionClass,
    DecisionLogEntry,
    ReversibilityClassification,
)
from theta_gamma.autonomy.risk_profile import (
    RiskAppetiteProfile,
    RiskDimension,
    RiskAppetiteLevel,
    FinancialRiskConfig,
    DataIntegrityRiskConfig,
    SecurityRiskConfig,
)
from theta_gamma.autonomy.failure_modes import (
    FailureMode,
    FailureModeRegistry,
    FailureModeSeverity,
    FailureModeLikelihood,
    FailureModeImpact,
)
from theta_gamma.autonomy.limits import (
    OperatingLimits,
    CostAlertThreshold,
    KillSwitchType,
    KillSwitch,
)

__all__ = [
    # Contract
    "AutonomyContract",
    "DecisionTier",
    "DecisionClass",
    "DecisionLogEntry",
    "ReversibilityClassification",
    # Risk Profile
    "RiskAppetiteProfile",
    "RiskDimension",
    "RiskAppetiteLevel",
    "FinancialRiskConfig",
    "DataIntegrityRiskConfig",
    "SecurityRiskConfig",
    # Failure Modes
    "FailureMode",
    "FailureModeRegistry",
    "FailureModeSeverity",
    "FailureModeLikelihood",
    "FailureModeImpact",
    # Limits
    "OperatingLimits",
    "CostAlertThreshold",
    "KillSwitchType",
    "KillSwitch",
]
