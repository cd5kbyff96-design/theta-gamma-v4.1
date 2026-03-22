"""
External module — Pilot SOW templates and validation.

This module implements external-facing templates for pilot engagements
and validation checklists.
"""

from theta_gamma.external.pilot import (
    PilotSOW,
    PilotSuccessCriteria,
    PilotDeliverable,
    PilotPhase,
)
from theta_gamma.external.validation import (
    ValidationChecklist,
    ValidationEvidence,
    PartnerReadiness,
)

__all__ = [
    # Pilot
    "PilotSOW",
    "PilotSuccessCriteria",
    "PilotDeliverable",
    "PilotPhase",
    # Validation
    "ValidationChecklist",
    "ValidationEvidence",
    "PartnerReadiness",
]
