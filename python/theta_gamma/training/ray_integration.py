"""
Ray Integration — Distributed training with Ray.

Provides distributed training support using Ray Train.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RayConfig:
    """Ray distributed training configuration."""

    num_workers: int = 4
    use_gpu: bool = True
    resources_per_worker: dict[str, float] | None = None
    storage_path: str = "/tmp/ray_storage"

    def __post_init__(self) -> None:
        if self.resources_per_worker is None:
            self.resources_per_worker = {"CPU": 4, "GPU": 1}


def is_ray_available() -> bool:
    """Check if Ray is available."""
    try:
        import ray
        return True
    except ImportError:
        return False


def initialize_ray(config: RayConfig | None = None) -> Any:
    """
    Initialize Ray cluster.

    Args:
        config: Ray configuration

    Returns:
        Ray context info
    """
    if not is_ray_available():
        raise ImportError(
            "Ray is required for distributed training. "
            "Install with: pip install ray[train]"
        )

    import ray

    config = config or RayConfig()

    ray.init(
        storage=config.storage_path,
        _temp_dir=config.storage_path,
    )

    return {
        "dashboard_url": ray.get_dashboard_url() if hasattr(ray, "get_dashboard_url") else "N/A",
        "num_cpus": ray.cluster_resources().get("CPU", 0),
        "num_gpus": ray.cluster_resources().get("GPU", 0),
    }


def create_distributed_training_func(
    model_class: Any,
    config: dict[str, Any],
) -> Any:
    """
    Create a distributed training function for Ray.

    Args:
        model_class: Model class to train
        config: Training configuration

    Returns:
        Ray-compatible training function
    """
    from ray import train

    def train_func() -> dict[str, Any]:
        """Distributed training function."""
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, DistributedSampler

        # Get distributed model
        model = model_class(**config)
        model = train.torch.prepare_model(model)

        # Prepare data loader with distributed sampler
        # In production, would load actual data
        train_dataset = torch.randn(1000, config.get("hidden_size", 768))
        sampler = DistributedSampler(train_dataset)
        train_loader = DataLoader(train_dataset, sampler=sampler)

        # Training loop
        optimizer = torch.optim.AdamW(model.parameters(), lr=config.get("learning_rate", 1e-4))
        criterion = nn.MSELoss()

        model.train()
        for epoch in range(config.get("epochs", 1)):
            for batch in train_loader:
                optimizer.zero_grad()
                outputs = model(batch)
                loss = criterion(outputs, batch)
                loss.backward()
                optimizer.step()

                # Report metrics to Ray
                train.report({"loss": loss.item(), "epoch": epoch})

        return {"status": "completed"}

    return train_func


def run_distributed_training(
    train_func: Any,
    ray_config: RayConfig,
) -> dict[str, Any]:
    """
    Run distributed training on Ray.

    Args:
        train_func: Training function
        ray_config: Ray configuration

    Returns:
        Training results
    """
    if not is_ray_available():
        raise ImportError("Ray is required")

    from ray.train import ScalingConfig
    from ray.train.torch import TorchTrainer

    trainer = TorchTrainer(
        train_loop_per_worker=train_func,
        scaling_config=ScalingConfig(
            num_workers=ray_config.num_workers,
            use_gpu=ray_config.use_gpu,
        ),
    )

    result = trainer.fit()

    return {
        "status": "completed" if result.error is None else "failed",
        "error": str(result.error) if result.error else None,
        "metrics": result.metrics if hasattr(result, "metrics") else {},
    }
