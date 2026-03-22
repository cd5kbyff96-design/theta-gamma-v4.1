"""
Theta-Gamma Pipeline — Main orchestrator for autonomous ML training.

This module provides the central pipeline orchestrator that wires together
all Theta-Gamma components into a cohesive autonomous system.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from theta_gamma.autonomy.contract import AutonomyContract
from theta_gamma.autonomy.risk_profile import RiskAppetiteProfile
from theta_gamma.autonomy.failure_modes import FailureModeRegistry
from theta_gamma.autonomy.limits import OperatingLimits
from theta_gamma.compute.budget import ComputeBudget, BudgetPolicy
from theta_gamma.compute.tiers import TierManager
from theta_gamma.compute.downgrade import DowngradeCascade
from theta_gamma.compute.dashboard import RunwayDashboard
from theta_gamma.evaluation.metrics import MetricDictionary
from theta_gamma.evaluation.gates import GateEvaluator, GateStatus
from theta_gamma.evaluation.harness import EvalHarness, EvalMode, EvalResult
from theta_gamma.recovery.state_machine import RecoveryStateMachine, IncidentState, IncidentSeverity
from theta_gamma.compiler.packets import TaskPacket, PacketDomain, PacketPriority, PacketStatus
from theta_gamma.compiler.compiler import PacketCompiler
from theta_gamma.weekly_loop.runbook import WeeklyControlLoop, WeeklyReport, GoNoGoDecision
from theta_gamma.weekly_loop.prioritization import AutoPrioritization
from theta_gamma.decisions.packets import DecisionPacket, Decision, DecisionPacketGenerator, DecisionImpact, DecisionUrgency


class PipelineState(str, Enum):
    """
    Pipeline execution state.

    States track the overall pipeline lifecycle.
    """

    INITIALIZING = "initializing"
    IDLE = "idle"
    RUNNING = "running"
    WEEKLY_LOOP = "weekly_loop"
    PAUSED = "paused"
    ESCALATED = "escalated"
    STOPPED = "stopped"


@dataclass
class PipelineMetrics:
    """
    Pipeline execution metrics.

    Attributes:
        current_gate: Current gate being evaluated
        packets_completed: Number of packets completed
        packets_pending: Number of packets pending
        monthly_spend: Monthly spend in USD
        daily_spend: Daily spend in USD
        incidents_active: Number of active incidents
        incidents_s1: Number of S1 incidents
        consecutive_gate_failures: Consecutive gate failures
        last_weekly_loop: Last weekly loop timestamp
    """

    current_gate: str = "G1"
    packets_completed: int = 0
    packets_pending: int = 0
    monthly_spend: float = 0.0
    daily_spend: float = 0.0
    incidents_active: int = 0
    incidents_s1: int = 0
    consecutive_gate_failures: int = 0
    last_weekly_loop: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "current_gate": self.current_gate,
            "packets_completed": self.packets_completed,
            "packets_pending": self.packets_pending,
            "monthly_spend_usd": self.monthly_spend,
            "daily_spend_usd": self.daily_spend,
            "incidents_active": self.incidents_active,
            "incidents_s1": self.incidents_s1,
            "consecutive_gate_failures": self.consecutive_gate_failures,
            "last_weekly_loop": self.last_weekly_loop.isoformat() if self.last_weekly_loop else None,
        }


@dataclass
class PipelineConfig:
    """
    Pipeline configuration.

    Attributes:
        project_root: Project root directory
        artifacts_dir: Directory for planning artifacts
        results_dir: Directory for results
        data_dir: Directory for datasets
        log_dir: Directory for logs
        weekly_loop_day: Day of week for weekly loop (0=Monday)
        weekly_loop_hour: Hour of day for weekly loop (UTC)
        max_parallel_packets: Maximum parallel packets
        enable_auto_downgrade: Enable auto-downgrade
        enable_kill_switches: Enable kill-switches
    """

    project_root: Path = field(default_factory=Path.cwd)
    artifacts_dir: Path = field(default_factory=lambda: Path("artifacts"))
    results_dir: Path = field(default_factory=lambda: Path("results"))
    data_dir: Path = field(default_factory=lambda: Path("data"))
    log_dir: Path = field(default_factory=lambda: Path("logs"))
    weekly_loop_day: int = 0  # Monday
    weekly_loop_hour: int = 9  # 09:00 UTC
    max_parallel_packets: int = 3
    enable_auto_downgrade: bool = True
    enable_kill_switches: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PipelineConfig":
        """Create config from dictionary."""
        return cls(
            project_root=Path(data.get("project_root", ".")),
            artifacts_dir=Path(data.get("artifacts_dir", "artifacts")),
            results_dir=Path(data.get("results_dir", "results")),
            data_dir=Path(data.get("data_dir", "data")),
            log_dir=Path(data.get("log_dir", "logs")),
            weekly_loop_day=data.get("weekly_loop_day", 0),
            weekly_loop_hour=data.get("weekly_loop_hour", 9),
            max_parallel_packets=data.get("max_parallel_packets", 3),
            enable_auto_downgrade=data.get("enable_auto_downgrade", True),
            enable_kill_switches=data.get("enable_kill_switches", True),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "project_root": str(self.project_root),
            "artifacts_dir": str(self.artifacts_dir),
            "results_dir": str(self.results_dir),
            "data_dir": str(self.data_dir),
            "log_dir": str(self.log_dir),
            "weekly_loop_day": self.weekly_loop_day,
            "weekly_loop_hour": self.weekly_loop_hour,
            "max_parallel_packets": self.max_parallel_packets,
            "enable_auto_downgrade": self.enable_auto_downgrade,
            "enable_kill_switches": self.enable_kill_switches,
        }


class ThetaGammaPipeline:
    """
    Main Theta-Gamma pipeline orchestrator.

    This class wires together all pipeline components:
    - Autonomy contract for decision authority
    - Compute budget for cost tracking
    - Evaluation harness for metric collection
    - Gate evaluator for milestone progression
    - Recovery state machine for failure handling
    - Packet compiler for task execution
    - Weekly control loop for autonomous operation

    Example:
        >>> pipeline = ThetaGammaPipeline()
        >>> await pipeline.initialize()
        >>> await pipeline.run_weekly_loop()
        >>> metrics = pipeline.get_metrics()
    """

    def __init__(self, config: PipelineConfig | None = None) -> None:
        """
        Initialize the pipeline.

        Args:
            config: Pipeline configuration
        """
        self._config = config or PipelineConfig()
        self._state = PipelineState.INITIALIZING
        self._started_at: datetime | None = None

        # Core components (initialized in _initialize_components)
        self._autonomy_contract: AutonomyContract | None = None
        self._risk_profile: RiskAppetiteProfile | None = None
        self._operating_limits: OperatingLimits | None = None
        self._failure_mode_registry: FailureModeRegistry | None = None

        self._budget: ComputeBudget | None = None
        self._budget_policy: BudgetPolicy | None = None
        self._tier_manager: TierManager | None = None
        self._downgrade_cascade: DowngradeCascade | None = None
        self._dashboard: RunwayDashboard | None = None

        self._metric_dictionary: MetricDictionary | None = None
        self._gate_evaluator: GateEvaluator | None = None
        self._eval_harness: EvalHarness | None = None

        self._recovery_state_machine: RecoveryStateMachine | None = None

        self._packet_compiler: PacketCompiler | None = None
        self._packets: list[TaskPacket] = []
        self._completed_packets: set[str] = set()

        self._weekly_loop: WeeklyControlLoop | None = None
        self._auto_prioritization: AutoPrioritization | None = None
        self._decision_packet_generator: DecisionPacketGenerator | None = None

        # State tracking
        self._current_gate: str = "G1"
        self._consecutive_gate_failures: dict[str, int] = {}
        self._last_report: WeeklyReport | None = None

    async def initialize(self) -> None:
        """
        Initialize all pipeline components.

        This loads configurations, initializes components, and
        compiles task packets from planning artifacts.
        """
        self._started_at = datetime.now()

        # Initialize components
        self._initialize_components()

        # Compile packets from artifacts
        await self._compile_packets()

        self._state = PipelineState.IDLE

    def _initialize_components(self) -> None:
        """Initialize all pipeline components."""
        # Autonomy components
        self._autonomy_contract = AutonomyContract.load_default()
        self._risk_profile = RiskAppetiteProfile.load_default()
        self._operating_limits = OperatingLimits()
        self._failure_mode_registry = FailureModeRegistry()

        # Compute components
        self._budget_policy = BudgetPolicy()
        self._budget = ComputeBudget(policy=self._budget_policy)
        self._tier_manager = TierManager()
        self._downgrade_cascade = DowngradeCascade(tier_manager=self._tier_manager)
        self._dashboard = RunwayDashboard(
            monthly_cap_usd=self._budget_policy.monthly_cap_usd,
            daily_cap_usd=self._budget_policy.daily_cap_usd,
        )

        # Evaluation components
        self._metric_dictionary = MetricDictionary.load_default()
        self._gate_evaluator = GateEvaluator(metric_dictionary=self._metric_dictionary)
        self._eval_harness = EvalHarness(metric_dictionary=self._metric_dictionary)

        # Recovery components
        self._recovery_state_machine = RecoveryStateMachine()

        # Compiler and packets
        self._packet_compiler = PacketCompiler()

        # Weekly loop components
        self._weekly_loop = WeeklyControlLoop()
        self._auto_prioritization = AutoPrioritization()
        self._decision_packet_generator = DecisionPacketGenerator()

    async def _compile_packets(self) -> None:
        """Compile task packets from planning artifacts."""
        if self._packet_compiler:
            self._packets = self._packet_compiler.compile_artifacts(self._config.artifacts_dir)
            self._packets_pending = len(self._packets)

    def _update_metrics_from_components(self) -> PipelineMetrics:
        """Update pipeline metrics from all components."""
        incidents_active = 0
        incidents_s1 = 0

        if self._recovery_state_machine:
            summary = self._recovery_state_machine.get_incident_summary()
            incidents_active = summary.get("active_incidents", 0)
            incidents_s1 = summary.get("s1_incidents", 0)

        monthly_spend = 0.0
        daily_spend = 0.0

        if self._budget:
            # Access private attributes - in production, would add public getters
            monthly_spend = self._budget._monthly_spend
            daily_spend = self._budget._daily_spend

        return PipelineMetrics(
            current_gate=self._current_gate,
            packets_completed=len(self._completed_packets),
            packets_pending=len([p for p in self._packets if p.status == PacketStatus.PENDING]),
            monthly_spend=monthly_spend,
            daily_spend=daily_spend,
            incidents_active=incidents_active,
            incidents_s1=incidents_s1,
            consecutive_gate_failures=self._consecutive_gate_failures.get(self._current_gate, 0),
            last_weekly_loop=self._last_report.generated_at if self._last_report else None,
        )

    async def run_weekly_loop(self) -> WeeklyReport:
        """
        Run the weekly control loop.

        This executes all 7 steps of the weekly loop:
        1. Collect metrics
        2. Evaluate gates
        3. Prioritize backlog
        4. Decide go/no-go
        5. Plan next 7 days
        6. Generate report
        7. Begin execution

        Returns:
            WeeklyReport with loop outcomes
        """
        if self._state == PipelineState.STOPPED:
            raise RuntimeError("Pipeline is stopped")

        self._state = PipelineState.WEEKLY_LOOP

        if not self._weekly_loop:
            raise RuntimeError("Weekly loop not initialized")

        # Run the weekly loop
        report = await self._weekly_loop.run_weekly_loop()
        self._last_report = report

        # Update gate status from report
        for gate_id, status in report.gate_status.items():
            if status == "failed":
                self._consecutive_gate_failures[gate_id] = (
                    self._consecutive_gate_failures.get(gate_id, 0) + 1
                )
            else:
                self._consecutive_gate_failures[gate_id] = 0

        # Generate decision packet if needed
        await self._generate_decision_packet(report)

        # Handle go/no-go decision
        if report.go_no_go_decision == GoNoGoDecision.NO_GO:
            self._state = PipelineState.ESCALATED
            self._escalate_blockers(report.blockers)
        else:
            self._state = PipelineState.RUNNING

        return report

    async def _generate_decision_packet(self, report: WeeklyReport) -> None:
        """Generate weekly decision packet from report."""
        if not self._decision_packet_generator:
            return

        # Collect decisions requiring human input
        decisions = self._extract_decisions_from_report(report)

        for decision in decisions:
            self._decision_packet_generator.add_pending_decision(decision)

        # Generate packet with top 5 decisions
        week = self._weekly_loop._get_current_week() if self._weekly_loop else "unknown"
        packet = self._decision_packet_generator.generate_packet(week)

        # Log packet generation
        self._log_decision_packet(packet)

    def _extract_decisions_from_report(self, report: WeeklyReport) -> list[Decision]:
        """Extract decisions requiring human input from report."""
        decisions = []

        # Check for gate progression decisions
        for gate_id, status in report.gate_status.items():
            if status == "passed":
                decisions.append(
                    Decision(
                        decision_id=f"gate-{gate_id}-progression",
                        title=f"Approve progression past {gate_id}",
                        impact=DecisionImpact.HIGH,
                        urgency=DecisionUrgency.THIS_WEEK,
                        context=f"Gate {gate_id} has passed. Approve progression to next phase?",
                        options=[
                            DecisionOption("A", "Approve progression"),
                            DecisionOption("B", "Request additional validation"),
                            DecisionOption("C", "Hold at current gate"),
                        ],
                        recommended_default=DecisionOption("A", "Approve progression", is_recommended=True),
                        deadline=datetime.now(),
                    )
                )

        # Check for budget amendment decisions
        if report.budget_status.get("monthly_spend_pct", 0) > 0.8:
            decisions.append(
                Decision(
                    decision_id="budget-amendment",
                    title="Budget amendment required",
                    impact=DecisionImpact.CRITICAL,
                    urgency=DecisionUrgency.IMMEDIATE,
                    context=f"Monthly spend at {report.budget_status.get('monthly_spend_pct', 0):.0%}. Approve continued operation?",
                    options=[
                        DecisionOption("A", "Approve continued operation"),
                        DecisionOption("B", "Approve with reduced scope"),
                        DecisionOption("C", "Halt until next budget cycle"),
                    ],
                    recommended_default=DecisionOption("B", "Approve with reduced scope", is_recommended=True),
                    deadline=datetime.now(),
                )
            )

        # Check for blocker decisions
        for blocker in report.blockers:
            decisions.append(
                Decision(
                    decision_id=f"blocker-{hash(blocker) % 10000}",
                    title="Resolve blocker",
                    impact=DecisionImpact.HIGH,
                    urgency=DecisionUrgency.THIS_WEEK,
                    context=blocker,
                    options=[
                        DecisionOption("A", "Allocate resources to resolve"),
                        DecisionOption("B", "Deprioritize and work around"),
                        DecisionOption("C", "Escalate to architect"),
                    ],
                    recommended_default=DecisionOption("A", "Allocate resources to resolve", is_recommended=True),
                    deadline=datetime.now(),
                )
            )

        return decisions

    def _log_decision_packet(self, packet: DecisionPacket) -> None:
        """Log decision packet generation."""
        # In production, this would write to decision log
        pass

    def _escalate_blockers(self, blockers: list[str]) -> None:
        """Escalate blockers to human stakeholders."""
        # In production, this would send notifications
        pass

    async def execute_packet(self, packet_id: str) -> bool:
        """
        Execute a single task packet.

        Args:
            packet_id: Packet to execute

        Returns:
            True if packet completed successfully
        """
        packet = self._get_packet(packet_id)
        if not packet:
            return False

        # Check dependencies
        if not packet.is_executable(self._completed_packets):
            return False

        # Check budget
        if self._budget and not self._budget.can_spend(packet.estimated_cost_usd):
            return False

        # Execute packet commands (simulated)
        success = await self._execute_packet_commands(packet)

        if success:
            self._completed_packets.add(packet_id)
            if self._budget:
                self._budget.record_cost(packet.estimated_cost_usd, "packet_execution")

        return success

    async def _execute_packet_commands(self, packet: TaskPacket) -> bool:
        """Execute packet commands."""
        # In production, this would execute actual commands
        # For now, simulate success
        return True

    def _get_packet(self, packet_id: str) -> TaskPacket | None:
        """Get packet by ID."""
        for packet in self._packets:
            if packet.packet_id == packet_id:
                return packet
        return None

    async def run_training_run(
        self,
        checkpoint_id: str,
        eval_mode: EvalMode = EvalMode.FULL,
    ) -> dict[str, Any]:
        """
        Run a training run with evaluation.

        Args:
            checkpoint_id: Checkpoint to evaluate
            eval_mode: Evaluation mode

        Returns:
            Training run results
        """
        if not self._eval_harness or not self._gate_evaluator:
            raise RuntimeError("Eval components not initialized")

        # Run evaluation
        results = await self._eval_harness.run_eval(
            mode=eval_mode,
            checkpoint_id=checkpoint_id,
        )

        # Collect metrics
        metrics = {}
        for result in results:
            metrics.update(result.metrics)

        # Evaluate current gate
        gate_result = self._gate_evaluator.evaluate_gate(self._current_gate, metrics)

        return {
            "checkpoint_id": checkpoint_id,
            "metrics": metrics,
            "gate_result": gate_result.to_dict(),
            "eval_results": [r.to_dict() for r in results],
        }

    def get_metrics(self) -> PipelineMetrics:
        """Get current pipeline metrics."""
        return self._update_metrics_from_components()

    def get_status(self) -> dict[str, Any]:
        """Get pipeline status."""
        metrics = self.get_metrics()
        return {
            "state": self._state.value,
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "metrics": metrics.to_dict(),
            "current_gate": self._current_gate,
            "packets": {
                "total": len(self._packets),
                "completed": len(self._completed_packets),
                "pending": len([p for p in self._packets if p.status == PacketStatus.PENDING]),
            },
        }

    def pause(self) -> None:
        """Pause the pipeline."""
        self._state = PipelineState.PAUSED

    def resume(self) -> None:
        """Resume the pipeline."""
        if self._state != PipelineState.STOPPED:
            self._state = PipelineState.RUNNING

    def stop(self) -> None:
        """Stop the pipeline."""
        self._state = PipelineState.STOPPED

    def get_packets(self, status: PacketStatus | None = None) -> list[TaskPacket]:
        """Get task packets, optionally filtered by status."""
        if status:
            return [p for p in self._packets if p.status == status]
        return self._packets.copy()

    def get_completed_packets(self) -> set[str]:
        """Get set of completed packet IDs."""
        return self._completed_packets.copy()

    def get_current_gate(self) -> str:
        """Get current gate."""
        return self._current_gate

    def set_current_gate(self, gate_id: str) -> None:
        """Set current gate."""
        self._current_gate = gate_id

    def to_dict(self) -> dict[str, Any]:
        """Convert pipeline state to dictionary for serialization."""
        return {
            "config": self._config.to_dict(),
            "state": self._state.value,
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "current_gate": self._current_gate,
            "consecutive_gate_failures": self._consecutive_gate_failures,
            "packets": [p.to_dict() for p in self._packets],
            "completed_packets": list(self._completed_packets),
            "last_report": self._last_report.to_dict() if self._last_report else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ThetaGammaPipeline":
        """Create pipeline from dictionary state."""
        config = PipelineConfig.from_dict(data.get("config", {}))
        pipeline = cls(config)
        pipeline._state = PipelineState(data.get("state", "initializing"))
        pipeline._current_gate = data.get("current_gate", "G1")
        pipeline._consecutive_gate_failures = data.get("consecutive_gate_failures", {})
        # Note: Components would need to be re-initialized
        return pipeline
