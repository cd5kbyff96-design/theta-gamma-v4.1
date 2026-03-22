"""
Recovery module — State machine for failure recovery and incident management.

This module implements the recovery state machine that handles
failure detection, retry logic, and escalation.
"""

from theta_gamma.recovery.state_machine import (
    RecoveryStateMachine,
    IncidentState,
    Incident,
    IncidentSeverity,
    FailureModeRegistry,
)
from theta_gamma.recovery.incidents import (
    IncidentManager,
    IncidentRecord,
    PostMortem,
)

__all__ = [
    # State Machine
    "RecoveryStateMachine",
    "IncidentState",
    "Incident",
    "IncidentSeverity",
    "FailureModeRegistry",
    # Incidents
    "IncidentManager",
    "IncidentRecord",
    "PostMortem",
]
