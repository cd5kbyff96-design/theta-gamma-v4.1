"""
Validation — Validation checklists and evidence tracking.

This module provides validation checklists for pilot readiness
and evidence tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ValidationEvidence:
    """
    Validation evidence item.

    Attributes:
        id: Evidence identifier
        description: Evidence description
        artifact_path: Path to evidence artifact
        verified: Whether evidence is verified
        verified_at: Verification timestamp
    """

    id: str
    description: str
    artifact_path: str
    verified: bool = False
    verified_at: datetime | None = None

    def mark_verified(self) -> None:
        """Mark evidence as verified."""
        self.verified = True
        self.verified_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "artifact_path": self.artifact_path,
            "verified": self.verified,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
        }


@dataclass
class ValidationChecklist:
    """
    Validation checklist.

    Attributes:
        checklist_id: Checklist identifier
        name: Checklist name
        items: Checklist items
    """

    checklist_id: str
    name: str
    items: list[dict[str, Any]] = field(default_factory=list)

    def add_item(
        self,
        item_id: str,
        description: str,
        required: bool = True,
        evidence_required: bool = True,
    ) -> None:
        """Add a checklist item."""
        self.items.append({
            "id": item_id,
            "description": description,
            "required": required,
            "evidence_required": evidence_required,
            "completed": False,
            "evidence": [],
        })

    def complete_item(self, item_id: str, evidence: list[ValidationEvidence]) -> None:
        """Mark an item as complete with evidence."""
        for item in self.items:
            if item["id"] == item_id:
                item["completed"] = True
                item["evidence"] = [e.to_dict() for e in evidence]
                break

    def get_completion_status(self) -> dict[str, Any]:
        """Get checklist completion status."""
        total = len(self.items)
        required = [i for i in self.items if i["required"]]
        completed = [i for i in self.items if i["completed"]]
        required_completed = [i for i in required if i["completed"]]

        return {
            "checklist_id": self.checklist_id,
            "name": self.name,
            "total_items": total,
            "completed_items": len(completed),
            "required_items": len(required),
            "required_completed": len(required_completed),
            "completion_pct": (len(completed) / total * 100) if total > 0 else 0,
            "required_completion_pct": (len(required_completed) / len(required) * 100) if required else 0,
            "is_complete": len(required_completed) == len(required),
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "checklist_id": self.checklist_id,
            "name": self.name,
            "status": self.get_completion_status(),
            "items": self.items,
        }


class PartnerReadiness:
    """
    Partner readiness assessment.

    Tracks partner readiness across multiple dimensions.
    """

    def __init__(self, partner_name: str) -> None:
        """
        Initialize partner readiness.

        Args:
            partner_name: Partner organization name
        """
        self.partner_name = partner_name
        self._checklists: dict[str, ValidationChecklist] = {}
        self._evidence: dict[str, ValidationEvidence] = {}

        self._initialize_checklists()

    def _initialize_checklists(self) -> None:
        """Initialize default checklists."""
        # Data Access Checklist
        data_checklist = ValidationChecklist(
            checklist_id="CHK-DATA-001",
            name="Data Access Readiness",
        )
        data_checklist.add_item("DATA-01", "Data sharing agreement executed", required=True)
        data_checklist.add_item("DATA-02", "Data transfer mechanism established", required=True)
        data_checklist.add_item("DATA-03", "Data format specifications agreed", required=True)
        data_checklist.add_item("DATA-04", "Sample data received and validated", required=True)
        self._checklists["data"] = data_checklist

        # Technical Integration Checklist
        tech_checklist = ValidationChecklist(
            checklist_id="CHK-TECH-001",
            name="Technical Integration Readiness",
        )
        tech_checklist.add_item("TECH-01", "API credentials provisioned", required=True)
        tech_checklist.add_item("TECH-02", "Network connectivity verified", required=True)
        tech_checklist.add_item("TECH-03", "Authentication flow tested", required=True)
        tech_checklist.add_item("TECH-04", "Error handling implemented", required=True)
        tech_checklist.add_item("TECH-05", "Monitoring/logging configured", required=False)
        self._checklists["technical"] = tech_checklist

        # Operational Readiness Checklist
        ops_checklist = ValidationChecklist(
            checklist_id="CHK-OPS-001",
            name="Operational Readiness",
        )
        ops_checklist.add_item("OPS-01", "Point of contact designated", required=True)
        ops_checklist.add_item("OPS-02", "Escalation path defined", required=True)
        ops_checklist.add_item("OPS-03", "Communication channels established", required=True)
        ops_checklist.add_item("OPS-04", "Weekly sync scheduled", required=True)
        self._checklists["operational"] = ops_checklist

    def get_checklist(self, checklist_type: str) -> ValidationChecklist | None:
        """Get a checklist by type."""
        return self._checklists.get(checklist_type)

    def get_all_checklists(self) -> dict[str, ValidationChecklist]:
        """Get all checklists."""
        return self._checklists.copy()

    def get_overall_readiness(self) -> dict[str, Any]:
        """Get overall readiness assessment."""
        statuses = [
            checklist.get_completion_status()
            for checklist in self._checklists.values()
        ]

        total_required = sum(s["required_items"] for s in statuses)
        total_required_completed = sum(s["required_completed"] for s in statuses)

        readiness_pct = (
            (total_required_completed / total_required * 100)
            if total_required > 0
            else 0
        )

        is_ready = all(s["is_complete"] for s in statuses)

        return {
            "partner_name": self.partner_name,
            "assessed_at": datetime.now().isoformat(),
            "overall_readiness_pct": readiness_pct,
            "is_ready_for_pilot": is_ready,
            "checklists": statuses,
        }

    def add_evidence(self, evidence: ValidationEvidence) -> None:
        """Add evidence."""
        self._evidence[evidence.id] = evidence

    def get_evidence(self, evidence_id: str) -> ValidationEvidence | None:
        """Get evidence by ID."""
        return self._evidence.get(evidence_id)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "partner_name": self.partner_name,
            "overall_readiness": self.get_overall_readiness(),
            "checklists": {
                k: v.to_dict() for k, v in self._checklists.items()
            },
            "evidence_count": len(self._evidence),
        }
