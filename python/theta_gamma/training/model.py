"""
Model — Cross-modal transformer model definitions.

Note: CrossModalModel is only available when PyTorch is installed.
"""

try:
    from theta_gamma.training.loop import CrossModalModel, ModelConfig
    __all__ = ["CrossModalModel", "ModelConfig"]
except (ImportError, NameError):
    # PyTorch not available - only export ModelConfig dataclass
    from theta_gamma.training.loop import ModelConfig
    CrossModalModel = None  # type: ignore
    __all__ = ["ModelConfig"]
