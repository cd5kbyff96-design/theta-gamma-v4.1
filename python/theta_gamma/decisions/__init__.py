"""
Decisions module — Decision packets, deadline policies, and delivery.

This module implements the weekly decision packet system that batches
human decisions with automatic defaults and multi-channel delivery.
"""

from theta_gamma.decisions.packets import (
    DecisionPacket,
    Decision,
    DecisionOption,
    DecisionStatus,
    DecisionImpact,
    DecisionUrgency,
    DecisionPacketGenerator,
)
from theta_gamma.decisions.deadlines import (
    DeadlinePolicy,
    DecisionType,
    StandardDeadlines,
)
from theta_gamma.decisions.delivery import (
    DecisionPacketDelivery,
    DeliveryChannel,
    DeliveryStatus,
    DeliveryRecipient,
    DeliveryResult,
    DeliveryNotification,
)

__all__ = [
    # Packets
    "DecisionPacket",
    "Decision",
    "DecisionOption",
    "DecisionStatus",
    "DecisionImpact",
    "DecisionUrgency",
    "DecisionPacketGenerator",
    # Deadlines
    "DeadlinePolicy",
    "DecisionType",
    "StandardDeadlines",
    # Delivery
    "DecisionPacketDelivery",
    "DeliveryChannel",
    "DeliveryStatus",
    "DeliveryRecipient",
    "DeliveryResult",
    "DeliveryNotification",
]
