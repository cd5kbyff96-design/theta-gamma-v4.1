"""
Autonomy Contract — Governs all autonomous decisions in the Theta-Gamma pipeline.

This module implements the decision authority tiers, reversibility classification,
and logging requirements defined in the autonomy contract specification.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


class DecisionTier(str, Enum):
    """
    Decision authority tiers defining the level of human oversight required.

    Tiers range from T0 (full autonomy) to T4 (prohibited):

    - T0: Full Auto — Agent proceeds without asking
    - T1: Log & Proceed — Agent proceeds and logs rationale
    - T2: Notify & Proceed — Agent proceeds, sends async notification
    - T3: Approval Required — Agent pauses, requests human approval
    - T4: Prohibited — Agent must never execute
    """

    T0 = "T0"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"

    @property
    def requires_approval(self) -> bool:
        """Check if this tier requires human approval before execution."""
        return self in (self.T3, self.T4)

    @property
    def requires_notification(self) -> bool:
        """Check if this tier requires notification."""
        return self in (self.T1, self.T2, self.T3)

    @property
    def is_prohibited(self) -> bool:
        """Check if this tier is prohibited from autonomous execution."""
        return self == self.T4


class ReversibilityClassification(str, Enum):
    """
    Classification of decision reversibility.

    A decision is reversible if:
    - The prior state can be fully restored within 1 hour
    - No data has been permanently deleted or transmitted externally
    - No third-party system has been irreversibly modified
    """

    REVERSIBLE = "reversible"
    IRREVERSIBLE = "irreversible"


class DecisionClass(BaseModel):
    """
    A categorized decision type with assigned authority tier.

    Attributes:
        id: Unique identifier (e.g., "DC-001")
        name: Human-readable name
        description: Detailed description of the decision scope
        tier: Authority tier required for this decision
        reversibility: Whether the decision is reversible
        scope: List of actions covered by this decision class
        examples: Concrete examples of decisions in this class
    """

    id: str = Field(..., description="Unique identifier (e.g., 'DC-001')")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Detailed description")
    tier: DecisionTier = Field(..., description="Authority tier")
    reversibility: ReversibilityClassification = Field(
        ..., description="Reversibility classification"
    )
    scope: list[str] = Field(default_factory=list, description="Actions covered")
    examples: list[str] = Field(default_factory=list, description="Concrete examples")

    model_config = ConfigDict(frozen=True)


@dataclass
class DecisionLogEntry:
    """
    A logged autonomous decision entry.

    Every autonomous decision must produce a log entry with:
    - timestamp: ISO-8601 format
    - decision_class: From decision matrix
    - tier: T0|T1|T2
    - choice_made: default|fallback
    - rationale: One-line explanation
    - reversible: yes|no
    - artifacts_affected: List of files/resources
    """

    timestamp: datetime
    decision_class: str
    tier: DecisionTier
    choice_made: str  # "default" or "fallback"
    rationale: str
    reversible: bool
    artifacts_affected: list[str]
    override: bool = False
    amendment: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "decision_class": self.decision_class,
            "tier": self.tier.value,
            "choice_made": self.choice_made,
            "rationale": self.rationale,
            "reversible": "yes" if self.reversible else "no",
            "artifacts_affected": self.artifacts_affected,
            "override": self.override,
            "amendment": self.amendment,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DecisionLogEntry:
        """Create from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            decision_class=data["decision_class"],
            tier=DecisionTier(data["tier"]),
            choice_made=data["choice_made"],
            rationale=data["rationale"],
            reversible=data["reversible"] == "yes",
            artifacts_affected=data.get("artifacts_affected", []),
            override=data.get("override", False),
            amendment=data.get("amendment", False),
        )


