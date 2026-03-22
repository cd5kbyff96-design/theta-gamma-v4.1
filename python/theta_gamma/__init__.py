"""
Theta-Gamma v4.1 — Autonomous ML Training Pipeline

A production-grade autonomous machine learning training pipeline with
gated milestone progression, budget guardrails, and comprehensive
failure recovery mechanisms.

Core Components:
    - autonomy: Decision authority tiers, risk profiles, failure modes
    - evaluation: Metrics, gates, eval harness, failure signals
    - compute: Budget tracking, training tiers, auto-downgrade rules
    - compiler: Task packet compilation and quality rubrics
    - recovery: State machine for failure recovery, incident management
    - external: Pilot SOW templates, validation checklists
    - weekly_loop: Weekly control loop, prioritization rules
    - decisions: Decision packets, deadline policies

Example:
    >>> from theta_gamma.autonomy import AutonomyContract
    >>> from theta_gamma.evaluation import GateEvaluator
    >>>
    >>> contract = AutonomyContract.load()
    >>> evaluator = GateEvaluator(contract=contract)
    >>> result = evaluator.evaluate_gate("G1", metrics)
"""

from theta_gamma.autonomy.contract import AutonomyContract, DecisionTier, DecisionClass
from theta_gamma.autonomy.risk_profile import RiskAppetiteProfile, RiskDimension
from theta_gamma.autonomy.failure_modes import FailureMode, FailureModeRegistry
from theta_gamma.compute.budget import ComputeBudget, BudgetPolicy
from theta_gamma.compute.tiers import TrainingTier, TierManager
from theta_gamma.evaluation.gates import Gate, GateEvaluator, GateStatus
from theta_gamma.evaluation.metrics import Metric, MetricDictionary
from theta_gamma.recovery.state_machine import RecoveryStateMachine, IncidentState
from theta_gamma.compiler.packets import TaskPacket, PacketDomain, PacketPriority
from theta_gamma.weekly_loop.runbook import WeeklyControlLoop
from theta_gamma.decisions.packets import DecisionPacket, Decision
from theta_gamma.orchestration.pipeline import ThetaGammaPipeline, PipelineState, PipelineMetrics, PipelineConfig
from theta_gamma.orchestration.config import ConfigLoader

__version__ = "4.1.0"
__author__ = "Theta-Gamma Team"

__all__ = [
    # Version
    "__version__",
    # Autonomy
    "AutonomyContract",
    "DecisionTier",
    "DecisionClass",
    "RiskAppetiteProfile",
    "RiskDimension",
    "FailureMode",
    "FailureModeRegistry",
    # Compute
    "ComputeBudget",
    "BudgetPolicy",
    "TrainingTier",
    "TierManager",
    # Evaluation
    "Gate",
    "GateEvaluator",
    "GateStatus",
    "Metric",
    "MetricDictionary",
    # Recovery
    "RecoveryStateMachine",
    "IncidentState",
    # Compiler
    "TaskPacket",
    "PacketDomain",
    "PacketPriority",
    # Weekly Loop
    "WeeklyControlLoop",
    # Decisions
    "DecisionPacket",
    "Decision",
    # Orchestration (new)
    "ThetaGammaPipeline",
    "PipelineState",
    "PipelineMetrics",
    "ConfigLoader",
    "PipelineConfig",
]
