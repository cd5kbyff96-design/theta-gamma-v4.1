"""
Tests for Theta-Gamma pipeline orchestrator.
"""

import asyncio
import pytest
from datetime import datetime
from pathlib import Path

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
)
from theta_gamma.compiler.packets import PacketStatus


class TestPipelineConfig:
    """Test PipelineConfig."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = PipelineConfig()

        assert config.project_root == Path.cwd()
        assert config.artifacts_dir == Path("artifacts")
        assert config.results_dir == Path("results")
        assert config.max_parallel_packets == 3
        assert config.enable_auto_downgrade is True
        assert config.enable_kill_switches is True

    def test_config_from_dict(self) -> None:
        """Test creating config from dictionary."""
        data = {
            "project_root": "/custom/path",
            "artifacts_dir": "/custom/artifacts",
            "max_parallel_packets": 5,
            "enable_auto_downgrade": False,
        }
        config = PipelineConfig.from_dict(data)

        assert config.project_root == Path("/custom/path")
        assert config.artifacts_dir == Path("/custom/artifacts")
        assert config.max_parallel_packets == 5
        assert config.enable_auto_downgrade is False

    def test_config_to_dict(self) -> None:
        """Test converting config to dictionary."""
        config = PipelineConfig(
            project_root=Path("/test"),
            max_parallel_packets=10,
        )
        data = config.to_dict()

        assert data["project_root"] == "/test"
        assert data["max_parallel_packets"] == 10


class TestPipelineMetrics:
    """Test PipelineMetrics."""

    def test_default_metrics(self) -> None:
        """Test default metrics."""
        metrics = PipelineMetrics()

        assert metrics.current_gate == "G1"
        assert metrics.packets_completed == 0
        assert metrics.packets_pending == 0
        assert metrics.monthly_spend == 0.0
        assert metrics.consecutive_gate_failures == 0

    def test_metrics_to_dict(self) -> None:
        """Test converting metrics to dictionary."""
        metrics = PipelineMetrics(
            current_gate="G2",
            packets_completed=5,
            packets_pending=3,
            monthly_spend=250.0,
            daily_spend=35.0,
        )
        data = metrics.to_dict()

        assert data["current_gate"] == "G2"
        assert data["packets_completed"] == 5
        assert data["monthly_spend_usd"] == 250.0


class TestThetaGammaPipeline:
    """Test ThetaGammaPipeline orchestrator."""

    def test_pipeline_initialization(self) -> None:
        """Test pipeline initialization."""
        pipeline = ThetaGammaPipeline()

        assert pipeline._state == PipelineState.INITIALIZING
        assert pipeline._current_gate == "G1"

    @pytest.mark.asyncio
    async def test_pipeline_initialize(self) -> None:
        """Test async pipeline initialization."""
        pipeline = ThetaGammaPipeline()

        await pipeline.initialize()

        assert pipeline._state == PipelineState.IDLE
        assert pipeline._autonomy_contract is not None
        assert pipeline._budget is not None
        assert pipeline._gate_evaluator is not None
        assert pipeline._weekly_loop is not None

    def test_pipeline_get_status(self) -> None:
        """Test getting pipeline status."""
        pipeline = ThetaGammaPipeline()

        status = pipeline.get_status()

        assert "state" in status
        assert "metrics" in status
        assert "packets" in status

    def test_pipeline_pause_resume(self) -> None:
        """Test pause and resume."""
        pipeline = ThetaGammaPipeline()

        pipeline.pause()
        assert pipeline._state == PipelineState.PAUSED

        pipeline.resume()
        assert pipeline._state == PipelineState.RUNNING

    def test_pipeline_stop(self) -> None:
        """Test stopping pipeline."""
        pipeline = ThetaGammaPipeline()

        pipeline.stop()
        assert pipeline._state == PipelineState.STOPPED

    @pytest.mark.asyncio
    async def test_get_metrics(self) -> None:
        """Test getting pipeline metrics."""
        pipeline = ThetaGammaPipeline()
        await pipeline.initialize()

        metrics = pipeline.get_metrics()

        assert isinstance(metrics, PipelineMetrics)
        assert metrics.current_gate == "G1"

    @pytest.mark.asyncio
    async def test_get_packets(self) -> None:
        """Test getting packets."""
        pipeline = ThetaGammaPipeline()
        await pipeline.initialize()

        packets = pipeline.get_packets()

        # Should have default packets from compiler
        assert len(packets) > 0

    def test_set_current_gate(self) -> None:
        """Test setting current gate."""
        pipeline = ThetaGammaPipeline()

        pipeline.set_current_gate("G2")
        assert pipeline.get_current_gate() == "G2"


class TestConfigLoader:
    """Test ConfigLoader."""

    def test_loader_initialization(self) -> None:
        """Test loader initialization."""
        loader = ConfigLoader()

        assert loader._config_path is None

    def test_loader_with_path(self, tmp_path: Path) -> None:
        """Test loader with config path."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
