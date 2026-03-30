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
    DecisionClass,
    DecisionLogEntry,
    DecisionTier,
    ReversibilityClassification,
)
from theta_gamma.autonomy.failure_modes import (
    FailureMode,
    FailureModeImpact,
    FailureModeLikelihood,
    FailureModeRegistry,
    FailureModeSeverity,
)
from theta_gamma.autonomy.limits import (
    CostAlertThreshold,
    KillSwitch,
    KillSwitchType,
    OperatingLimits,
)
from theta_gamma.autonomy.risk_profile import (
    DataIntegrityRiskConfig,
    FinancialRiskConfig,
    RiskAppetiteLevel,
    RiskAppetiteProfile,
    RiskDimension,
    SecurityRiskConfig,
)

__all__ = [
    # Contract
    "AutonomyContract",
    "DecisionClass",
    "DecisionLogEntry",
    "DecisionTier",
    "ReversibilityClassification",
    # Failure Modes
    "FailureMode",
    "FailureModeImpact",
    "FailureModeLikelihood",
    "FailureModeRegistry",
    "FailureModeSeverity",
    # Limits
    "CostAlertThreshold",
    "KillSwitch",
    "KillSwitchType",
    "OperatingLimits",
    # Risk Profile
    "DataIntegrityRiskConfig",
    "FinancialRiskConfig",
    "RiskAppetiteLevel",
    "RiskAppetiteProfile",
    "RiskDimension",
    "SecurityRiskConfig",
]
