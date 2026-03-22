"""Tests for the compiler, recovery, weekly_loop, decisions, and external modules."""

import pytest
from datetime import datetime, timedelta

from theta_gamma.compiler.packets import (
    TaskPacket,
    PacketDomain,
    PacketPriority,
    PacketStatus,
    PacketTest,
)
from theta_gamma.compiler.quality import (
    QualityRubric,
    QualityTier,
)
from theta_gamma.recovery.state_machine import (
    RecoveryStateMachine,
    IncidentState,
    IncidentSeverity,
)
from theta_gamma.weekly_loop.runbook import (
    WeeklyControlLoop,
    GoNoGoDecision,
)
from theta_gamma.decisions.packets import (
    Decision,
    DecisionPacket,
    DecisionImpact,
    DecisionUrgency,
    DecisionOption,
    DecisionStatus,
)
from theta_gamma.external.pilot import (
    PilotSOW,
    PilotSuccessCriteria,
    PilotDeliverable,
)


class TestTaskPacket:
    """Tests for TaskPacket."""

    def test_packet_creation(self):
        """Test packet creation."""
        packet = TaskPacket(
            packet_id="PKT-TEST-001",
            title="Test Packet",
            priority=PacketPriority.P0_CRITICAL,
            domain=PacketDomain.INFRA,
            estimated_effort="1d",
            objective="Test objective",
            commands=["echo test"],
            tests=[PacketTest(name="Test", command="test", expected="pass")],
            done_definition="Test done",
            stop_condition="Test stop",
        )

        assert packet.packet_id == "PKT-TEST-001"
        assert packet.priority == PacketPriority.P0_CRITICAL

    def test_is_executable(self):
        """Test executable checking."""
        packet = TaskPacket(
            packet_id="PKT-TEST-002",
            title="Test",
            priority=PacketPriority.P1_HIGH,
            domain=PacketDomain.INFRA,
            estimated_effort="1d",
            depends_on=["PKT-TEST-001"],
        )

        # Not executable - dependency not complete
        assert packet.is_executable(set()) is False

        # Executable - dependency complete
        assert packet.is_executable({"PKT-TEST-001"}) is True

    def test_validate(self):
        """Test packet validation."""
        # Valid packet
        packet = TaskPacket(
            packet_id="PKT-TEST-003",
            title="Test",
            priority=PacketPriority.P1_HIGH,
            domain=PacketDomain.INFRA,
            estimated_effort="1d",
            objective="Test",
            commands=["test"],
            tests=[PacketTest("t", "c", "e")],
            done_definition="Done",
            stop_condition="Stop",
        )

        is_valid, issues = packet.validate()
        assert is_valid is True
        assert len(issues) == 0

        # Invalid packet - missing fields
        packet2 = TaskPacket(
            packet_id="PKT-TEST-004",
            title="Test",
            priority=PacketPriority.P1_HIGH,
            domain=PacketDomain.INFRA,
            estimated_effort="1d",
        )

        is_valid, issues = packet2.validate()
        assert is_valid is False
        assert len(issues) > 0

    def test_mark_complete(self):
        """Test marking packet complete."""
        packet = TaskPacket(
            packet_id="PKT-TEST-005",
            title="Test",
            priority=PacketPriority.P1_HIGH,
            domain=PacketDomain.INFRA,
            estimated_effort="1d",
        )

        assert packet.status == PacketStatus.PENDING

        packet.mark_complete()

        assert packet.status == PacketStatus.DONE
        assert packet.completed_at is not None


class TestQualityRubric:
    """Tests for QualityRubric."""

    def test_assess_gold_tier(self):
        """Test assessing gold tier packet."""
        rubric = QualityRubric()

        packet = TaskPacket(
            packet_id="PKT-TEST-001",
            title="Test",
            priority=PacketPriority.P0_CRITICAL,
            domain=PacketDomain.INFRA,
            estimated_effort="1d",
            objective="Test objective",
            inputs=["input1"],
            commands=["concrete command 1", "concrete command 2"],
            tests=[PacketTest("t", "python test.py", "pass")],
            done_definition="Done definition",
            stop_condition="Stop condition with revert",
        )

        score = rubric.assess(packet)

        assert score.completeness_passed is True
        assert score.tier in [QualityTier.GOLD, QualityTier.SILVER]

    def test_assess_reject_tier(self):
        """Test assessing reject tier packet."""
        rubric = QualityRubric()

        packet = TaskPacket(
            packet_id="PKT-TEST-002",
            title="Test",
            priority=PacketPriority.P1_HIGH,
            domain=PacketDomain.INFRA,
            estimated_effort="1d",
            # Missing required fields
        )

        score = rubric.assess(packet)

        assert score.completeness_passed is False
        assert score.tier == QualityTier.REJECT


class TestRecoveryStateMachine:
    """Tests for RecoveryStateMachine."""

    def test_create_incident(self):
        """Test incident creation."""
        sm = RecoveryStateMachine()

        incident = sm.create_incident("FM-TR-01")

        assert incident.incident_id.startswith("INC-")
        assert incident.state == IncidentState.DETECTED
        assert incident.severity == IncidentSeverity.S1_CRITICAL

    def test_execute_retry_success(self):
        """Test successful retry."""
        sm = RecoveryStateMachine()
        incident = sm.create_incident("FM-TR-01")

        # First retry succeeds
        sm.execute_retry(incident, attempt=1, success=True)

        assert incident.state == IncidentState.RECOVERED
        assert incident.resolution_method == "retry_1"

    def test_execute_retry_then_escalate(self):
        """Test retry failure leading to escalation."""
        sm = RecoveryStateMachine()
        incident = sm.create_incident("FM-TR-01")

        # First retry fails
        sm.execute_retry(incident, attempt=1, success=False)
        assert incident.state == IncidentState.RETRY_2

        # Second retry fails - escalate
        sm.execute_retry(incident, attempt=2, success=False)
        assert incident.state == IncidentState.ESCALATED

    def test_get_active_incidents(self):
        """Test getting active incidents."""
        sm = RecoveryStateMachine()

        sm.create_incident("FM-TR-01")
        sm.create_incident("FM-TR-02")

        active = sm.get_active_incidents()
        assert len(active) == 2


