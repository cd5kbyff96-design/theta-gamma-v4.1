"""
Weekly Control Loop Runbook — Enhanced with go/no-go decision logic.

This module implements the weekly control loop that runs every Monday
to collect metrics, evaluate progress, and generate execution plans.

Enhanced with full go/no-go decision matrix from A6 specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from theta_gamma.compiler.packets import TaskPacket, PacketStatus


class LoopStep(str, Enum):
    """
    Weekly loop steps.

    Steps execute in order: COLLECT -> EVALUATE -> PRIORITIZE -> DECIDE -> PLAN -> REPORT -> EXECUTE
    """

    COLLECT = "collect"
    EVALUATE = "evaluate"
    PRIORITIZE = "prioritize"
    DECIDE = "decide"
    PLAN = "plan"
    REPORT = "report"
    EXECUTE = "execute"


class GoNoGoDecision(str, Enum):
    """
    Go/No-Go decision outcomes.

    Determines whether the week proceeds as planned.
    """

    GO = "go"
    GO_WITH_WATCH = "go_with_watch"
    CONDITIONAL_GO = "conditional_go"
    NO_GO = "no_go"


@dataclass
class GoNoGoResult:
    """
    Go/No-Go decision result.

    Attributes:
        decision: The decision outcome
        triggers: List of triggers that fired
        watch_items: Items to watch if GO_WITH_WATCH
        required_actions: Actions required before proceeding
        blockers: Blockers if NO_GO
    """

    decision: GoNoGoDecision
    triggers: list[str] = field(default_factory=list)
    watch_items: list[str] = field(default_factory=list)
    required_actions: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "decision": self.decision.value,
            "triggers": self.triggers,
            "watch_items": self.watch_items,
            "required_actions": self.required_actions,
            "blockers": self.blockers,
        }


@dataclass
class WeeklyReport:
    """
    Weekly loop report.

    Attributes:
        week: Week identifier
        generated_at: Report generation timestamp
        go_no_go_decision: Go/No-Go decision
        metrics_summary: Summary of collected metrics
        gate_status: Status of all gates
        budget_status: Budget status
        top_packets: Top prioritized packets
        watch_items: Items to watch
        blockers: Current blockers
        next_7_days_plan: Plan for next 7 days
    """

    week: str
    generated_at: datetime
    go_no_go_decision: GoNoGoDecision
    metrics_summary: dict[str, Any] = field(default_factory=dict)
    gate_status: dict[str, str] = field(default_factory=dict)
    budget_status: dict[str, Any] = field(default_factory=dict)
    top_packets: list[dict[str, Any]] = field(default_factory=list)
    watch_items: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    next_7_days_plan: dict[str, Any] = field(default_factory=dict)
    go_no_go_result: GoNoGoResult | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "week": self.week,
            "generated_at": self.generated_at.isoformat(),
            "go_no_go_decision": self.go_no_go_decision.value,
            "metrics_summary": self.metrics_summary,
            "gate_status": self.gate_status,
            "budget_status": self.budget_status,
            "top_packets": self.top_packets,
            "watch_items": self.watch_items,
            "blockers": self.blockers,
            "next_7_days_plan": self.next_7_days_plan,
            "go_no_go_result": self.go_no_go_result.to_dict() if self.go_no_go_result else None,
        }


class WeeklyControlLoop:
    """
    Weekly control loop orchestrator.

    Runs the weekly control loop sequence:
    1. Collect metrics
    2. Evaluate progress
    3. Prioritize backlog
    4. Decide go/no-go
    5. Plan next 7 days
    6. Generate report
    7. Execute plan

    Example:
        >>> loop = WeeklyControlLoop()
        >>> report = await loop.run_weekly_loop()
        >>> print(f"Decision: {report.go_no_go_decision}")
    """

    def __init__(self) -> None:
        """Initialize the weekly control loop."""
        self._current_week: str = ""
        self._loop_started_at: datetime | None = None
        self._loop_completed_at: datetime | None = None
        self._reports: list[WeeklyReport] = []

        # State for go/no-go evaluation
        self._incidents: list[dict[str, Any]] = []
        self._packets: list[TaskPacket] = []
        self._completed_packets: set[str] = set()
        self._gate_failures: dict[str, int] = {}
        self._kill_switches_tripped: list[str] = []
        self._metric_trends: dict[str, list[float]] = {}

    def _get_current_week(self) -> str:
        """Get current week identifier."""
        now = datetime.now()
        return f"{now.year}-W{now.isocalendar()[1]:02d}"

    def set_state(
        self,
        incidents: list[dict[str, Any]],
        packets: list[TaskPacket],
        completed_packets: set[str],
        gate_failures: dict[str, int],
        kill_switches: list[str],
        metric_trends: dict[str, list[float]],
    ) -> None:
        """
        Set state for go/no-go evaluation.

        Args:
            incidents: List of active incidents
            packets: List of task packets
            completed_packets: Set of completed packet IDs
            gate_failures: Dict of gate ID to consecutive failure count
            kill_switches: List of tripped kill-switches
            metric_trends: Dict of metric ID to historical values
        """
        self._incidents = incidents
        self._packets = packets
        self._completed_packets = completed_packets
        self._gate_failures = gate_failures
        self._kill_switches_tripped = kill_switches
        self._metric_trends = metric_trends

    async def run_weekly_loop(self) -> WeeklyReport:
        """
        Run the complete weekly control loop.

        Returns:
            WeeklyReport with loop outcomes
        """
        self._current_week = self._get_current_week()
        self._loop_started_at = datetime.now()

        # Step 1: Collect metrics
        metrics = await self._step_collect()

        # Step 2: Evaluate progress
        gate_status = await self._step_evaluate(metrics)

        # Step 3: Prioritize backlog
        top_packets = await self._step_prioritize(gate_status)

        # Step 4: Decide go/no-go
        go_no_go_result = await self._step_decide(metrics, gate_status)

        # Step 5: Plan next 7 days
        plan = await self._step_plan(top_packets, go_no_go_result)

        # Step 6: Generate report
        report = await self._step_report(
            metrics=metrics,
            gate_status=gate_status,
            top_packets=top_packets,
            go_no_go_result=go_no_go_result,
            plan=plan,
        )

        self._reports.append(report)
        self._loop_completed_at = datetime.now()

        return report

    async def _step_collect(self) -> dict[str, Any]:
        """Step 1: Collect metrics from all sources."""
        # In production, this would gather from actual data sources
        return {
            "eval_metrics": {},
            "latency_metrics": {},
            "safety_metrics": {},
            "training_metrics": {},
            "cost_metrics": {
                "monthly_spend": 0.0,
                "daily_spend": 0.0,
                "monthly_pct_used": 0.0,
                "daily_pct_used": 0.0,
            },
            "incident_metrics": {
                "s1_count": 0,
                "s2_count": 0,
                "s3_count": 0,
            },
            "packet_metrics": {
                "pending": len([p for p in self._packets if p.status == PacketStatus.PENDING]),
                "completed": len(self._completed_packets),
            },
        }

    async def _step_evaluate(
        self, metrics: dict[str, Any]
    ) -> dict[str, str]:
        """Step 2: Evaluate progress against gates."""
        # In production, this would run gate evaluation
        return {
            "G1": "in_progress",
            "G2": "not_started",
            "G3": "not_started",
            "G4": "not_started",
        }

    async def _step_prioritize(
        self, gate_status: dict[str, str]
    ) -> list[dict[str, Any]]:
        """Step 3: Prioritize packet backlog."""
        # In production, this would run auto-prioritization
        return [
            {"packet_id": "PKT-TRAIN-001", "score": 85.0, "rationale": "Blocks G1"},
            {"packet_id": "PKT-EVAL-001", "score": 75.0, "rationale": "Required for gate eval"},
        ]

    async def _step_decide(
        self,
        metrics: dict[str, Any],
        gate_status: dict[str, str],
    ) -> GoNoGoResult:
        """
        Step 4: Decide go/no-go for the week.

        Applies the full go/no-go decision matrix from A6 specification:
        - GO: All metrics nominal, budget on track, no S1/S2 incidents
        - GO_WITH_WATCH: Minor issues (budget warning, S3 incident)
        - CONDITIONAL_GO: Significant issues (S2 unresolved, budget > 80%)
        - NO_GO: Critical issues (S1 open, budget exhausted, consecutive gate failures)
        """
        triggers = []
        watch_items = []
        required_actions = []
        blockers = []

        # Extract state
        monthly_pct = metrics.get("cost_metrics", {}).get("monthly_pct_used", 0.0)
        daily_pct = metrics.get("cost_metrics", {}).get("daily_pct_used", 0.0)
        s1_count = metrics.get("incident_metrics", {}).get("s1_count", 0)
        s2_count = metrics.get("incident_metrics", {}).get("s2_count", 0)
        s3_count = metrics.get("incident_metrics", {}).get("s3_count", 0)
        pending_packets = metrics.get("packet_metrics", {}).get("pending", 0)

        # Check NO-GO triggers (highest priority)
        no_go_checks = [
            (s1_count > 0, "open_s1_incident", f"{s1_count} S1 incident(s) open"),
            (monthly_pct >= 95, "budget_above_95_pct", f"Monthly budget at {monthly_pct:.0f}%"),
            (any(count >= 2 for count in self._gate_failures.values()), "two_consecutive_gate_failures", "2+ consecutive gate failures"),
            (len(self._kill_switches_tripped) > 0, "kill_switches_tripped", f"{len(self._kill_switches_tripped)} kill-switch(es) tripped"),
            (pending_packets == 0 and len(self._completed_packets) == 0, "zero_packets_executable", "No executable packets"),
        ]

        for condition, trigger_id, description in no_go_checks:
            if condition:
                triggers.append(trigger_id)
                blockers.append(description)

        # If any NO-GO trigger fired, return NO-GO
        if triggers:
            return GoNoGoResult(
                decision=GoNoGoDecision.NO_GO,
                triggers=triggers,
                blockers=blockers,
                required_actions=["Resolve blockers before proceeding", "Escalate to stakeholders"],
            )

        # Check CONDITIONAL-GO triggers
        conditional_go_checks = [
            (s2_count > 0, "s2_incident_unresolved", f"{s2_count} S2 incident(s) unresolved"),
            (80 <= monthly_pct < 95, "budget_between_80_and_95_pct", f"Monthly budget at {monthly_pct:.0f}%"),
            (any(count == 1 for count in self._gate_failures.values()), "gate_metric_regressed", "Gate metric regression detected"),
        ]

        for condition, trigger_id, description in conditional_go_checks:
            if condition:
                triggers.append(trigger_id)
                required_actions.append(description)

        # If any CONDITIONAL-GO trigger fired, return CONDITIONAL_GO
        if triggers:
            return GoNoGoResult(
                decision=GoNoGoDecision.CONDITIONAL_GO,
                triggers=triggers,
                required_actions=required_actions,
            )

        # Check WATCH triggers
        watch_checks = [
            (60 <= monthly_pct < 80, "budget_between_60_and_80_pct", f"Monthly budget at {monthly_pct:.0f}%"),
            (s3_count > 0, "s3_incident_open", f"{s3_count} S3 incident(s) open"),
            (daily_pct > 60, "daily_budget_elevated", f"Daily budget at {daily_pct:.0f}%"),
        ]

        for condition, trigger_id, description in watch_checks:
            if condition:
                triggers.append(trigger_id)
                watch_items.append(description)

        # If any WATCH trigger fired, return GO_WITH_WATCH
        if triggers:
            return GoNoGoResult(
                decision=GoNoGoDecision.GO_WITH_WATCH,
                triggers=triggers,
                watch_items=watch_items,
            )

        # Default: GO
        return GoNoGoResult(
            decision=GoNoGoDecision.GO,
            triggers=[],
            watch_items=[],
            required_actions=[],
        )

    async def _step_plan(
        self,
        top_packets: list[dict[str, Any]],
        go_no_go_result: GoNoGoResult,
    ) -> dict[str, Any]:
        """Step 5: Generate next 7 days plan."""
        plan = {
            "packets": top_packets,
            "estimated_cost_usd": 50.0,
            "success_criteria": [],
            "constraints": [],
        }

        # Apply constraints based on go/no-go decision
        if go_no_go_result.decision == GoNoGoDecision.CONDITIONAL_GO:
            plan["constraints"] = go_no_go_result.required_actions
            # Reduce scope for conditional go
            plan["packets"] = top_packets[:2]  # Only top 2 packets
            plan["estimated_cost_usd"] = 25.0

        if go_no_go_result.decision == GoNoGoDecision.GO_WITH_WATCH:
            plan["watch_items"] = go_no_go_result.watch_items

        return plan

    async def _step_report(
        self,
        metrics: dict[str, Any],
        gate_status: dict[str, str],
        top_packets: list[dict[str, Any]],
        go_no_go_result: GoNoGoResult,
        plan: dict[str, Any],
    ) -> WeeklyReport:
        """Step 6: Generate weekly report."""
        return WeeklyReport(
            week=self._current_week,
            generated_at=datetime.now(),
            go_no_go_decision=go_no_go_result.decision,
            metrics_summary=metrics,
            gate_status=gate_status,
            budget_status={
                "monthly_spend": metrics.get("cost_metrics", {}).get("monthly_spend", 0.0),
                "monthly_pct_used": metrics.get("cost_metrics", {}).get("monthly_pct_used", 0.0),
                "runway_days": self._calculate_runway_days(metrics),
            },
            top_packets=top_packets,
            watch_items=go_no_go_result.watch_items,
            blockers=go_no_go_result.blockers,
            next_7_days_plan=plan,
            go_no_go_result=go_no_go_result,
        )

    def _calculate_runway_days(self, metrics: dict[str, Any]) -> float:
        """Calculate runway in days based on current burn rate."""
        monthly_spend = metrics.get("cost_metrics", {}).get("monthly_spend", 0.0)
        monthly_cap = 500.0  # Would come from config

        if monthly_spend <= 0:
            return 30.0

        remaining = monthly_cap - monthly_spend
        days_elapsed = min(30, datetime.now().day)
        daily_burn = monthly_spend / days_elapsed

        if daily_burn <= 0:
            return 30.0

        return remaining / daily_burn

    def get_latest_report(self) -> WeeklyReport | None:
        """Get the latest weekly report."""
        return self._reports[-1] if self._reports else None

    def get_all_reports(self) -> list[WeeklyReport]:
        """Get all weekly reports."""
        return self._reports.copy()

    def get_loop_duration_minutes(self) -> float:
        """Get duration of last loop in minutes."""
        if self._loop_started_at and self._loop_completed_at:
            return (self._loop_completed_at - self._loop_started_at).total_seconds() / 60
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "current_week": self._current_week,
            "loop_started_at": self._loop_started_at.isoformat() if self._loop_started_at else None,
            "loop_completed_at": self._loop_completed_at.isoformat() if self._loop_completed_at else None,
            "loop_duration_minutes": self.get_loop_duration_minutes(),
            "reports": [r.to_dict() for r in self._reports],
        }