class AutonomyContract:
    """
    Main contract governing autonomous execution.

    The contract defines:
    - Decision authority tiers (T0-T4)
    - Reversibility classification rules
    - Permitted autonomous actions (T0-T2)
    - Escalation-required actions (T3)
    - Prohibited actions (T4)
    - Logging requirements

    Example:
        >>> contract = AutonomyContract.load_default()
        >>> tier = contract.get_tier_for_action("file_creation")
        >>> if tier.requires_approval:
        ...     await request_human_approval(action)
        >>> else:
        ...     await execute_autonomously(action)
    """

    def __init__(
        self,
        version: str = "1.0.0",
        decision_classes: list[DecisionClass] | None = None,
        log_path: Path | None = None,
    ) -> None:
        """
        Initialize the autonomy contract.

        Args:
            version: Contract version number
            decision_classes: List of defined decision classes
            log_path: Path to decision log file
        """
        self.version = version
        self._decision_classes: dict[str, DecisionClass] = {}
        self._log_path = log_path or Path("decision_log.md")

        if decision_classes:
            for dc in decision_classes:
                self._decision_classes[dc.id] = dc

        self._initialize_default_decision_classes()

    def _initialize_default_decision_classes(self) -> None:
        """Initialize default decision classes from the contract specification."""
        defaults = [
            # T0 - Full Auto (Reversible, cost < $5, no external side effects)
            DecisionClass(
                id="DC-001",
                name="File Creation/Modification",
                description="Create, modify, or delete files within project workspace",
                tier=DecisionTier.T0,
                reversibility=ReversibilityClassification.REVERSIBLE,
                scope=["file creation", "file modification", "file deletion"],
                examples=["Creating config files", "Updating documentation"],
            ),
            DecisionClass(
                id="DC-002",
                name="Dependency Installation",
                description="Install dependencies from approved registries",
                tier=DecisionTier.T0,
                reversibility=ReversibilityClassification.REVERSIBLE,
                scope=["npm install", "pip install", "cargo add"],
                examples=["Installing patch updates", "Adding dev dependencies"],
            ),
            DecisionClass(
                id="DC-003",
                name="Test Execution",
                description="Run test suites and linters",
                tier=DecisionTier.T0,
                reversibility=ReversibilityClassification.REVERSIBLE,
                scope=["pytest", "npm test", "linting", "type checking"],
                examples=["Running unit tests", "Running linter"],
            ),
            DecisionClass(
                id="DC-004",
                name="Git Operations",
                description="Create branches, commits, and draft PRs",
                tier=DecisionTier.T0,
                reversibility=ReversibilityClassification.REVERSIBLE,
                scope=["git branch", "git commit", "gh pr create --draft"],
                examples=["Creating feature branch", "Committing changes"],
            ),
            DecisionClass(
                id="DC-005",
                name="Ephemeral Compute",
                description="Spin up dev/test compute within monthly cap",
                tier=DecisionTier.T0,
                reversibility=ReversibilityClassification.REVERSIBLE,
                scope=["dev environment", "test compute"],
                examples=["Starting dev VM", "Running benchmark"],
            ),
            # T1 - Log & Proceed (Reversible, cost $5-$50)
            DecisionClass(
                id="DC-010",
                name="Schema Migration (Dev/Test)",
                description="Schema migrations on dev/test databases",
                tier=DecisionTier.T1,
                reversibility=ReversibilityClassification.REVERSIBLE,
                scope=["dev database", "test database"],
                examples=["Adding dev table", "Updating test schema"],
            ),
            DecisionClass(
                id="DC-011",
                name="CI Job Retry",
                description="Retry failed CI jobs (max 2 retries)",
                tier=DecisionTier.T1,
                reversibility=ReversibilityClassification.REVERSIBLE,
                scope=["ci retry"],
                examples=["Retrying failed test", "Retrying build"],
            ),
            DecisionClass(
                id="DC-012",
                name="Library Version Selection",
                description="Select between equivalent library versions",
                tier=DecisionTier.T1,
                reversibility=ReversibilityClassification.REVERSIBLE,
                scope=["patch version", "minor version"],
                examples=["Choosing patch update", "Minor version upgrade"],
            ),
            # T2 - Notify & Proceed (Reversible, cost $50-$200)
            DecisionClass(
                id="DC-020",
                name="Staging Schema Migration",
                description="Schema migrations on staging (with logging)",
                tier=DecisionTier.T2,
                reversibility=ReversibilityClassification.REVERSIBLE,
                scope=["staging database"],
                examples=["Staging table addition"],
            ),
            DecisionClass(
                id="DC-021",
                name="Test Changes (Security-Critical)",
                description="Test modifications for security-critical paths",
                tier=DecisionTier.T2,
                reversibility=ReversibilityClassification.REVERSIBLE,
                scope=["security tests"],
                examples=["Adding auth tests"],
            ),
            # T3 - Approval Required (Irreversible OR cost > $200)
            DecisionClass(
                id="DC-030",
                name="Production Deployment",
                description="Any release to production infrastructure",
                tier=DecisionTier.T3,
                reversibility=ReversibilityClassification.IRREVERSIBLE,
                scope=["production deploy"],
                examples=["Deploying to prod"],
            ),
            DecisionClass(
                id="DC-031",
                name="Production Database Migration",
                description="Schema changes affecting live data",
                tier=DecisionTier.T3,
                reversibility=ReversibilityClassification.IRREVERSIBLE,
                scope=["production database"],
                examples=["Adding production column"],
            ),
            DecisionClass(
                id="DC-032",
                name="Major Dependency Upgrade",
                description="Semver major version bumps",
                tier=DecisionTier.T3,
                reversibility=ReversibilityClassification.REVERSIBLE,
                scope=["major version"],
                examples=["React 17 to 18"],
            ),
            DecisionClass(
                id="DC-033",
                name="External API Integration",
                description="Connecting to new third-party services",
                tier=DecisionTier.T3,
                reversibility=ReversibilityClassification.IRREVERSIBLE,
                scope=["external api"],
                examples=["Adding Stripe integration"],
            ),
            DecisionClass(
                id="DC-034",
                name="Security Configuration",
                description="Auth, encryption, access control changes",
                tier=DecisionTier.T3,
                reversibility=ReversibilityClassification.IRREVERSIBLE,
                scope=["security config"],
                examples=["Changing auth provider"],
            ),
            DecisionClass(
                id="DC-035",
                name="Cost Commitment",
                description="Actions exceeding $200 or creating recurring cost",
                tier=DecisionTier.T3,
                reversibility=ReversibilityClassification.IRREVERSIBLE,
                scope=["cost > $200"],
                examples=["Reserved instance purchase"],
            ),
            # T4 - Prohibited
            DecisionClass(
                id="DC-040",
                name="Force Push to Main",
                description="Force-pushing to main/production branches",
                tier=DecisionTier.T4,
                reversibility=ReversibilityClassification.IRREVERSIBLE,
                scope=["force push main"],
                examples=[],
            ),
            DecisionClass(
                id="DC-041",
                name="Production Data Deletion",
                description="Deleting production data or backups",
                tier=DecisionTier.T4,
                reversibility=ReversibilityClassification.IRREVERSIBLE,
                scope=["production data deletion"],
                examples=[],
            ),
            DecisionClass(
                id="DC-042",
                name="Production IAM Modification",
                description="Modifying production access controls or IAM",
                tier=DecisionTier.T4,
                reversibility=ReversibilityClassification.IRREVERSIBLE,
                scope=["production iam"],
                examples=[],
            ),
            DecisionClass(
                id="DC-043",
                name="Secret Exposure",
                description="Exposing secrets, tokens, or credentials",
                tier=DecisionTier.T4,
                reversibility=ReversibilityClassification.IRREVERSIBLE,
                scope=["secrets"],
                examples=[],
            ),
            DecisionClass(
                id="DC-044",
                name="External Communication",
                description="Sending communications to external users/customers",
                tier=DecisionTier.T4,
                reversibility=ReversibilityClassification.IRREVERSIBLE,
                scope=["external communication"],
                examples=[],
            ),
        ]

        for dc in defaults:
            if dc.id not in self._decision_classes:
                self._decision_classes[dc.id] = dc

    def get_tier_for_action(self, action_type: str) -> DecisionTier:
        """
        Get the authority tier for a given action type.

        Args:
            action_type: The type of action being considered

        Returns:
            The DecisionTier required for this action

        Example:
            >>> contract.get_tier_for_action("file_creation")
            <DecisionTier.T0: 'T0'>
        """
        # Normalize: replace underscores with spaces for flexible matching
        normalized_action = action_type.lower().replace("_", " ")
        # Search decision classes for matching scope
        for dc in self._decision_classes.values():
            if any(normalized_action in scope.lower() for scope in dc.scope):
                return dc.tier

        # Default to T3 for unknown actions (conservative)
        return DecisionTier.T3

    def get_decision_class(self, class_id: str) -> DecisionClass | None:
        """
        Get a decision class by ID.

        Args:
            class_id: The decision class ID (e.g., "DC-001")

        Returns:
            The DecisionClass or None if not found
        """
        return self._decision_classes.get(class_id)

    def classify_action(
        self, action_type: str, cost_usd: float = 0.0, is_external: bool = False
    ) -> tuple[DecisionTier, ReversibilityClassification]:
        """
        Classify an action and determine required authority tier.

        Args:
            action_type: The type of action
            cost_usd: Estimated cost in USD
            is_external: Whether action has external side effects

        Returns:
            Tuple of (DecisionTier, ReversibilityClassification)
        """
        base_tier = self.get_tier_for_action(action_type)
        reversibility = self._assess_reversibility(action_type, is_external)

        # Adjust tier based on cost
        if cost_usd > 200 and base_tier != DecisionTier.T4:
            base_tier = DecisionTier.T3
        elif 50 < cost_usd <= 200 and base_tier == DecisionTier.T0:
            base_tier = DecisionTier.T2
        elif 5 < cost_usd <= 50 and base_tier == DecisionTier.T0:
            base_tier = DecisionTier.T1

        # Irreversible actions always require at least T3
        if reversibility == ReversibilityClassification.IRREVERSIBLE:
            if base_tier not in (DecisionTier.T3, DecisionTier.T4):
                base_tier = DecisionTier.T3

        return base_tier, reversibility

    def _assess_reversibility(
        self, action_type: str, is_external: bool
    ) -> ReversibilityClassification:
        """
        Assess whether an action is reversible.

        Args:
            action_type: The type of action
            is_external: Whether action has external side effects

        Returns:
            ReversibilityClassification
        """
        irreversible_patterns = [
            "production",
            "delete",
            "destroy",
            "external",
            "deploy",
            "force",
        ]

        if is_external:
            return ReversibilityClassification.IRREVERSIBLE

        if any(pattern in action_type.lower() for pattern in irreversible_patterns):
            return ReversibilityClassification.IRREVERSIBLE

        return ReversibilityClassification.REVERSIBLE

    def log_decision(self, entry: DecisionLogEntry) -> None:
        """
        Log an autonomous decision.

        Args:
            entry: The decision log entry

        Example:
            >>> entry = DecisionLogEntry(
            ...     timestamp=datetime.now(),
            ...     decision_class="DC-001",
            ...     tier=DecisionTier.T0,
            ...     choice_made="default",
            ...     rationale="Created config file",
            ...     reversible=True,
            ...     artifacts_affected=["config.yaml"],
            ... )
            >>> contract.log_decision(entry)
        """
        log_content = f"- {entry.to_dict()}\n"

        with open(self._log_path, "a") as f:
            f.write(log_content)

    def get_all_decision_classes(self) -> list[DecisionClass]:
        """Get all registered decision classes."""
        return list(self._decision_classes.values())

    @classmethod
    def load_default(cls) -> AutonomyContract:
        """Load the default autonomy contract."""
        return cls()

    @classmethod
    def load_from_yaml(cls, path: Path | str) -> AutonomyContract:
        """
        Load contract from YAML file.

        Args:
            path: Path to YAML file

        Returns:
            AutonomyContract instance
        """
        path = Path(path)
        with open(path) as f:
            data = yaml.safe_load(f)

        decision_classes = [
            DecisionClass(
                id=dc["id"],
                name=dc["name"],
                description=dc["description"],
                tier=DecisionTier(dc["tier"]),
                reversibility=ReversibilityClassification(dc["reversibility"]),
                scope=dc.get("scope", []),
                examples=dc.get("examples", []),
            )
            for dc in data.get("decision_classes", [])
        ]

        return cls(
            version=data.get("version", "1.0.0"),
            decision_classes=decision_classes,
            log_path=Path(data.get("log_path", "decision_log.md")),
        )

    def to_yaml(self, path: Path | str) -> None:
        """
        Serialize contract to YAML file.

        Args:
            path: Path to output YAML file
        """
        path = Path(path)
        data = {
            "version": self.version,
            "log_path": str(self._log_path),
            "decision_classes": [
                {
                    "id": dc.id,
                    "name": dc.name,
                    "description": dc.description,
                    "tier": dc.tier.value,
                    "reversibility": dc.reversibility.value,
                    "scope": dc.scope,
                    "examples": dc.examples,
                }
                for dc in self._decision_classes.values()
            ],
        }

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
