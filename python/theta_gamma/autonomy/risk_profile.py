"""
Risk Appetite Profile — Defines risk tolerance across multiple dimensions.

This module implements the risk appetite profile that governs the
Theta-Gamma pipeline's tolerance for various types of risk including
financial, data integrity, security, availability, and compliance risks.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class RiskAppetiteLevel(str, Enum):
    """
    Risk appetite levels for each dimension.

    Levels range from zero tolerance to high appetite:
    - ZERO: Zero tolerance for risk
    - VERY_LOW: Minimal risk tolerance
    - LOW: Conservative risk approach
    - MODERATE: Balanced risk approach
    - MODERATE_CONSERVATIVE: Leans conservative
    - HIGH: High risk tolerance for velocity
    """

    ZERO = "zero"
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    MODERATE_CONSERVATIVE = "moderate_conservative"
    HIGH = "high"


class RiskDimension(str, Enum):
    """
    Risk dimensions tracked in the profile.

    Each dimension has its own appetite level and configuration.
    """

    FINANCIAL = "financial"
    DATA_INTEGRITY = "data_integrity"
    SECURITY = "security"
    AVAILABILITY = "availability"
    VELOCITY = "velocity"
    TECHNICAL_DEBT = "technical_debt"
    COMPLIANCE = "compliance"


class DataEnvironment(str, Enum):
    """Data environment classifications with increasing protection levels."""

    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class FinancialRiskConfig:
    """
    Configuration for financial risk tolerance.

    Attributes:
        monthly_cap_usd: Maximum monthly compute spend
        daily_cap_usd: Maximum daily compute spend
        single_action_cap_usd: Maximum cost for single autonomous action
        alert_threshold_pct: Percentage of cap that triggers alert
        tolerance_for_waste_pct: Acceptable waste percentage for experiments
    """

    monthly_cap_usd: float = 500.0
    daily_cap_usd: float = 50.0
    single_action_cap_usd: float = 50.0
    alert_threshold_pct: float = 80.0
    tolerance_for_waste_pct: float = 10.0

    @property
    def escalation_threshold_usd(self) -> float:
        """USD threshold for cost escalation."""
        return self.monthly_cap_usd * (self.alert_threshold_pct / 100)

    @property
    def hard_stop_usd(self) -> float:
        """Hard stop USD threshold (100% of cap)."""
        return self.monthly_cap_usd


@dataclass
class DataIntegrityRiskConfig:
    """
    Configuration for data integrity risk tolerance.

    Attributes:
        dev_policy: Policy for dev data (freely mutable, disposable)
        staging_policy: Policy for staging data (mutable with logging)
        production_policy: Policy for production data (immutable without approval)
        backup_retention_days: Days to retain backups
    """

    dev_policy: str = "freely_mutable"
    staging_policy: str = "mutable_with_logging"
    production_policy: str = "immutable_without_approval"
    backup_retention_days: int = 30

    def get_policy(self, env: DataEnvironment) -> str:
        """Get the data policy for an environment."""
        policies = {
            DataEnvironment.DEV: self.dev_policy,
            DataEnvironment.STAGING: self.staging_policy,
            DataEnvironment.PRODUCTION: self.production_policy,
        }
        return policies.get(env, self.production_policy)


@dataclass
class SecurityRiskConfig:
    """
    Configuration for security risk tolerance.

    Attributes:
        patching_sla_critical_hours: SLA for critical security patches
        patching_sla_high_hours: SLA for high severity patches
        secret_rotation_policy: Policy for secret rotation
        access_control_policy: Policy for access control changes
    """

    patching_sla_critical_hours: int = 24
    patching_sla_high_hours: int = 168  # 7 days
    secret_rotation_policy: str = "automated_dev_manual_prod"
    access_control_policy: str = "human_approval_required"


@dataclass
class AvailabilityRiskConfig:
    """
    Configuration for availability/operational risk tolerance.

    Attributes:
        dev_downtime_tolerance: Downtime tolerance for dev environments
        staging_downtime_tolerance_hours: Downtime tolerance for staging
        production_downtime_tolerance_minutes: Downtime tolerance for production
        rollback_required: Whether rollback is required for deployments
    """

    dev_downtime_tolerance: str = "unlimited"
    staging_downtime_tolerance_hours: float = 2.0
    production_downtime_tolerance_minutes: float = 5.0
    rollback_required: bool = True


@dataclass
class VelocityRiskConfig:
    """
    Configuration for velocity/delivery risk tolerance.

    Attributes:
        min_test_coverage_pct: Minimum test coverage for new code
        draft_pr_policy: Policy for draft PRs
        merge_policy: Policy for merging code
        feature_flag_required: Whether feature flags are required
    """

    min_test_coverage_pct: float = 80.0
    draft_pr_policy: str = "open_freely"
    merge_policy: str = "requires_ci_and_human_review"
    feature_flag_required: bool = True


@dataclass
class TechnicalDebtRiskConfig:
    """
    Configuration for technical debt risk tolerance.

    Attributes:
        auto_fix_policy: Policy for automated fixes
        refactoring_policy: Policy for refactoring
        dependency_update_policy: Policy for dependency updates
    """

    auto_fix_policy: str = "safe_linting_formatting"
    refactoring_policy: str = "when_touching_file"
    dependency_update_policy: str = "patch_minor_automated"


@dataclass
class ComplianceRiskConfig:
    """
    Configuration for compliance/legal risk tolerance.

    Attributes:
        license_auditing: Whether license auditing is automated
        copyleft_policy: Policy for copyleft dependencies
        data_handling_policy: Policy for data handling changes
        agreement_acceptance_policy: Policy for agreement acceptance
    """

    license_auditing: bool = True
    copyleft_policy: str = "escalate_immediately"
    data_handling_policy: str = "human_review_required"
    agreement_acceptance_policy: str = "prohibited_without_approval"


class RiskAppetiteProfile:
    """
    Main risk appetite profile for the Theta-Gamma pipeline.

    The profile defines risk tolerance across multiple dimensions:
    - Financial: Budget caps and cost tolerance
    - Data Integrity: Data protection by environment
    - Security: Patching SLAs and access control
    - Availability: Downtime tolerance by environment
    - Velocity: Delivery speed vs quality tradeoffs
    - Technical Debt: Debt acceptance and maintenance
    - Compliance: Legal and regulatory compliance

    Example:
        >>> profile = RiskAppetiteProfile.load_default()
        >>> if profile.financial.monthly_spend > profile.financial.escalation_threshold:
        ...     trigger_budget_alert()
    """

    def __init__(
        self,
        version: str = "1.0.0",
        overall_posture: RiskAppetiteLevel = RiskAppetiteLevel.MODERATE_CONSERVATIVE,
        financial: FinancialRiskConfig | None = None,
        data_integrity: DataIntegrityRiskConfig | None = None,
        security: SecurityRiskConfig | None = None,
        availability: AvailabilityRiskConfig | None = None,
        velocity: VelocityRiskConfig | None = None,
        technical_debt: TechnicalDebtRiskConfig | None = None,
        compliance: ComplianceRiskConfig | None = None,
    ) -> None:
        """
        Initialize the risk appetite profile.

        Args:
            version: Profile version
            overall_posture: Overall risk posture
            financial: Financial risk configuration
            data_integrity: Data integrity risk configuration
            security: Security risk configuration
            availability: Availability risk configuration
            velocity: Velocity risk configuration
            technical_debt: Technical debt risk configuration
            compliance: Compliance risk configuration
        """
        self.version = version
        self.overall_posture = overall_posture
        self.financial = financial or FinancialRiskConfig()
        self.data_integrity = data_integrity or DataIntegrityRiskConfig()
        self.security = security or SecurityRiskConfig()
        self.availability = availability or AvailabilityRiskConfig()
        self.velocity = velocity or VelocityRiskConfig()
        self.technical_debt = technical_debt or TechnicalDebtRiskConfig()
        self.compliance = compliance or ComplianceRiskConfig()

        # Irreversible decision registry
        self._irreversible_decisions: list[dict[str, Any]] = []
        self._initialize_irreversible_decisions()

    def _initialize_irreversible_decisions(self) -> None:
        """Initialize the registry of irreversible decisions."""
        self._irreversible_decisions = [
            {
                "decision": "Production deployment",
                "tier": "T3",
                "why_irreversible": "User-facing state change; rollback is not instant",
            },
            {
                "decision": "Production data deletion",
                "tier": "T4",
                "why_irreversible": "Data cannot be reconstructed",
            },
            {
                "decision": "Production schema migration",
                "tier": "T3",
                "why_irreversible": "May cause data loss or downtime",
            },
            {
                "decision": "Main branch force-push",
                "tier": "T4",
                "why_irreversible": "Rewrites shared history",
            },
            {
                "decision": "External API integration",
                "tier": "T3",
                "why_irreversible": "Creates third-party dependency",
            },
            {
                "decision": "License change",
                "tier": "T3",
                "why_irreversible": "Legal implications",
            },
            {
                "decision": "Access control modification",
                "tier": "T4",
                "why_irreversible": "Security boundary change",
            },
            {
                "decision": "External notification/communication",
                "tier": "T4",
                "why_irreversible": "Cannot be unsent",
            },
            {
                "decision": "Production secret rotation",
                "tier": "T3",
                "why_irreversible": "May break live services",
            },
            {
                "decision": "Backup deletion",
                "tier": "T4",
                "why_irreversible": "Eliminates recovery option",
            },
        ]

    def get_appetite_level(self, dimension: RiskDimension) -> RiskAppetiteLevel:
        """
        Get the appetite level for a risk dimension.

        Args:
            dimension: The risk dimension

        Returns:
            RiskAppetiteLevel for the dimension
        """
        mapping = {
            RiskDimension.FINANCIAL: RiskAppetiteLevel.LOW,
            RiskDimension.DATA_INTEGRITY: RiskAppetiteLevel.VERY_LOW,
            RiskDimension.SECURITY: RiskAppetiteLevel.ZERO,
            RiskDimension.AVAILABILITY: RiskAppetiteLevel.MODERATE,
            RiskDimension.VELOCITY: RiskAppetiteLevel.HIGH,
            RiskDimension.TECHNICAL_DEBT: RiskAppetiteLevel.MODERATE,
            RiskDimension.COMPLIANCE: RiskAppetiteLevel.ZERO,
        }
        return mapping.get(dimension, RiskAppetiteLevel.MODERATE)

    def is_decision_irreversible(self, decision: str) -> bool:
        """
        Check if a decision is classified as irreversible.

        Args:
            decision: The decision to check

        Returns:
            True if the decision is irreversible
        """
        return any(d["decision"].lower() in decision.lower() for d in self._irreversible_decisions)

    def get_irreversible_tier(self, decision: str) -> str | None:
        """
        Get the required tier for an irreversible decision.

        Args:
            decision: The decision to check

        Returns:
            Tier (T3 or T4) or None if not irreversible
        """
        for d in self._irreversible_decisions:
            if d["decision"].lower() in decision.lower():
                return d["tier"]
        return None

    def get_data_policy(self, env: DataEnvironment) -> str:
        """
        Get the data handling policy for an environment.

        Args:
            env: The data environment

        Returns:
            Policy string
        """
        return self.data_integrity.get_policy(env)

    def get_patching_sla(self, severity: str) -> int:
        """
        Get the patching SLA in hours for a severity level.

        Args:
            severity: Severity level ("critical" or "high")

        Returns:
            SLA in hours
        """
        if severity.lower() == "critical":
            return self.security.patching_sla_critical_hours
        elif severity.lower() == "high":
            return self.security.patching_sla_high_hours
        return 168  # Default to 7 days

    def requires_feature_flag(self, is_user_facing: bool) -> bool:
        """
        Check if a feature flag is required.

        Args:
            is_user_facing: Whether the change is user-facing

        Returns:
            True if feature flag is required
        """
        return is_user_facing and self.velocity.feature_flag_required

    def get_min_test_coverage(self) -> float:
        """Get the minimum test coverage percentage for new code."""
        return self.velocity.min_test_coverage_pct

    def is_copyleft_allowed(self) -> bool:
        """Check if copyleft dependencies are allowed."""
        return self.compliance.copyleft_policy != "escalate_immediately"

    def get_irreversible_decisions(self) -> list[dict[str, Any]]:
        """Get the list of irreversible decisions."""
        return self._irreversible_decisions.copy()

    @classmethod
    def load_default(cls) -> RiskAppetiteProfile:
        """Load the default risk appetite profile."""
        return cls()

    @classmethod
    def load_from_yaml(cls, path: Path | str) -> RiskAppetiteProfile:
        """
        Load profile from YAML file.

        Args:
            path: Path to YAML file

        Returns:
            RiskAppetiteProfile instance
        """
        path = Path(path)
        with open(path) as f:
            data = yaml.safe_load(f)

        return cls(
            version=data.get("version", "1.0.0"),
            overall_posture=RiskAppetiteLevel(data.get("overall_posture", "moderate_conservative")),
            financial=FinancialRiskConfig(**data.get("financial", {})),
            data_integrity=DataIntegrityRiskConfig(**data.get("data_integrity", {})),
            security=SecurityRiskConfig(**data.get("security", {})),
            availability=AvailabilityRiskConfig(**data.get("availability", {})),
            velocity=VelocityRiskConfig(**data.get("velocity", {})),
            technical_debt=TechnicalDebtRiskConfig(**data.get("technical_debt", {})),
            compliance=ComplianceRiskConfig(**data.get("compliance", {})),
        )

    def to_yaml(self, path: Path | str) -> None:
        """
        Serialize profile to YAML file.

        Args:
            path: Path to output YAML file
        """
        path = Path(path)
        data = {
            "version": self.version,
            "overall_posture": self.overall_posture.value,
            "financial": {
                "monthly_cap_usd": self.financial.monthly_cap_usd,
                "daily_cap_usd": self.financial.daily_cap_usd,
                "single_action_cap_usd": self.financial.single_action_cap_usd,
                "alert_threshold_pct": self.financial.alert_threshold_pct,
                "tolerance_for_waste_pct": self.financial.tolerance_for_waste_pct,
            },
            "data_integrity": {
                "dev_policy": self.data_integrity.dev_policy,
                "staging_policy": self.data_integrity.staging_policy,
                "production_policy": self.data_integrity.production_policy,
                "backup_retention_days": self.data_integrity.backup_retention_days,
            },
            "security": {
                "patching_sla_critical_hours": self.security.patching_sla_critical_hours,
                "patching_sla_high_hours": self.security.patching_sla_high_hours,
                "secret_rotation_policy": self.security.secret_rotation_policy,
                "access_control_policy": self.security.access_control_policy,
            },
            "availability": {
                "dev_downtime_tolerance": self.availability.dev_downtime_tolerance,
                "staging_downtime_tolerance_hours": self.availability.staging_downtime_tolerance_hours,
                "production_downtime_tolerance_minutes": self.availability.production_downtime_tolerance_minutes,
                "rollback_required": self.availability.rollback_required,
            },
            "velocity": {
                "min_test_coverage_pct": self.velocity.min_test_coverage_pct,
                "draft_pr_policy": self.velocity.draft_pr_policy,
                "merge_policy": self.velocity.merge_policy,
                "feature_flag_required": self.velocity.feature_flag_required,
            },
            "technical_debt": {
                "auto_fix_policy": self.technical_debt.auto_fix_policy,
                "refactoring_policy": self.technical_debt.refactoring_policy,
                "dependency_update_policy": self.technical_debt.dependency_update_policy,
            },
            "compliance": {
                "license_auditing": self.compliance.license_auditing,
                "copyleft_policy": self.compliance.copyleft_policy,
                "data_handling_policy": self.compliance.data_handling_policy,
                "agreement_acceptance_policy": self.compliance.agreement_acceptance_policy,
            },
        }

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
