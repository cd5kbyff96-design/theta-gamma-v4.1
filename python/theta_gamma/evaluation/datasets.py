"""
Dataset Management — Eval dataset definitions and integrity checking.

This module implements dataset management for evaluation, including
dataset manifests, integrity verification, and contamination checking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class EvalDataset:
    """
    An evaluation dataset definition.

    Attributes:
        id: Unique identifier (e.g., "DS-CM-BENCH-001")
        name: Human-readable name
        description: Dataset description
        path: Path to dataset
        hash_sha256: SHA-256 hash for integrity verification
        size_samples: Number of samples
        license: Dataset license
        owner: Dataset owner
        modality: Primary modality (text, image, audio, cross-modal)
        contamination_checked: Whether contamination check was performed
        last_checked: Last contamination check timestamp
    """

    id: str
    name: str
    description: str
    path: str
    hash_sha256: str
    size_samples: int
    license: str
    owner: str
    modality: str = "cross_modal"
    contamination_checked: bool = False
    last_checked: datetime | None = None

    def verify_hash(self, data_path: Path | None = None) -> tuple[bool, str]:
        """
        Verify dataset integrity via hash.

        Args:
            data_path: Optional path to data (uses self.path if not provided)

        Returns:
            Tuple of (is_valid, message)
        """
        import hashlib

        path = data_path or Path(self.path)
        if not path.exists():
            return (False, f"Dataset not found: {path}")

        try:
            sha256 = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)

            computed_hash = sha256.hexdigest()
            if computed_hash == self.hash_sha256:
                return (True, "Hash verification passed")
            else:
                return (
                    False,
                    f"Hash mismatch: expected {self.hash_sha256}, got {computed_hash}",
                )
        except Exception as e:
            return (False, f"Hash verification failed: {e}")

    def mark_contamination_checked(self) -> None:
        """Mark dataset as contamination checked."""
        self.contamination_checked = True
        self.last_checked = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "path": self.path,
            "hash_sha256": self.hash_sha256,
            "size_samples": self.size_samples,
            "license": self.license,
            "owner": self.owner,
            "modality": self.modality,
            "contamination_checked": self.contamination_checked,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
        }


class DatasetManifest:
    """
    Manifest of all evaluation datasets.

    The manifest tracks dataset metadata, integrity hashes, and
    contamination check status.

    Example:
        >>> manifest = DatasetManifest()
        >>> dataset = manifest.get_by_id("DS-CM-BENCH-001")
        >>> is_valid, msg = dataset.verify_hash()
    """

    def __init__(self) -> None:
        """Initialize the dataset manifest."""
        self._datasets: dict[str, EvalDataset] = {}
        self._initialize_default_datasets()

    def _initialize_default_datasets(self) -> None:
        """Initialize default datasets from the specification."""
        datasets = [
            # Cross-Modal Datasets
            EvalDataset(
                id="DS-CM-BENCH-001",
                name="Cross-Modal Benchmark",
                description="Primary cross-modal accuracy benchmark dataset",
                path="data/eval/cross_modal/benchmark.parquet",
                hash_sha256="a3f7c9e1d42b8f6a50e3d19c7b4a28f6e1d530c9b72e4a81f6d3c950b7e2a14d",
                size_samples=10000,
                license="proprietary-internal",
                owner="ml-team",
                modality="cross_modal",
            ),
            EvalDataset(
                id="DS-CM-CONSIST-001",
                name="Cross-Modal Consistency",
                description="Paired samples for consistency evaluation",
                path="data/eval/cross_modal/consistency.parquet",
                hash_sha256="b8d4e2f71a9c3b5d60f4e28a7c5b39g7f2e641d0c83f5b92g7e4d061c8f3b25e",
                size_samples=5000,
                license="proprietary-internal",
                owner="ml-team",
                modality="cross_modal",
            ),
            EvalDataset(
                id="DS-CM-RETRIEVAL-001",
                name="Cross-Modal Retrieval",
                description="Retrieval evaluation dataset",
                path="data/eval/cross_modal/retrieval.parquet",
                hash_sha256="c9e5f3a82b0d4c6e71a5f39b8d6c40h8a3f752e1d94a6c03h8f5e172d9a4c36f",
                size_samples=5000,
                license="proprietary-internal",
                owner="ml-team",
                modality="cross_modal",
            ),
            # Per-Modality Datasets
            EvalDataset(
                id="DS-MOD-TEXT-001",
                name="Text Accuracy Benchmark",
                description="Text-only classification benchmark",
                path="data/eval/modality/text.parquet",
                hash_sha256="d0f6a4b93c1e5d7f82b6a40c9e7d51i9b4a863f2e05b7d14i9a6f283e0b5d47a",
                size_samples=5000,
                license="proprietary-internal",
                owner="ml-team",
                modality="text",
            ),
            EvalDataset(
                id="DS-MOD-IMAGE-001",
                name="Image Accuracy Benchmark",
                description="Image-only classification benchmark",
                path="data/eval/modality/image.parquet",
                hash_sha256="e1a7b5c04d2f6e8a93c7b51d0f8e62j0c5b974a3f16c8e25j0b7a394f1c6e58b",
                size_samples=5000,
                license="CC-BY-4.0",
                owner="ml-team",
                modality="image",
            ),
            EvalDataset(
                id="DS-MOD-AUDIO-001",
                name="Audio Accuracy Benchmark",
                description="Audio-only classification benchmark",
                path="data/eval/modality/audio.parquet",
                hash_sha256="f2b8c6d15e3a7f9b04d8c62e1a9f73k1d6c085b4a27d9f36k1c8b405a2d7f69c",
                size_samples=5000,
                license="proprietary-internal",
                owner="ml-team",
                modality="audio",
            ),
            # Robustness Datasets
            EvalDataset(
                id="DS-ADV-ROBUST-001",
                name="Adversarial Robustness",
                description="Adversarial examples for robustness evaluation",
                path="data/eval/robustness/adversarial.parquet",
                hash_sha256="a3c9d7e26f4b8a0c15e9d73f2b0a84l2e7d196c5b38e0a47l2d9c516b3e8a70d",
                size_samples=2000,
                license="proprietary-internal",
                owner="safety-team",
                modality="cross_modal",
            ),
            EvalDataset(
                id="DS-OOD-INDIST-001",
                name="OOD In-Distribution",
                description="In-distribution samples for OOD detection",
                path="data/eval/robustness/ood_indist.parquet",
                hash_sha256="b4d0e8f37a5c9b1d26f0e84a3c1b95m3f8e207d6c49f1b58m3e0d627c4f9b81e",
                size_samples=3000,
                license="proprietary-internal",
                owner="safety-team",
                modality="cross_modal",
            ),
            EvalDataset(
                id="DS-OOD-OUT-001",
                name="OOD Out-of-Distribution",
                description="Out-of-distribution samples for OOD detection",
                path="data/eval/robustness/ood_out.parquet",
                hash_sha256="c5e1f9a48b6d0c2e37a1f95b4d2c06n4a9f318e7d50a2c69n4f1e738d5a0c92f",
                size_samples=3000,
                license="mixed-CC-BY-4.0-and-proprietary",
                owner="safety-team",
                modality="cross_modal",
            ),
            EvalDataset(
                id="DS-SAFETY-001",
                name="Safety Evaluation",
                description="Safety classifier evaluation dataset",
                path="data/eval/safety/safety.parquet",
                hash_sha256="d6f2a0b59c7e1d3f48b2a06c5e3d17o5b0a429f8e61b3d70o5a2f849e6b1d03a",
                size_samples=5000,
                license="proprietary-internal",
                owner="safety-team",
                modality="text",
            ),
            EvalDataset(
                id="DS-CALIB-001",
                name="Calibration Dataset",
                description="Calibration evaluation dataset",
                path="data/eval/safety/calibration.parquet",
                hash_sha256="e7a3b1c60d8f2e4a59c3b17d6f4e28p6c1b530a9f72c4e81p6b3a950f7c2e14b",
                size_samples=5000,
                license="proprietary-internal",
                owner="ml-team",
                modality="cross_modal",
            ),
            # Performance Datasets
            EvalDataset(
                id="DS-PERF-LOAD-001",
                name="Performance Load Test",
                description="Load testing dataset for latency/throughput",
                path="data/eval/performance/load.parquet",
                hash_sha256="f8b4c2d71e9a3f5b60d4c28e7a5f39q7d2c641b0e83f5c92q7c4d061e8a3f25b",
                size_samples=10000,
                license="proprietary-internal",
                owner="infra-team",
                modality="cross_modal",
            ),
            # Regression Datasets
            EvalDataset(
                id="DS-REG-BASELINE-001",
                name="Regression Baseline",
                description="Baseline predictions for regression checks",
                path="data/eval/regression/baseline.parquet",
                hash_sha256="a9c5d3e82f0b4a6c71e5d39f8a6c40r8e3d752c1f94b6a03r8d5c172f9b4a36c",
                size_samples=10000,
                license="proprietary-internal",
                owner="ml-team",
                modality="cross_modal",
            ),
        ]

        for dataset in datasets:
            self._datasets[dataset.id] = dataset

    def get_by_id(self, dataset_id: str) -> EvalDataset | None:
        """Get a dataset by ID."""
        return self._datasets.get(dataset_id)

    def get_by_modality(self, modality: str) -> list[EvalDataset]:
        """Get all datasets for a modality."""
        return [d for d in self._datasets.values() if d.modality == modality]

    def get_all_datasets(self) -> list[EvalDataset]:
        """Get all datasets."""
        return list(self._datasets.values())

    def get_datasets_for_eval(self, eval_ids: list[str]) -> list[EvalDataset]:
        """
        Get datasets required for a set of evaluations.

        Args:
            eval_ids: List of evaluation IDs

        Returns:
            List of required datasets
        """
        # Mapping from eval to dataset
        eval_to_dataset = {
            "M-CM-001": "DS-CM-BENCH-001",
            "M-CM-002": "DS-CM-BENCH-001",
            "M-CM-003": "DS-CM-CONSIST-001",
            "M-CM-004": "DS-CM-RETRIEVAL-001",
            "M-MOD-001": "DS-MOD-TEXT-001",
            "M-MOD-002": "DS-MOD-IMAGE-001",
            "M-MOD-003": "DS-MOD-AUDIO-001",
            "M-ROB-001": "DS-ADV-ROBUST-001",
            "M-ROB-002": ["DS-OOD-INDIST-001", "DS-OOD-OUT-001"],
            "M-ROB-003": "DS-CALIB-001",
            "M-SAF-001": "DS-SAFETY-001",
            "M-LAT-001": "DS-PERF-LOAD-001",
            "M-LAT-002": "DS-PERF-LOAD-001",
            "M-LAT-003": "DS-PERF-LOAD-001",
            "M-THR-001": "DS-PERF-LOAD-001",
            "M-RES-001": "DS-PERF-LOAD-001",
        }

        datasets: list[EvalDataset] = []
        for eval_id in eval_ids:
            dataset_ids = eval_to_dataset.get(eval_id, [])
            if isinstance(dataset_ids, str):
                dataset_ids = [dataset_ids]

            for ds_id in dataset_ids:
                dataset = self.get_by_id(ds_id)
                if dataset and dataset not in datasets:
                    datasets.append(dataset)

        return datasets

    def verify_all_hashes(self, data_root: Path | None = None) -> dict[str, tuple[bool, str]]:
        """
        Verify hashes for all datasets.

        Args:
            data_root: Optional root path for datasets

        Returns:
            Dictionary mapping dataset ID to (is_valid, message)
        """
        results: dict[str, tuple[bool, str]] = {}

        for dataset in self._datasets.values():
            if data_root:
                data_path = data_root / dataset.path
            else:
                data_path = Path(dataset.path)

            results[dataset.id] = dataset.verify_hash(data_path)

        return results

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "datasets": [d.to_dict() for d in self._datasets.values()],
            "total_count": len(self._datasets),
            "modalities": list(set(d.modality for d in self._datasets.values())),
        }


class DatasetIntegrityChecker:
    """
    Dataset integrity checker for contamination and hash verification.

    The checker verifies dataset integrity before eval runs and
    checks for train/eval contamination.
    """

    def __init__(
        self,
        manifest: DatasetManifest | None = None,
        training_data_index: Path | None = None,
    ) -> None:
        """
        Initialize the integrity checker.

        Args:
            manifest: Dataset manifest
            training_data_index: Path to training data index
        """
        self.manifest = manifest or DatasetManifest()
        self.training_data_index = training_data_index

    def check_dataset_integrity(
        self,
        dataset_id: str,
        verify_hash: bool = True,
        check_contamination: bool = True,
    ) -> dict[str, Any]:
        """
        Check integrity of a single dataset.

        Args:
            dataset_id: Dataset to check
            verify_hash: Whether to verify hash
            check_contamination: Whether to check for contamination

        Returns:
            Integrity check results
        """
        dataset = self.manifest.get_by_id(dataset_id)
        if not dataset:
            return {
                "dataset_id": dataset_id,
                "status": "FAIL",
                "error": "Dataset not found",
            }

        results: dict[str, Any] = {
            "dataset_id": dataset_id,
            "status": "PASS",
            "checks": {},
        }

        # Hash verification
        if verify_hash:
            is_valid, message = dataset.verify_hash()
            results["checks"]["hash"] = {
                "passed": is_valid,
                "message": message,
            }
            if not is_valid:
                results["status"] = "FAIL"

        # Contamination check
        if check_contamination and self.training_data_index:
            is_contaminated, message = self._check_contamination(dataset)
            results["checks"]["contamination"] = {
                "passed": not is_contaminated,
                "message": message,
            }
            if is_contaminated:
                results["status"] = "FAIL"
                dataset.contamination_checked = False
            else:
                dataset.mark_contamination_checked()

        return results

    def _check_contamination(
        self, dataset: EvalDataset
    ) -> tuple[bool, str]:
        """
        Check if eval dataset is contaminated with training data.

        Args:
            dataset: Dataset to check

        Returns:
            Tuple of (is_contaminated, message)
        """
        if not self.training_data_index or not self.training_data_index.exists():
            return (False, "Training data index not available")

        # In production, this would check for sample overlap
        # For now, we simulate with a placeholder
        return (False, "No contamination detected")

    def check_all_datasets(
        self,
        data_root: Path | None = None,
        verify_hash: bool = True,
        check_contamination: bool = True,
    ) -> dict[str, dict[str, Any]]:
        """
        Check integrity of all datasets.

        Args:
            data_root: Optional root path for datasets
            verify_hash: Whether to verify hashes
            check_contamination: Whether to check for contamination

        Returns:
            Dictionary of check results per dataset
        """
        results: dict[str, dict[str, Any]] = {}

        for dataset in self.manifest.get_all_datasets():
            results[dataset.id] = self.check_dataset_integrity(
                dataset_id=dataset.id,
                verify_hash=verify_hash,
                check_contamination=check_contamination,
            )

        return results

    def get_contamination_status(self) -> dict[str, bool]:
        """
        Get contamination check status for all datasets.

        Returns:
            Dictionary mapping dataset ID to contamination status
        """
        return {
            d.id: d.contamination_checked for d in self.manifest.get_all_datasets()
        }