compute:
  monthly_cap_usd: 600.0
  daily_cap_usd: 60.0
""")

        loader = ConfigLoader(config_file)

        # File config is loaded
        assert loader._file_config.get("compute", {}).get("monthly_cap_usd") == 600.0

    def test_load_compute_config(self) -> None:
        """Test loading compute config."""
        loader = ConfigLoader()
        config = loader.load_compute_config()

        assert config.monthly_cap_usd == 500.0
        assert config.daily_cap_usd == 50.0

    def test_load_all_configs(self) -> None:
        """Test loading all configurations."""
        loader = ConfigLoader()
        configs = loader.load_all()

        assert "autonomy" in configs
        assert "compute" in configs
        assert "evaluation" in configs
        assert "recovery" in configs
        assert "compiler" in configs
        assert "weekly_loop" in configs
        assert "decisions" in configs


class TestPipelineIntegration:
    """Integration tests for pipeline components."""

    @pytest.mark.asyncio
    async def test_full_initialization(self) -> None:
        """Test full pipeline initialization."""
        config = PipelineConfig(
            artifacts_dir=Path("artifacts"),
            max_parallel_packets=3,
        )
        pipeline = ThetaGammaPipeline(config)

        await pipeline.initialize()

        # Verify all components initialized
        assert pipeline._autonomy_contract is not None
        assert pipeline._risk_profile is not None
        assert pipeline._operating_limits is not None
        assert pipeline._budget is not None
        assert pipeline._tier_manager is not None
        assert pipeline._metric_dictionary is not None
        assert pipeline._gate_evaluator is not None
        assert pipeline._eval_harness is not None
        assert pipeline._recovery_state_machine is not None
        assert pipeline._packet_compiler is not None
        assert pipeline._weekly_loop is not None

        # Verify state
        assert pipeline._state == PipelineState.IDLE

    @pytest.mark.asyncio
    async def test_packet_compilation(self) -> None:
        """Test packet compilation during initialization."""
        pipeline = ThetaGammaPipeline()
        await pipeline.initialize()

        packets = pipeline.get_packets()

        # Should have packets from all domains
        assert len(packets) > 0

        # Check for expected packets
        packet_ids = [p.packet_id for p in packets]
        assert any("INFRA" in pid for pid in packet_ids)
        assert any("DATA" in pid for pid in packet_ids)
        assert any("TRAIN" in pid for pid in packet_ids)
        assert any("EVAL" in pid for pid in packet_ids)

    @pytest.mark.asyncio
    async def test_metrics_from_components(self) -> None:
        """Test metrics aggregation from components."""
        pipeline = ThetaGammaPipeline()
        await pipeline.initialize()

        metrics = pipeline.get_metrics()

        # Should aggregate from all components
        assert metrics.packets_pending > 0
        assert metrics.current_gate == "G1"

    def test_pipeline_serialization(self) -> None:
        """Test pipeline serialization."""
        pipeline = ThetaGammaPipeline()
        pipeline.set_current_gate("G2")

        data = pipeline.to_dict()

        assert data["current_gate"] == "G2"
        assert data["state"] == "initializing"

    def test_pipeline_deserialization(self) -> None:
        """Test pipeline deserialization."""
        data = {
            "state": "running",
            "current_gate": "G3",
            "consecutive_gate_failures": {"G1": 0, "G2": 1},
        }

        pipeline = ThetaGammaPipeline.from_dict(data)

        assert pipeline.get_current_gate() == "G3"
        assert pipeline._consecutive_gate_failures["G2"] == 1
