"""
Tests for Phase 2 enhancements: weekly loop, decision delivery, and packet compiler.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from theta_gamma.weekly_loop.runbook import (
    WeeklyControlLoop,
    GoNoGoDecision,
    GoNoGoResult,
    WeeklyReport,
)
from theta_gamma.decisions.delivery import (
    DecisionPacketDelivery,
    DeliveryChannel,
    DeliveryStatus,
    DeliveryRecipient,
    DeliveryResult,
)
from theta_gamma.compiler.compiler import (
    PacketCompiler,
    DependencyCycleError,
    DependencyNotFoundError,
)
from theta_gamma.compiler.packets import (
    TaskPacket,
    PacketDomain,
    PacketPriority,
    PacketStatus,
    PacketTest,
)
from theta_gamma.decisions.packets import (
    DecisionPacket,
    Decision,
    DecisionOption,
    DecisionImpact,
    DecisionUrgency,
)


class TestWeeklyControlLoop:
    """Test enhanced weekly control loop with go/no-go logic."""

    @pytest.mark.asyncio
    async def test_go_decision_all_clear(self) -> None:
        """Test GO decision when all metrics are nominal."""
        loop = WeeklyControlLoop()
        
        # Set state with no issues
        loop.set_state(
            incidents=[],
            packets=[],
            completed_packets={"PKT-EXISTING-001"},  # At least one packet completed
            gate_failures={},
            kill_switches=[],
            metric_trends={},
        )

        report = await loop.run_weekly_loop()

        assert report.go_no_go_decision == GoNoGoDecision.GO
        assert report.go_no_go_result is not None
        assert report.go_no_go_result.decision == GoNoGoDecision.GO

    @pytest.mark.asyncio
    async def test_go_with_watch_budget_warning(self) -> None:
        """Test GO_WITH_WATCH when budget is between 60-80%."""
        loop = WeeklyControlLoop()
        loop.set_state(
            incidents=[],
            packets=[],
            completed_packets={"PKT-EXISTING-001"},
            gate_failures={},
            kill_switches=[],
            metric_trends={},
        )

        # Mock metrics with budget warning
        original_step_collect = loop._step_collect

        async def mock_collect():
            metrics = await original_step_collect()
            metrics["cost_metrics"]["monthly_pct_used"] = 65.0
            metrics["cost_metrics"]["daily_pct_used"] = 50.0
            return metrics

        loop._step_collect = mock_collect

        report = await loop.run_weekly_loop()

        assert report.go_no_go_decision == GoNoGoDecision.GO_WITH_WATCH
        assert report.go_no_go_result is not None
        assert "budget_between_60_and_80_pct" in report.go_no_go_result.triggers

    @pytest.mark.asyncio
    async def test_conditional_go_s2_incident(self) -> None:
        """Test CONDITIONAL_GO when S2 incident is unresolved."""
        loop = WeeklyControlLoop()
        loop.set_state(
            incidents=[{"severity": "S2", "id": "INC-001"}],
            packets=[],
            completed_packets={"PKT-EXISTING-001"},
            gate_failures={},
            kill_switches=[],
            metric_trends={},
        )

        # Mock metrics with S2 incident
        original_step_collect = loop._step_collect

        async def mock_collect():
            metrics = await original_step_collect()
            metrics["incident_metrics"]["s2_count"] = 1
            return metrics

        loop._step_collect = mock_collect

        report = await loop.run_weekly_loop()

        assert report.go_no_go_decision == GoNoGoDecision.CONDITIONAL_GO
        assert report.go_no_go_result is not None
        assert "s2_incident_unresolved" in report.go_no_go_result.triggers

    @pytest.mark.asyncio
    async def test_no_go_s1_incident(self) -> None:
        """Test NO-GO when S1 incident is open."""
        loop = WeeklyControlLoop()
        loop.set_state(
            incidents=[{"severity": "S1", "id": "INC-001"}],
            packets=[],
            completed_packets=set(),
            gate_failures={},
            kill_switches=[],
            metric_trends={},
        )

        # Mock metrics with S1 incident
        original_step_collect = loop._step_collect

        async def mock_collect():
            metrics = await original_step_collect()
            metrics["incident_metrics"]["s1_count"] = 1
            return metrics

        loop._step_collect = mock_collect

        report = await loop.run_weekly_loop()

        assert report.go_no_go_decision == GoNoGoDecision.NO_GO
        assert report.go_no_go_result is not None
        assert "open_s1_incident" in report.go_no_go_result.triggers
        assert len(report.blockers) > 0

    @pytest.mark.asyncio
    async def test_no_go_budget_exhausted(self) -> None:
        """Test NO-GO when budget is above 95%."""
        loop = WeeklyControlLoop()

        original_step_collect = loop._step_collect

        async def mock_collect():
            metrics = await original_step_collect()
            metrics["cost_metrics"]["monthly_pct_used"] = 96.0
            return metrics

        loop._step_collect = mock_collect

        report = await loop.run_weekly_loop()

        assert report.go_no_go_decision == GoNoGoDecision.NO_GO
        assert "budget_above_95_pct" in report.go_no_go_result.triggers

    @pytest.mark.asyncio
    async def test_no_go_consecutive_gate_failures(self) -> None:
        """Test NO-GO when there are 2+ consecutive gate failures."""
        loop = WeeklyControlLoop()
        loop.set_state(
            incidents=[],
            packets=[],
            completed_packets=set(),
            gate_failures={"G1": 2},
            kill_switches=[],
            metric_trends={},
        )

        report = await loop.run_weekly_loop()

        assert report.go_no_go_decision == GoNoGoDecision.NO_GO
        assert "two_consecutive_gate_failures" in report.go_no_go_result.triggers

    @pytest.mark.asyncio
    async def test_conditional_go_reduced_scope(self) -> None:
        """Test that CONDITIONAL_GO reduces plan scope."""
        loop = WeeklyControlLoop()

        original_step_collect = loop._step_collect

        async def mock_collect():
            metrics = await original_step_collect()
            metrics["cost_metrics"]["monthly_pct_used"] = 85.0
            return metrics

        loop._step_collect = mock_collect
        loop.set_state(
            incidents=[],
            packets=[],
            completed_packets={"PKT-EXISTING-001"},
            gate_failures={},
            kill_switches=[],
            metric_trends={},
        )

        report = await loop.run_weekly_loop()

        assert report.go_no_go_decision == GoNoGoDecision.CONDITIONAL_GO
        # Plan should have reduced scope
        assert report.next_7_days_plan.get("constraints") is not None


class TestPacketCompiler:
    """Test packet compiler with DAG resolution."""

    def test_compile_packets(self) -> None:
        """Test packet compilation."""
        compiler = PacketCompiler()
        packets = compiler.compile_artifacts(Path("artifacts"))

        assert len(packets) > 0
        assert compiler._validated is True

    def test_dependency_graph_built(self) -> None:
        """Test dependency graph construction."""
        compiler = PacketCompiler()
        compiler.compile_artifacts(Path("artifacts"))

        graph = compiler.get_dependency_graph()

        assert len(graph) > 0
        # PKT-TRAIN-001 should depend on PKT-INFRA-001 and PKT-DATA-001
        train_deps = graph.get("PKT-TRAIN-001", [])
        assert "PKT-INFRA-001" in train_deps
        assert "PKT-DATA-001" in train_deps

    def test_reverse_graph_built(self) -> None:
        """Test reverse dependency graph construction."""
        compiler = PacketCompiler()
        compiler.compile_artifacts(Path("artifacts"))

        reverse_graph = compiler.get_reverse_graph()

        # PKT-INFRA-001 should have PKT-TRAIN-001 as dependent
        train_dependents = reverse_graph.get("PKT-INFRA-001", [])
        assert "PKT-TRAIN-001" in train_dependents

    def test_execution_order(self) -> None:
        """Test topological sort for execution order."""
        compiler = PacketCompiler()
        compiler.compile_artifacts(Path("artifacts"))

        order = compiler.get_execution_order()

        # Dependencies should come before dependents
        infra_idx = order.index("PKT-INFRA-001")
        data_idx = order.index("PKT-DATA-001")
        train_idx = order.index("PKT-TRAIN-001")

        assert infra_idx < train_idx
        assert data_idx < train_idx

    def test_executable_packets(self) -> None:
        """Test getting executable packets."""
        compiler = PacketCompiler()
        compiler.compile_artifacts(Path("artifacts"))

        # Initially, only packets with no dependencies are executable
        executable = compiler.get_executable_packets(set())

        executable_ids = [p.packet_id for p in executable]
        assert "PKT-INFRA-001" in executable_ids
        assert "PKT-DATA-001" in executable_ids
        assert "PKT-BUDGET-001" in executable_ids
        # TRAIN and EVAL should not be executable yet
        assert "PKT-TRAIN-001" not in executable_ids

    def test_executable_after_dependencies_met(self) -> None:
        """Test packets become executable after dependencies complete."""
        compiler = PacketCompiler()
        compiler.compile_artifacts(Path("artifacts"))

        # Complete INFRA and DATA packets
        completed = {"PKT-INFRA-001", "PKT-DATA-001"}
        executable = compiler.get_executable_packets(completed)

        executable_ids = [p.packet_id for p in executable]
        # TRAIN should now be executable
        assert "PKT-TRAIN-001" in executable_ids

    def test_dependency_chain(self) -> None:
        """Test getting full dependency chain."""
        compiler = PacketCompiler()
        compiler.compile_artifacts(Path("artifacts"))

        # OPS depends on EVAL and BUDGET, EVAL depends on DATA
        chain = compiler.get_dependency_chain("PKT-OPS-001")

        assert "PKT-EVAL-001" in chain
        assert "PKT-BUDGET-001" in chain
        assert "PKT-DATA-001" in chain

    def test_critical_path(self) -> None:
        """Test critical path calculation."""
        compiler = PacketCompiler()
        compiler.compile_artifacts(Path("artifacts"))

        path = compiler.get_critical_path()

        assert len(path) > 0
        # Critical path should end with OPS (has most dependencies)
        assert path[-1] == "PKT-OPS-001"

    def test_cycle_detection(self) -> None:
        """Test dependency cycle detection."""
        compiler = PacketCompiler()

        # Create packets with a cycle
        compiler._packets = {
            "PKT-A": TaskPacket(
                packet_id="PKT-A",
                title="A",
                priority=PacketPriority.P0_CRITICAL,
                domain=PacketDomain.INFRA,
                estimated_effort="1d",
                depends_on=["PKT-B"],
                objective="A",
                inputs=[],
                commands=[],
                tests=[],
                done_definition="A done",
                stop_condition="A failed",
            ),
            "PKT-B": TaskPacket(
                packet_id="PKT-B",
                title="B",
                priority=PacketPriority.P0_CRITICAL,
                domain=PacketDomain.INFRA,
                estimated_effort="1d",
                depends_on=["PKT-A"],  # Cycle!
                objective="B",
                inputs=[],
                commands=[],
                tests=[],
                done_definition="B done",
                stop_condition="B failed",
            ),
        }

        compiler._build_dependency_graphs()

        with pytest.raises(DependencyCycleError):
            compiler.validate_dependencies()

    def test_missing_dependency_error(self) -> None:
        """Test error on missing dependency."""
        compiler = PacketCompiler()

        # Create packet with non-existent dependency
        compiler._packets = {
            "PKT-A": TaskPacket(
                packet_id="PKT-A",
                title="A",
                priority=PacketPriority.P0_CRITICAL,
                domain=PacketDomain.INFRA,
                estimated_effort="1d",
                depends_on=["PKT-NONEXISTENT"],
                objective="A",
                inputs=[],
                commands=[],
                tests=[],
                done_definition="A done",
                stop_condition="A failed",
            ),
        }

        compiler._build_dependency_graphs()

        with pytest.raises(DependencyNotFoundError):
            compiler.validate_dependencies()


class TestDecisionPacketDelivery:
    """Test decision packet delivery system."""

    @pytest.mark.asyncio
    async def test_deliver_packet(self, tmp_path: Path) -> None:
        """Test decision packet delivery."""
        delivery = DecisionPacketDelivery(file_output_dir=tmp_path)

        # Create a test decision packet
        packet = DecisionPacket(
            packet_id="DP-2026-W12-001",
            week="2026-W12",
            generated_at=datetime.now(),
            deadline=datetime.now() + timedelta(hours=32),
        )

        # Add a test decision
        decision = Decision(
            decision_id="D1",
            title="Test Decision",
            impact=DecisionImpact.HIGH,
            urgency=DecisionUrgency.THIS_WEEK,
            context="Test context",
            options=[
                DecisionOption("A", "Option A", is_recommended=True),
                DecisionOption("B", "Option B"),
            ],
            recommended_default=DecisionOption("A", "Option A", is_recommended=True),
            deadline=datetime.now() + timedelta(hours=32),
        )
        packet.add_decision(decision)

        # Create recipient
        recipient = DeliveryRecipient(
            name="Test User",
            email="test@example.com",
            slack_id="U123456",
            role="tech_lead",
        )

        # Deliver
        result = await delivery.deliver_packet(
            packet=packet,
            recipients=[recipient],
            deadline_hours=32,
        )

        assert result.packet_id == packet.packet_id
        assert result.success is True
        assert len(result.notifications) > 0

    @pytest.mark.asyncio
    async def test_delivery_channels(self, tmp_path: Path) -> None:
        """Test multi-channel delivery."""
        delivery = DecisionPacketDelivery(file_output_dir=tmp_path)

        packet = DecisionPacket(
            packet_id="DP-2026-W12-002",
            week="2026-W12",
            generated_at=datetime.now(),
            deadline=datetime.now() + timedelta(hours=32),
        )

        recipient = DeliveryRecipient(
            name="Test User",
            email="test@example.com",
            slack_id="U123456",
        )

        result = await delivery.deliver_packet(packet, [recipient])

        # Should have notifications for multiple channels
        channels = set(n.channel for n in result.notifications)
        assert DeliveryChannel.DASHBOARD in channels
        assert DeliveryChannel.FILE in channels

    def test_process_response(self, tmp_path: Path) -> None:
        """Test processing human response."""
        delivery = DecisionPacketDelivery(file_output_dir=tmp_path)

        packet = DecisionPacket(
            packet_id="DP-2026-W12-003",
            week="2026-W12",
            generated_at=datetime.now(),
            deadline=datetime.now() + timedelta(hours=32),
        )

        decision = Decision(
            decision_id="D1",
            title="Test Decision",
            impact=DecisionImpact.HIGH,
            urgency=DecisionUrgency.THIS_WEEK,
            context="Test",
            options=[
                DecisionOption("A", "Option A", is_recommended=True),
                DecisionOption("B", "Option B"),
            ],
            recommended_default=DecisionOption("A", "Option A", is_recommended=True),
            deadline=datetime.now() + timedelta(hours=32),
        )
        packet.add_decision(decision)

        recipient = DeliveryRecipient(name="Test")
        result = delivery._delivery_history.append(
            DeliveryResult(
                packet_id=packet.packet_id,
                delivered_at=datetime.now(),
                response_deadline=datetime.now() + timedelta(hours=32),
            )
        )

        # Process response
        success = delivery.process_response(packet.packet_id, {"D1": "B"})

        assert success is True
        assert delivery.get_response(packet.packet_id) == {"D1": "B"}

    def test_get_overdue_packets(self, tmp_path: Path) -> None:
        """Test getting overdue packets."""
        delivery = DecisionPacketDelivery(file_output_dir=tmp_path)

        # Add an overdue delivery result
        overdue_result = DeliveryResult(
            packet_id="DP-OVERDUE-001",
            delivered_at=datetime.now() - timedelta(days=2),
            response_deadline=datetime.now() - timedelta(days=1),
        )
        delivery._delivery_history.append(overdue_result)

        overdue = delivery.get_overdue_packets()

        assert len(overdue) == 1
        assert overdue[0].packet_id == "DP-OVERDUE-001"

    def test_delivery_stats(self, tmp_path: Path) -> None:
        """Test delivery statistics."""
        delivery = DecisionPacketDelivery(file_output_dir=tmp_path)

        # Add some delivery results
        for i in range(3):
            result = DeliveryResult(
                packet_id=f"DP-STATS-{i:03d}",
                delivered_at=datetime.now(),
                response_deadline=datetime.now() + timedelta(hours=32),
            )
            delivery._delivery_history.append(result)

        # Process response for one
        delivery.process_response("DP-STATS-000", {"D1": "A"})

        stats = delivery.get_delivery_stats()

        assert stats["total_deliveries"] == 3
        assert stats["response_rate"] == 1 / 3