class TestWeeklyControlLoop:
    """Tests for WeeklyControlLoop."""

    @pytest.mark.asyncio
    async def test_run_weekly_loop(self):
        """Test running weekly loop."""
        loop = WeeklyControlLoop()

        report = await loop.run_weekly_loop()

        assert report.week != ""
        assert report.go_no_go_decision in GoNoGoDecision
        assert report.generated_at is not None

    def test_get_latest_report(self):
        """Test getting latest report."""
        loop = WeeklyControlLoop()

        # No reports yet
        assert loop.get_latest_report() is None


class TestDecision:
    """Tests for Decision."""

    def test_decision_creation(self):
        """Test decision creation."""
        option_a = DecisionOption(label="A", description="Option A", is_recommended=True)
        option_b = DecisionOption(label="B", description="Option B")

        decision = Decision(
            decision_id="D1",
            title="Test Decision",
            impact=DecisionImpact.HIGH,
            urgency=DecisionUrgency.THIS_WEEK,
            context="Test context",
            options=[option_a, option_b],
            recommended_default=option_a,
            deadline=datetime.now() + timedelta(days=1),
        )

        assert decision.decision_id == "D1"
        assert decision.score == 16  # 4 * 4

    def test_apply_default(self):
        """Test applying default."""
        option_a = DecisionOption(label="A", description="Option A", is_recommended=True)

        decision = Decision(
            decision_id="D2",
            title="Test",
            impact=DecisionImpact.MEDIUM,
            urgency=DecisionUrgency.SOON,
            context="Test",
            options=[option_a],
            recommended_default=option_a,
            deadline=datetime.now() + timedelta(days=1),
        )

        assert decision.status == DecisionStatus.PENDING

        decision.apply_default()

        assert decision.status == DecisionStatus.DEFAULTED
        assert decision.response == "A"

    def test_respond(self):
        """Test human response."""
        option_a = DecisionOption(label="A", description="Option A")
        option_b = DecisionOption(label="B", description="Option B")

        decision = Decision(
            decision_id="D3",
            title="Test",
            impact=DecisionImpact.MEDIUM,
            urgency=DecisionUrgency.SOON,
            context="Test",
            options=[option_a, option_b],
            recommended_default=option_a,
            deadline=datetime.now() + timedelta(days=1),
        )

        decision.respond("B")

        assert decision.status == DecisionStatus.ANSWERED
        assert decision.response == "B"


class TestDecisionPacket:
    """Tests for DecisionPacket."""

    def test_packet_creation(self):
        """Test packet creation."""
        packet = DecisionPacket(
            packet_id="DP-2026-W08",
            week="2026-W08",
            generated_at=datetime.now(),
            deadline=datetime.now() + timedelta(days=1),
        )

        assert packet.packet_id == "DP-2026-W08"
        assert len(packet.decisions) == 0

    def test_add_decision(self):
        """Test adding decisions."""
        packet = DecisionPacket(
            packet_id="DP-2026-W08",
            week="2026-W08",
            generated_at=datetime.now(),
            deadline=datetime.now() + timedelta(days=1),
        )

        # Add 6 decisions - should keep top 5
        for i in range(6):
            option = DecisionOption(label="A", description="Option A", is_recommended=True)
            decision = Decision(
                decision_id=f"D{i}",
                title=f"Decision {i}",
                impact=DecisionImpact(i % 5 + 1),
                urgency=DecisionUrgency.THIS_WEEK,
                context="Test",
                options=[option],
                recommended_default=option,
                deadline=datetime.now() + timedelta(days=1),
            )
            packet.add_decision(decision)

        assert len(packet.decisions) == 5
        assert len(packet.deferred_decisions) == 1


class TestPilotSOW:
    """Tests for PilotSOW."""

    def test_create_template(self):
        """Test creating SOW template."""
        sow = PilotSOW.create_template("Test Partner Inc.")

        assert sow.partner == "Test Partner Inc."
        assert sow.duration_weeks == 10
        assert len(sow.deliverables) > 0
        assert len(sow.success_criteria) > 0

    def test_evaluate_success(self):
        """Test success evaluation."""
        sow = PilotSOW.create_template("Test Partner")

        # Add a 6th criterion to meet the >= 6 threshold
        sow.add_success_criterion(
            PilotSuccessCriteria(
                criterion="Consistency",
                metric="M-CM-003",
                target=">= 65%",
                measurement_method="Eval harness",
            )
        )

        # Mark all criteria as passed
        for criterion in sow.success_criteria:
            criterion.passed = True
            criterion.actual_value = "Achieved"

        passed, summary = sow.evaluate_success()
        assert passed is True

    def test_add_deliverable(self):
        """Test adding deliverable."""
        sow = PilotSOW(
            sow_id="SOW-TEST-001",
            provider="Provider",
            partner="Partner",
            effective_date=datetime.now(),
        )

        deliverable = PilotDeliverable(
            id="D-TEST",
            description="Test deliverable",
            owner="Provider",
            due_week=1,
            acceptance_criteria="Test criteria",
        )

        sow.add_deliverable(deliverable)

        assert len(sow.deliverables) == 1
