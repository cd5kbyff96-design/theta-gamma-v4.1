"""
Incident Management — Incident records and post-mortems.

This module provides incident record templates and post-mortem management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class IncidentRecord:
    """
    Comprehensive incident record.

    Attributes:
        incident_id: Unique identifier
        created_at: Creation timestamp
        severity: Severity level
        failure_mode_id: Associated failure mode
        owner: Incident owner
        state_transitions: List of state transitions
        resolved_at: Resolution timestamp
        root_cause: Root cause analysis
        prevention_action: Actions to prevent recurrence
    """

    incident_id: str
    created_at: datetime
    severity: str
    failure_mode_id: str
    owner: str
    state_transitions: list[dict[str, Any]] = field(default_factory=list)
    resolved_at: datetime | None = None
    root_cause: str = ""
    prevention_action: str = ""
    impact: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "incident_id": self.incident_id,
            "created_at": self.created_at.isoformat(),
            "severity": self.severity,
            "failure_mode_id": self.failure_mode_id,
            "owner": self.owner,
            "state_transitions": self.state_transitions,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "root_cause": self.root_cause,
            "prevention_action": self.prevention_action,
            "impact": self.impact,
        }


@dataclass
class PostMortem:
    """
    Post-mortem document for significant incidents.

    Attributes:
        post_mortem_id: Unique identifier
        incident_id: Associated incident
        conducted_at: When post-mortem was conducted
        participants: List of participants
        timeline: Incident timeline
        root_cause: Root cause analysis
        action_items: Follow-up action items
    """

    post_mortem_id: str
    incident_id: str
    conducted_at: datetime
    participants: list[str] = field(default_factory=list)
    timeline: list[dict[str, Any]] = field(default_factory=list)
    root_cause: str = ""
    what_happened: str = ""
    what_went_well: list[str] = field(default_factory=list)
    what_went_poorly: list[str] = field(default_factory=list)
    action_items: list[dict[str, Any]] = field(default_factory=list)

    def add_action_item(
        self,
        action: str,
        owner: str,
        due_date: datetime,
        ticket_id: str = "",
    ) -> None:
        """Add an action item."""
        self.action_items.append({
            "action": action,
            "owner": owner,
            "due_date": due_date.isoformat(),
            "ticket_id": ticket_id,
            "status": "open",
        })

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "post_mortem_id": self.post_mortem_id,
            "incident_id": self.incident_id,
            "conducted_at": self.conducted_at.isoformat(),
            "participants": self.participants,
            "timeline": self.timeline,
            "root_cause": self.root_cause,
            "what_happened": self.what_happened,
            "what_went_well": self.what_went_well,
            "what_went_poorly": self.what_went_poorly,
            "action_items": self.action_items,
        }


class IncidentManager:
    """
    Manager for incident records and post-mortems.

    Provides incident creation, tracking, and post-mortem generation.
    """

    def __init__(self) -> None:
        """Initialize the incident manager."""
        self._incidents: dict[str, IncidentRecord] = {}
        self._post_mortems: dict[str, PostMortem] = {}

    def create_incident(
        self,
        severity: str,
        failure_mode_id: str,
        owner: str,
    ) -> IncidentRecord:
        """Create a new incident record."""
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{len(self._incidents) + 1:03d}"

        incident = IncidentRecord(
            incident_id=incident_id,
            created_at=datetime.now(),
            severity=severity,
            failure_mode_id=failure_mode_id,
            owner=owner,
        )

        self._incidents[incident_id] = incident
        return incident

    def add_state_transition(
        self,
        incident_id: str,
        state: str,
        action: str,
        outcome: str,
    ) -> None:
        """Add a state transition to an incident."""
        incident = self._incidents.get(incident_id)
        if incident:
            incident.state_transitions.append({
                "state": state,
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "outcome": outcome,
            })

    def resolve_incident(
        self,
        incident_id: str,
        root_cause: str,
        prevention_action: str,
        impact: dict[str, Any] | None = None,
    ) -> None:
        """Resolve an incident."""
        incident = self._incidents.get(incident_id)
        if incident:
            incident.resolved_at = datetime.now()
            incident.root_cause = root_cause
            incident.prevention_action = prevention_action
            if impact:
                incident.impact = impact

    def create_post_mortem(
        self,
        incident_id: str,
        participants: list[str],
    ) -> PostMortem:
        """Create a post-mortem for an incident."""
        post_mortem_id = f"PM-{datetime.now().strftime('%Y%m%d')}-{len(self._post_mortems) + 1:03d}"

        post_mortem = PostMortem(
            post_mortem_id=post_mortem_id,
            incident_id=incident_id,
            conducted_at=datetime.now(),
            participants=participants,
        )

        self._post_mortems[post_mortem_id] = post_mortem
        return post_mortem

    def get_incident(self, incident_id: str) -> IncidentRecord | None:
        """Get incident by ID."""
        return self._incidents.get(incident_id)

    def get_post_mortem(self, post_mortem_id: str) -> PostMortem | None:
        """Get post-mortem by ID."""
        return self._post_mortems.get(post_mortem_id)

    def get_all_incidents(self) -> list[IncidentRecord]:
        """Get all incidents."""
        return list(self._incidents.values())

    def get_open_incidents(self) -> list[IncidentRecord]:
        """Get all open (unresolved) incidents."""
        return [i for i in self._incidents.values() if i.resolved_at is None]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "incidents": [i.to_dict() for i in self._incidents.values()],
            "post_mortems": [p.to_dict() for p in self._post_mortems.values()],
        }
