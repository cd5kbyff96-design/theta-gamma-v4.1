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
)
from theta_gamma.training.model import (
    CrossModalModel,
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

__all__ = [
    # Loop
    "TrainingLoop",
    "TrainingConfig",
    "TrainingMetrics",
    "create_model",
    # Model
    "CrossModalModel",
    "ModelConfig",
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
