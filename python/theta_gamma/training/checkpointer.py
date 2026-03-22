"""
Checkpointer — Training checkpoint management.
"""

from __future__ import annotations

import json
import torch
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class CheckpointConfig:
    """Checkpoint configuration."""

    save_dir: Path = field(default_factory=lambda: Path("checkpoints"))
    save_every_n_steps: int = 1000
    keep_last_n: int = 3
    save_optimizer: bool = True
    save_scheduler: bool = True


class Checkpointer:
    """
    Training checkpointer.

    Manages checkpoint saving, loading, and cleanup.
    """

    def __init__(self, config: CheckpointConfig | None = None) -> None:
        """Initialize checkpointer."""
        self._config = config or CheckpointConfig()
        self._saved_checkpoints: list[Path] = []

    def save(
        self,
        model: torch.nn.Module,
        step: int,
        metrics: dict[str, Any],
        optimizer: torch.optim.Optimizer | None = None,
        scheduler: Any | None = None,
    ) -> Path:
        """
        Save a checkpoint.

        Args:
            model: Model to save
            step: Training step
            metrics: Metrics to save
            optimizer: Optimizer state
            scheduler: Scheduler state

        Returns:
            Path to saved checkpoint
        """
        self._config.save_dir.mkdir(parents=True, exist_ok=True)

        checkpoint_id = f"ckpt-step-{step:06d}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        checkpoint_path = self._config.save_dir / f"{checkpoint_id}.pt"

        checkpoint = {
            "step": step,
            "metrics": metrics,
            "saved_at": datetime.now().isoformat(),
        }

        # Model state
        checkpoint["model_state_dict"] = model.state_dict()

        # Optimizer state
        if optimizer and self._config.save_optimizer:
            checkpoint["optimizer_state_dict"] = optimizer.state_dict()

        # Scheduler state
        if scheduler and self._config.save_scheduler:
            checkpoint["scheduler_state_dict"] = scheduler.state_dict()

        torch.save(checkpoint, checkpoint_path)
        self._saved_checkpoints.append(checkpoint_path)

        # Cleanup old checkpoints
        self._cleanup()

        # Save metadata
        self._save_metadata(checkpoint_id, checkpoint_path, metrics)

        return checkpoint_path

    def load(
        self,
        model: torch.nn.Module,
        checkpoint_path: Path | str,
        optimizer: torch.optim.Optimizer | None = None,
        scheduler: Any | None = None,
    ) -> dict[str, Any]:
        """
        Load a checkpoint.

        Args:
            model: Model to load into
            checkpoint_path: Path to checkpoint
            optimizer: Optimizer to load into
            scheduler: Scheduler to load into

        Returns:
            Checkpoint metadata
        """
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)

        # Load model state
        model.load_state_dict(checkpoint["model_state_dict"])

        # Load optimizer state
        if optimizer and "optimizer_state_dict" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

        # Load scheduler state
        if scheduler and "scheduler_state_dict" in checkpoint:
            scheduler.load_state_dict(checkpoint["scheduler_state_dict"])

        return {
            "step": checkpoint.get("step", 0),
            "metrics": checkpoint.get("metrics", {}),
            "saved_at": checkpoint.get("saved_at", ""),
        }

    def _cleanup(self) -> None:
        """Remove old checkpoints."""
        if len(self._saved_checkpoints) <= self._config.keep_last_n:
            return

        # Sort by modification time
        self._saved_checkpoints.sort(key=lambda p: p.stat().st_mtime)

        # Remove oldest
        while len(self._saved_checkpoints) > self._config.keep_last_n:
            old_checkpoint = self._saved_checkpoints.pop(0)
            if old_checkpoint.exists():
                old_checkpoint.unlink()

    def _save_metadata(
        self,
        checkpoint_id: str,
        checkpoint_path: Path,
        metrics: dict[str, Any],
    ) -> None:
        """Save checkpoint metadata."""
        metadata_path = self._config.save_dir / "checkpoints.json"

        metadata = {
            "checkpoint_id": checkpoint_id,
            "path": str(checkpoint_path),
            "size_bytes": checkpoint_path.stat().st_size,
            "metrics": metrics,
            "saved_at": datetime.now().isoformat(),
        }

        # Load existing metadata
        existing = []
        if metadata_path.exists():
            with open(metadata_path) as f:
                existing = json.load(f)

        existing.append(metadata)

        # Keep only last N
        existing = existing[-self._config.keep_last_n:]

        with open(metadata_path, "w") as f:
            json.dump(existing, f, indent=2)

    def list_checkpoints(self) -> list[dict[str, Any]]:
        """List available checkpoints."""
        metadata_path = self._config.save_dir / "checkpoints.json"

        if not metadata_path.exists():
            return []

        with open(metadata_path) as f:
            return json.load(f)

    def get_latest(self) -> Path | None:
        """Get latest checkpoint path."""
        checkpoints = self.list_checkpoints()
        if not checkpoints:
            return None

        return Path(checkpoints[-1]["path"])
