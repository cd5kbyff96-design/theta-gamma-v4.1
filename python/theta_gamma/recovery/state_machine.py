"""
Recovery State Machine — Deterministic failure recovery.

This module implements the state machine for recovering from failed
runs, failed tests, and stalled delivery.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class IncidentState(str, Enum):
    """
    Incident states in the recovery state machine.

    States progress through: HEALTHY -> DETECTED -> RETRY-1 -> RETRY-2 -> ESCALATED -> RECOVERED -> HEALTHY
    """

    HEALTHY = "healthy"
    DETECTED = "detected"
    RETRY_1 = "retry_1"
    RETRY_2 = "retry_2"
    ESCALATED = "escalated"
    RECOVERED = "recovered"


class IncidentSeverity(str, Enum):
    """
    Incident severity levels.

    Determines SLA and escalation path.
    """

    S1_CRITICAL = "S1"
    S2_HIGH = "S2"
    S3_MEDIUM = "S3"


@dataclass
class StateTransition:
    """
    A state transition record.

    Attributes:
        from_state: Source state
        to_state: Target state
        timestamp: Transition timestamp
        action_taken: Action that triggered transition
        outcome: Transition outcome
        duration_minutes: Time spent in source state
    """

    from_state: IncidentState
    to_state: IncidentState
    timestamp: datetime
    action_taken: str
    outcome: str
    duration_minutes: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "timestamp": self.timestamp.isoformat(),
            "action_taken": self.action_taken,
            "outcome": self.outcome,
            "duration_minutes": self.duration_minutes,
        }


@dataclass
class Incident:
    """
    An incident record.

    Attributes:
        incident_id: Unique identifier
        failure_mode_id: Failure mode that triggered incident
        severity: Incident severity
        owner: Incident owner
        state: Current state
        created_at: Creation timestamp
        resolved_at: Resolution timestamp
        transitions: State transition history
        root_cause: Root cause if resolved
        resolution_method: How incident was resolved
    """

    incident_id: str
    failure_mode_id: str
    severity: IncidentSeverity
    owner: str
    state: IncidentState = IncidentState.DETECTED
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None
    transitions: list[StateTransition] = field(default_factory=list)
    root_cause: str = ""
    resolution_method: str = ""
    escalation_target: str = ""
    sla_met: bool = True

    def transition_to(
        self,
        new_state: IncidentState,
        action_taken: str,
        outcome: str,
    ) -> StateTransition:
        """
        Transition to a new state.

        Args:
            new_state: Target state
            action_taken: Action that triggered transition
            outcome: Transition outcome

        Returns:
            StateTransition record
        """
        # Calculate duration in current state
        if self.transitions:
            last_transition = self.transitions[-1]
            duration = (datetime.now() - last_transition.timestamp).total_seconds() / 60
        else:
            duration = (datetime.now() - self.created_at).total_seconds() / 60

        transition = StateTransition(
            from_state=self.state,
            to_state=new_state,
            timestamp=datetime.now(),
            action_taken=action_taken,
            outcome=outcome,
            duration_minutes=duration,
        )

        self.transitions.append(transition)
        self.state = new_state

        if new_state == IncidentState.RECOVERED:
            self.resolved_at = datetime.now()

        return transition

    def get_total_resolution_time_minutes(self) -> float:
        """Get total resolution time in minutes."""
        if self.resolved_at:
            return (self.resolved_at - self.created_at).total_seconds() / 60
        return (datetime.now() - self.created_at).total_seconds() / 60

    def get_sla_class(self) -> str:
        """Get SLA class based on severity."""
        sla_mapping = {
            IncidentSeverity.S1_CRITICAL: "immediate",
            IncidentSeverity.S2_HIGH: "4h",
            IncidentSeverity.S3_MEDIUM: "24h",
        }
        return sla_mapping.get(self.severity, "24h")

    def is_sla_breached(self) -> bool:
        """Check if SLA has been breached."""
        sla_hours = {
            "immediate": 4,  # 4 hours total resolution
            "4h": 24,
            "24h": 72,
        }
        max_hours = sla_hours.get(self.get_sla_class(), 72)
        return self.get_total_resolution_time_minutes() > (max_hours * 60)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "incident_id": self.incident_id,
            "failure_mode_id": self.failure_mode_id,
            "severity": self.severity.value,
            "owner": self.owner,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "transitions": [t.to_dict() for t in self.transitions],
            "root_cause": self.root_cause,
            "resolution_method": self.resolution_method,
            "escalation_target": self.escalation_target,
            "sla_met": self.sla_met and not self.is_sla_breached(),
            "total_resolution_minutes": self.get_total_resolution_time_minutes(),
        }


class FailureModeRegistry:
    """Registry of failure modes with retry and fallback paths."""

    def __init__(self) -> None:
        """Initialize the failure mode registry."""
        self._failure_modes: dict[str, dict[str, Any]] = {}
        self._initialize_default_failure_modes()

    def _initialize_default_failure_modes(self) -> None:
        """Initialize default failure modes."""
        modes = {
            "FM-TR-01": {
                "name": "Loss divergence",
                "severity": IncidentSeverity.S1_CRITICAL,
                "owner": "ML Engineer",
                "retry_path": "Revert checkpoint + halve LR",
                "fallback_path": "Revert 2 checkpoints + halve LR + reduce batch",
                "escalation_target": "Tech Lead",
            },
            "FM-TR-02": {
                "name": "Validation loss plateau",
                "severity": IncidentSeverity.S2_HIGH,
                "owner": "ML Engineer",
                "retry_path": "Apply LR decay schedule",
                "fallback_path": "Switch optimizer + add warmup",
                "escalation_target": "Tech Lead",
            },
            "FM-CM-01": {
                "name": "Accuracy regression",
                "severity": IncidentSeverity.S2_HIGH,
                "owner": "ML Engineer",
                "retry_path": "Revert to previous checkpoint",
                "fallback_path": "Revert to best-known checkpoint + analyze data",
                "escalation_target": "Tech Lead",
            },
            "FM-LT-01": {
                "name": "Latency spike",
                "severity": IncidentSeverity.S2_HIGH,
                "owner": "Infra Engineer",
                "retry_path": "Profile + remove unoptimized ops",
                "fallback_path": "Apply quantization for inference",
                "escalation_target": "Tech Lead",
            },
            "FM-SF-01": {
                "name": "Safety violation spike",
                "severity": IncidentSeverity.S1_CRITICAL,
                "owner": "Safety Engineer",
                "retry_path": "Quarantine checkpoint + inspect data",
                "fallback_path": "Revert to last safe checkpoint + retrain",
                "escalation_target": "Safety Lead + Legal",
            },
        }
        self._failure_modes = modes

    def get_failure_mode(self, mode_id: str) -> dict[str, Any] | None:
        """Get failure mode by ID."""
        return self._failure_modes.get(mode_id)

    def get_retry_path(self, mode_id: str) -> str:
        """Get retry path for a failure mode."""
        mode = self.get_failure_mode(mode_id)
        return mode.get("retry_path", "Unknown") if mode else "Unknown"

    def get_fallback_path(self, mode_id: str) -> str:
        """Get fallback path for a failure mode."""
        mode = self.get_failure_mode(mode_id)
        return mode.get("fallback_path", "Unknown") if mode else "Unknown"


class RecoveryStateMachine:
    """
    State machine for failure recovery.

    Manages incidents through states: HEALTHY -> DETECTED -> RETRY-1 -> RETRY-2 -> ESCALATED -> RECOVERED

    Example:
        >>> sm = RecoveryStateMachine()
        >>> incident = sm.create_incident("FM-TR-01")
        >>> sm.execute_retry(incident, attempt=1, success=False)
        >>> sm.execute_retry(incident, attempt=2, success=True)
    """

    def __init__(self) -> None:
        """Initialize the recovery state machine."""
        self._incidents: dict[str, Incident] = {}
        self._failure_modes = FailureModeRegistry()
        self._incident_counter = 0

    def create_incident(self, failure_mode_id: str) -> Incident:
        """
        Create a new incident.

        Args:
            failure_mode_id: Failure mode that triggered incident

        Returns:
            New Incident
        """
        self._incident_counter += 1
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{self._incident_counter:03d}"

        mode = self._failure_modes.get_failure_mode(failure_mode_id)
        if not mode:
            mode = {
                "severity": IncidentSeverity.S3_MEDIUM,
                "owner": "Unassigned",
                "escalation_target": "Tech Lead",
            }

        incident = Incident(
            incident_id=incident_id,
            failure_mode_id=failure_mode_id,
            severity=mode.get("severity", IncidentSeverity.S3_MEDIUM),
            owner=mode.get("owner", "Unassigned"),
            escalation_target=mode.get("escalation_target", "Tech Lead"),
        )

        self._incidents[incident_id] = incident
        return incident

    def execute_retry(
        self,
        incident: Incident,
        attempt: int,
        success: bool,
        action_taken: str = "",
    ) -> Incident:
        """
        Execute a retry attempt.

        Args:
            incident: Incident to retry
            attempt: Retry attempt number (1 or 2)
            success: Whether retry succeeded
            action_taken: Action taken during retry

        Returns:
            Updated Incident
        """
        if not action_taken:
            if attempt == 1:
                action_taken = self._failure_modes.get_retry_path(incident.failure_mode_id)
            else:
                action_taken = self._failure_modes.get_fallback_path(incident.failure_mode_id)

        if success:
            incident.transition_to(
                IncidentState.RECOVERED,
                action_taken=f"Retry {attempt} succeeded: {action_taken}",
                outcome="success",
            )
            incident.resolution_method = f"retry_{attempt}"
        else:
            if attempt == 1:
                incident.transition_to(
                    IncidentState.RETRY_2,
                    action_taken=f"Retry 1 failed: {action_taken}",
                    outcome="failure",
                )
            else:
                # Second failure - escalate
                incident.transition_to(
                    IncidentState.ESCALATED,
                    action_taken=f"Retry 2 failed: {action_taken}",
                    outcome="failure",
                )

        return incident

    def escalate_incident(
        self,
        incident: Incident,
        human_decision: str,
    ) -> Incident:
        """
        Escalate incident for human intervention.

        Args:
            incident: Incident to escalate
            human_decision: Human decision for resolution

        Returns:
            Updated Incident
        """
        incident.transition_to(
            IncidentState.ESCALATED,
            action_taken=f"Escalated to {incident.escalation_target}",
            outcome=f"Human decision: {human_decision}",
        )
        return incident

    def resolve_incident(
        self,
        incident: Incident,
        root_cause: str,
        resolution_method: str,
    ) -> Incident:
        """
        Resolve an incident.

        Args:
            incident: Incident to resolve
            root_cause: Root cause of incident
            resolution_method: How incident was resolved

        Returns:
            Updated Incident
        """
        incident.root_cause = root_cause
        incident.resolution_method = resolution_method
        incident.transition_to(
            IncidentState.RECOVERED,
            action_taken="Incident resolved",
            outcome="resolved",
        )

        # Cooldown before returning to HEALTHY
        return incident

    def return_to_healthy(self, incident: Incident) -> Incident:
        """
        Return incident to HEALTHY state after cooldown.

        Args:
            incident: Incident to return to healthy

        Returns:
            Updated Incident
        """
        incident.transition_to(
            IncidentState.HEALTHY,
            action_taken="Cooldown complete",
            outcome="healthy",
        )
        return incident

    def get_incident(self, incident_id: str) -> Incident | None:
        """Get incident by ID."""
        return self._incidents.get(incident_id)

    def get_active_incidents(self) -> list[Incident]:
        """Get all active (non-recovered) incidents."""
        return [
            i for i in self._incidents.values()
            if i.state not in (IncidentState.RECOVERED, IncidentState.HEALTHY)
        ]

    def get_incidents_by_severity(
        self, severity: IncidentSeverity
    ) -> list[Incident]:
        """Get incidents by severity."""
        return [i for i in self._incidents.values() if i.severity == severity]

    def get_sla_breached_incidents(self) -> list[Incident]:
        """Get incidents that have breached SLA."""
        return [i for i in self._incidents.values() if i.is_sla_breached()]

    def get_incident_summary(self) -> dict[str, Any]:
        """Get incident summary."""
        return {
            "total_incidents": len(self._incidents),
            "active_incidents": len(self.get_active_incidents()),
            "s1_incidents": len(self.get_incidents_by_severity(IncidentSeverity.S1_CRITICAL)),
            "s2_incidents": len(self.get_incidents_by_severity(IncidentSeverity.S2_HIGH)),
            "sla_breached": len(self.get_sla_breached_incidents()),
            "incidents": [i.to_dict() for i in self._incidents.values()],
        }
