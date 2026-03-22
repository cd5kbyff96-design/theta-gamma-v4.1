"""
Orchestration module — Main pipeline orchestrator and configuration.

This module provides the central orchestration for the Theta-Gamma pipeline,
wiring together all components into a cohesive autonomous system.
"""

from theta_gamma.orchestration.pipeline import (
    ThetaGammaPipeline,
    PipelineState,
    PipelineMetrics,
    PipelineConfig,
)
from theta_gamma.orchestration.config import (
    ConfigLoader,
    AutonomyConfig,
    ComputeConfig,
    EvaluationConfig,
    RecoveryConfig,
    CompilerConfig,
    WeeklyLoopConfig,
    DecisionConfig,
)

__all__ = [
    # Pipeline
    "ThetaGammaPipeline",
    "PipelineState",
    "PipelineMetrics",
    "PipelineConfig",
    # Config
    "ConfigLoader",
    "AutonomyConfig",
    "ComputeConfig",
    "EvaluationConfig",
    "RecoveryConfig",
    "CompilerConfig",
    "WeeklyLoopConfig",
    "DecisionConfig",
]
