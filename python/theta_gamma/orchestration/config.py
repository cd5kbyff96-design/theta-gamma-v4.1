"""
Configuration Loader — Unified configuration for Theta-Gamma pipeline.

This module provides configuration loading from YAML files and
environment variables for all pipeline components.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


@dataclass
class AutonomyConfig:
    """Autonomy component configuration."""

    contract_path: Path = field(default_factory=lambda: Path("artifacts/A0/00_autonomy_contract.md"))
    decision_matrix_path: Path = field(default_factory=lambda: Path("artifacts/A0/01_decision_matrix.csv"))
    operating_limits_path: Path = field(default_factory=lambda: Path("artifacts/A0/02_operating_limits.yaml"))
    risk_appetite_path: Path = field(default_factory=lambda: Path("artifacts/A0/03_risk_appetite_profile.md"))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AutonomyConfig":
        """Create from dictionary."""
        return cls(
            contract_path=Path(data.get("contract_path", "artifacts/A0/00_autonomy_contract.md")),
            decision_matrix_path=Path(data.get("decision_matrix_path", "artifacts/A0/01_decision_matrix.csv")),
            operating_limits_path=Path(data.get("operating_limits_path", "artifacts/A0/02_operating_limits.yaml")),
            risk_appetite_path=Path(data.get("risk_appetite_path", "artifacts/A0/03_risk_appetite_profile.md")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "contract_path": str(self.contract_path),
            "decision_matrix_path": str(self.decision_matrix_path),
            "operating_limits_path": str(self.operating_limits_path),
            "risk_appetite_path": str(self.risk_appetite_path),
        }


@dataclass
class ComputeConfig:
    """Compute component configuration."""

    budget_policy_path: Path = field(default_factory=lambda: Path("artifacts/A2/01_compute_budget_policy.md"))
    training_tiers_path: Path = field(default_factory=lambda: Path("artifacts/A2/02_training_tier_matrix.csv"))
    downgrade_rules_path: Path = field(default_factory=lambda: Path("artifacts/A2/03_auto_downgrade_rules.md"))
    guardrails_path: Path = field(default_factory=lambda: Path("artifacts/A2/05_budget_guardrails.yaml"))
    monthly_cap_usd: float = 500.0
    daily_cap_usd: float = 50.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ComputeConfig":
        """Create from dictionary."""
        return cls(
            budget_policy_path=Path(data.get("budget_policy_path", "artifacts/A2/01_compute_budget_policy.md")),
            training_tiers_path=Path(data.get("training_tiers_path", "artifacts/A2/02_training_tier_matrix.csv")),
            downgrade_rules_path=Path(data.get("downgrade_rules_path", "artifacts/A2/03_auto_downgrade_rules.md")),
            guardrails_path=Path(data.get("guardrails_path", "artifacts/A2/05_budget_guardrails.yaml")),
            monthly_cap_usd=data.get("monthly_cap_usd", 500.0),
            daily_cap_usd=data.get("daily_cap_usd", 50.0),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "budget_policy_path": str(self.budget_policy_path),
            "training_tiers_path": str(self.training_tiers_path),
            "downgrade_rules_path": str(self.downgrade_rules_path),
            "guardrails_path": str(self.guardrails_path),
            "monthly_cap_usd": self.monthly_cap_usd,
            "daily_cap_usd": self.daily_cap_usd,
        }


@dataclass
class EvaluationConfig:
    """Evaluation component configuration."""

    metric_dictionary_path: Path = field(default_factory=lambda: Path("artifacts/A1/01_metric_dictionary.yaml"))
    gate_definitions_path: Path = field(default_factory=lambda: Path("artifacts/A1/02_gate_definitions.yaml"))
    eval_harness_plan_path: Path = field(default_factory=lambda: Path("artifacts/A1/03_eval_harness_plan.md"))
    dataset_manifest_path: Path = field(default_factory=lambda: Path("artifacts/A1/06_golden_dataset_manifest.csv"))
    results_dir: Path = field(default_factory=lambda: Path("results/eval"))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationConfig":
        """Create from dictionary."""
        return cls(
            metric_dictionary_path=Path(data.get("metric_dictionary_path", "artifacts/A1/01_metric_dictionary.yaml")),
            gate_definitions_path=Path(data.get("gate_definitions_path", "artifacts/A1/02_gate_definitions.yaml")),
            eval_harness_plan_path=Path(data.get("eval_harness_plan_path", "artifacts/A1/03_eval_harness_plan.md")),
            dataset_manifest_path=Path(data.get("dataset_manifest_path", "artifacts/A1/06_golden_dataset_manifest.csv")),
            results_dir=Path(data.get("results_dir", "results/eval")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_dictionary_path": str(self.metric_dictionary_path),
            "gate_definitions_path": str(self.gate_definitions_path),
            "eval_harness_plan_path": str(self.eval_harness_plan_path),
            "dataset_manifest_path": str(self.dataset_manifest_path),
            "results_dir": str(self.results_dir),
        }


@dataclass
class RecoveryConfig:
    """Recovery component configuration."""

    state_machine_path: Path = field(default_factory=lambda: Path("artifacts/A4/01_recovery_state_machine.md"))
    retry_policy_path: Path = field(default_factory=lambda: Path("artifacts/A4/02_retry_policy.yaml"))
    incident_templates_path: Path = field(default_factory=lambda: Path("artifacts/A4/03_incident_templates.md"))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecoveryConfig":
        """Create from dictionary."""
        return cls(
            state_machine_path=Path(data.get("state_machine_path", "artifacts/A4/01_recovery_state_machine.md")),
            retry_policy_path=Path(data.get("retry_policy_path", "artifacts/A4/02_retry_policy.yaml")),
            incident_templates_path=Path(data.get("incident_templates_path", "artifacts/A4/03_incident_templates.md")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "state_machine_path": str(self.state_machine_path),
            "retry_policy_path": str(self.retry_policy_path),
            "incident_templates_path": str(self.incident_templates_path),
        }


@dataclass
class CompilerConfig:
    """Compiler component configuration."""

    artifacts_dir: Path = field(default_factory=lambda: Path("artifacts"))
    packets_dir: Path = field(default_factory=lambda: Path("artifacts/A3/03_compiled_packets"))
    packet_index_path: Path = field(default_factory=lambda: Path("artifacts/A3/04_packet_index.csv"))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompilerConfig":
        """Create from dictionary."""
        return cls(
            artifacts_dir=Path(data.get("artifacts_dir", "artifacts")),
            packets_dir=Path(data.get("packets_dir", "artifacts/A3/03_compiled_packets")),
            packet_index_path=Path(data.get("packet_index_path", "artifacts/A3/04_packet_index.csv")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "artifacts_dir": str(self.artifacts_dir),
            "packets_dir": str(self.packets_dir),
            "packet_index_path": str(self.packet_index_path),
        }


@dataclass
class WeeklyLoopConfig:
    """Weekly loop component configuration."""

    runbook_path: Path = field(default_factory=lambda: Path("artifacts/A6/01_weekly_loop_runbook.md"))
    report_schema_path: Path = field(default_factory=lambda: Path("artifacts/A6/02_weekly_report_schema.yaml"))
    prioritization_rules_path: Path = field(default_factory=lambda: Path("artifacts/A6/03_auto_prioritization_rules.md"))
    reports_dir: Path = field(default_factory=lambda: Path("results/weekly-reports"))
    loop_day: int = 0  # Monday
    loop_hour: int = 9  # 09:00 UTC

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WeeklyLoopConfig":
        """Create from dictionary."""
        return cls(
            runbook_path=Path(data.get("runbook_path", "artifacts/A6/01_weekly_loop_runbook.md")),
            report_schema_path=Path(data.get("report_schema_path", "artifacts/A6/02_weekly_report_schema.yaml")),
            prioritization_rules_path=Path(data.get("prioritization_rules_path", "artifacts/A6/03_auto_prioritization_rules.md")),
            reports_dir=Path(data.get("reports_dir", "results/weekly-reports")),
            loop_day=data.get("loop_day", 0),
            loop_hour=data.get("loop_hour", 9),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "runbook_path": str(self.runbook_path),
            "report_schema_path": str(self.report_schema_path),
            "prioritization_rules_path": str(self.prioritization_rules_path),
            "reports_dir": str(self.reports_dir),
            "loop_day": self.loop_day,
            "loop_hour": self.loop_hour,
        }


@dataclass
class DecisionConfig:
    """Decision component configuration."""

    decision_packet_path: Path = field(default_factory=lambda: Path("artifacts/A7/01_weekly_decision_packet.md"))
    top5_template_path: Path = field(default_factory=lambda: Path("artifacts/A7/02_top5_decisions_template.md"))
    deadline_policy_path: Path = field(default_factory=lambda: Path("artifacts/A7/03_decision_deadline_policy.md"))
    default_action_path: Path = field(default_factory=lambda: Path("artifacts/A7/04_default_action_if_no_response.md"))
    deadline_hours: int = 32  # Tuesday 18:00 UTC for Monday delivery

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DecisionConfig":
        """Create from dictionary."""
        return cls(
            decision_packet_path=Path(data.get("decision_packet_path", "artifacts/A7/01_weekly_decision_packet.md")),
            top5_template_path=Path(data.get("top5_template_path", "artifacts/A7/02_top5_decisions_template.md")),
            deadline_policy_path=Path(data.get("deadline_policy_path", "artifacts/A7/03_decision_deadline_policy.md")),
            default_action_path=Path(data.get("default_action_path", "artifacts/A7/04_default_action_if_no_response.md")),
            deadline_hours=data.get("deadline_hours", 32),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "decision_packet_path": str(self.decision_packet_path),
            "top5_template_path": str(self.top5_template_path),
            "deadline_policy_path": str(self.deadline_policy_path),
            "default_action_path": str(self.default_action_path),
            "deadline_hours": self.deadline_hours,
        }


class ConfigLoader:
    """
    Unified configuration loader for Theta-Gamma pipeline.

    Loads configuration from:
    1. YAML config file (if provided)
    2. Environment variables (THETA_GAMMA_* prefix)
    3. Default values

    Example:
        >>> loader = ConfigLoader("config.yaml")
        >>> config = loader.load()
        >>> print(config.compute.monthly_cap_usd)
    """

    ENV_PREFIX = "THETA_GAMMA_"

    def __init__(self, config_path: Path | None = None) -> None:
        """
        Initialize the configuration loader.

        Args:
            config_path: Path to YAML config file
        """
        self._config_path = config_path
        self._file_config: dict[str, Any] = {}

        if config_path and config_path.exists():
            self._file_config = self._load_yaml(config_path)

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        """Load YAML file."""
        if yaml is None:
            raise ImportError("PyYAML is required for YAML config loading. Install with: pip install pyyaml")

        with open(path, "r") as f:
            return yaml.safe_load(f) or {}

    def _get_env_value(self, key: str, default: Any = None) -> Any:
        """Get value from environment variable."""
        env_key = f"{self.ENV_PREFIX}{key.upper()}"
        value = os.environ.get(env_key, default)

        # Type conversion for common types
        if value is not None:
            if isinstance(default, bool):
                return value.lower() in ("true", "1", "yes")
            elif isinstance(default, (int, float)):
                try:
                    return type(default)(value)
                except (ValueError, TypeError):
                    return default
            elif isinstance(default, Path):
                return Path(value)

        return value

    def _get_value(self, key: str, default: Any, section: str | None = None) -> Any:
        """Get value from file config or environment."""
        # Check file config first
        if section and section in self._file_config:
            file_value = self._file_config[section].get(key)
            if file_value is not None:
                return file_value
        elif not section and key in self._file_config:
            return self._file_config[key]

        # Fall back to environment
        env_key = f"{section}_{key}" if section else key
        return self._get_env_value(env_key, default)

    def load_autonomy_config(self) -> AutonomyConfig:
        """Load autonomy configuration."""
        return AutonomyConfig.from_dict(self._file_config.get("autonomy", {}))

    def load_compute_config(self) -> ComputeConfig:
        """Load compute configuration."""
        return ComputeConfig.from_dict(self._file_config.get("compute", {}))

    def load_evaluation_config(self) -> EvaluationConfig:
        """Load evaluation configuration."""
        return EvaluationConfig.from_dict(self._file_config.get("evaluation", {}))

    def load_recovery_config(self) -> RecoveryConfig:
        """Load recovery configuration."""
        return RecoveryConfig.from_dict(self._file_config.get("recovery", {}))

    def load_compiler_config(self) -> CompilerConfig:
        """Load compiler configuration."""
        return CompilerConfig.from_dict(self._file_config.get("compiler", {}))

    def load_weekly_loop_config(self) -> WeeklyLoopConfig:
        """Load weekly loop configuration."""
        return WeeklyLoopConfig.from_dict(self._file_config.get("weekly_loop", {}))

    def load_decision_config(self) -> DecisionConfig:
        """Load decision configuration."""
        return DecisionConfig.from_dict(self._file_config.get("decisions", {}))

    def load_all(self) -> dict[str, Any]:
        """Load all configurations."""
        return {
            "autonomy": self.load_autonomy_config().to_dict(),
            "compute": self.load_compute_config().to_dict(),
            "evaluation": self.load_evaluation_config().to_dict(),
            "recovery": self.load_recovery_config().to_dict(),
            "compiler": self.load_compiler_config().to_dict(),
            "weekly_loop": self.load_weekly_loop_config().to_dict(),
            "decisions": self.load_decision_config().to_dict(),
        }

    def save(self, path: Path) -> None:
        """Save current configuration to YAML file."""
        if yaml is None:
            raise ImportError("PyYAML is required for YAML config saving. Install with: pip install pyyaml")

        config = self.load_all()

        with open(path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    @classmethod
    def create_default_config(cls, output_path: Path) -> None:
        """Create a default configuration file."""
        loader = cls()
        loader.save(output_path)
