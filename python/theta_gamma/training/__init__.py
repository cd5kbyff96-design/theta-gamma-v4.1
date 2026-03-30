"""
Training module — PyTorch/Lightning training integration.

Provides actual training loop implementation with:
- FSDP/DeepSpeed support
- Checkpointing
- Metric emission
- Cost tracking
- Ray distributed training
"""

from theta_gamma.training.loop import (
    TrainingLoop,
    TrainingConfig,
    TrainingMetrics,
    create_model,
    ModelConfig,
)
from theta_gamma.training.checkpointer import (
    Checkpointer,
    CheckpointConfig,
)
from theta_gamma.training.ray_integration import (
    RayConfig,
    is_ray_available,
    initialize_ray,
    create_distributed_training_func,
    run_distributed_training,
)

# CrossModalModel is only available when PyTorch is installed
try:
    from theta_gamma.training.loop import CrossModalModel
except (ImportError, NameError):
    CrossModalModel = None  # type: ignore

__all__ = [
    # Loop
    "TrainingLoop",
    "TrainingConfig",
    "TrainingMetrics",
    "create_model",
    "ModelConfig",
    # Model (only when torch available)
    "CrossModalModel",
    # Checkpointer
    "Checkpointer",
    "CheckpointConfig",
    # Ray
    "RayConfig",
    "is_ray_available",
    "initialize_ray",
    "create_distributed_training_func",
    "run_distributed_training",
]
