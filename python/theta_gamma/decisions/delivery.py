"""
Decision Packet Delivery — Notification system for decision packets.

This module implements delivery of decision packets via multiple channels:
- Dashboard notifications
- Email digests
- Slack messages

Per A7 specification, decisions are delivered Monday 09:35 UTC with
Tuesday 18:00 UTC deadline.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Protocol


class DeliveryChannel(str, Enum):
    """Delivery channels for decision packets."""

    DASHBOARD = "dashboard"
    EMAIL = "email"
    SLACK = "slack"
    FILE = "file"


class DeliveryStatus(str, Enum):
    """Delivery status for notifications."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


@dataclass
class DeliveryRecipient:
    """
    Notification recipient.

    Attributes:
        name: Recipient name
        email: Email address (for email channel)
        slack_id: Slack user/channel ID (for Slack channel)
        role: Recipient role (e.g., "tech_lead", "budget_owner")
    """

    name: str
    email: str = ""
    slack_id: str = ""
    role: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "email": self.email,
            "slack_id": self.slack_id,
            "role": self.role,
        }


@dataclass
class DeliveryNotification:
    """
    A delivery notification record.

    Attributes:
        channel: Delivery channel used
        recipient: Notification recipient
        status: Delivery status
        sent_at: Send timestamp
        delivered_at: Delivery confirmation timestamp
        error: Error message if failed
    """

    channel: DeliveryChannel
    recipient: DeliveryRecipient
    status: DeliveryStatus = DeliveryStatus.PENDING
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "channel": self.channel.value,
            "recipient": self.recipient.to_dict(),
            "status": self.status.value,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "error": self.error,
        }


@dataclass
class DeliveryResult:
    """
    Result of packet delivery.

    Attributes:
        packet_id: Decision packet ID
        delivered_at: Delivery timestamp
        notifications: List of delivery notifications
        success: Whether all deliveries succeeded
        response_deadline: Response deadline
    """

    packet_id: str
    delivered_at: datetime
    notifications: list[DeliveryNotification] = field(default_factory=list)
    success: bool = True
    response_deadline: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "packet_id": self.packet_id,
            "delivered_at": self.delivered_at.isoformat(),
            "notifications": [n.to_dict() for n in self.notifications],
            "success": self.success,
            "response_deadline": self.response_deadline.isoformat() if self.response_deadline else None,
        }


class NotificationSender(Protocol):
    """Protocol for notification senders."""

    def send(self, subject: str, body: str, recipient: DeliveryRecipient) -> bool:
        """Send notification. Returns True if successful."""
        ...


class DashboardSender:
    """Dashboard notification sender."""

    def __init__(self, dashboard_dir: Path | None = None) -> None:
        """Initialize dashboard sender."""
        self._dashboard_dir = dashboard_dir or Path("dashboard/notifications")
        self._notifications: list[dict[str, Any]] = []

    def send(self, subject: str, body: str, recipient: DeliveryRecipient) -> bool:
        """Send dashboard notification."""
        notification = {
            "type": "decision_packet",
            "subject": subject,
            "body": body,
            "recipient": recipient.to_dict(),
            "timestamp": datetime.now().isoformat(),
            "read": False,
        }
        self._notifications.append(notification)

        # In production, would update dashboard database
        return True

    def get_notifications(self) -> list[dict[str, Any]]:
        """Get all notifications."""
        return self._notifications.copy()


class EmailSender:
    """Email notification sender with SMTP support."""

    def __init__(
        self,
        smtp_host: str = "",
        smtp_port: int = 587,
        username: str = "",
        password: str = "",
        from_email: str = "",
    ) -> None:
        """Initialize email sender."""
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._username = username
        self._password = password
        self._from_email = from_email
        self._sent_count = 0

    def send(self, subject: str, body: str, recipient: DeliveryRecipient) -> bool:
        """Send email notification via SMTP."""
        if not recipient.email:
            return False

        if not self._smtp_host:
            # No SMTP configured, simulate success
            self._sent_count += 1
            return True

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg["From"] = self._from_email
            msg["To"] = recipient.email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(self._smtp_host, self._smtp_port)
            server.starttls()
            if self._username and self._password:
                server.login(self._username, self._password)
            server.send_message(msg)
            server.quit()

            self._sent_count += 1
            return True
        except Exception:
            return False


class SlackSender:
    """Slack notification sender with webhook support."""

    def __init__(self, webhook_url: str = "") -> None:
        """Initialize Slack sender."""
        self._webhook_url = webhook_url
        self._sent_count = 0

    def send(self, subject: str, body: str, recipient: DeliveryRecipient) -> bool:
        """Send Slack notification via webhook."""
        if not recipient.slack_id:
            return False

        if not self._webhook_url:
            # No webhook configured, simulate success
            self._sent_count += 1
            return True

        try:
            import urllib.request
            import json

            # Format message for Slack
            message = {
                "channel": recipient.slack_id,
                "username": "Theta-Gamma Bot",
                "icon_emoji": ":robot_face:",
                "text": f"*{subject}*",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{subject}*\n{body[:2000]}...",
                        },
                    },
                ],
            }

            data = json.dumps(message).encode("utf-8")
            req = urllib.request.Request(
                self._webhook_url,
                data=data,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req)

            self._sent_count += 1
            return True
        except Exception:
            return False


class FileSender:
    """File-based notification sender (for testing/archiving)."""

    def __init__(self, output_dir: Path) -> None:
        """Initialize file sender."""
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def send(self, subject: str, body: str, recipient: DeliveryRecipient) -> bool:
        """Write notification to file."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"decision-{timestamp}.json"
        filepath = self._output_dir / filename

        content = {
            "subject": subject,
            "body": body,
            "recipient": recipient.to_dict(),
            "timestamp": datetime.now().isoformat(),
        }

        with open(filepath, "w") as f:
            json.dump(content, f, indent=2)

        return True


class DecisionPacketDelivery:
    """
    Decision packet delivery service.

    Delivers decision packets via multiple channels and tracks
    delivery status and responses.

    Example:
        >>> delivery = DecisionPacketDelivery()
        >>> result = await delivery.deliver_packet(packet, recipients)
        >>> print(f"Delivered to {len(result.notifications)} recipients")
    """

    def __init__(
        self,
        dashboard_dir: Path | None = None,
        file_output_dir: Path | None = None,
        enable_email: bool = False,
        enable_slack: bool = False,
    ) -> None:
        """
        Initialize the delivery service.

        Args:
            dashboard_dir: Directory for dashboard notifications
            file_output_dir: Directory for file output (archiving)
            enable_email: Enable email delivery
            enable_slack: Enable Slack delivery
        """
        self._dashboard_sender = DashboardSender(dashboard_dir)
        self._file_sender = FileSender(file_output_dir or Path("decisions/archive"))
        self._email_sender = EmailSender() if enable_email else None
        self._slack_sender = SlackSender() if enable_slack else None

        self._delivery_history: list[DeliveryResult] = []
        self._responses: dict[str, dict[str, str]] = {}

    async def deliver_packet(
        self,
        packet: Any,  # DecisionPacket
        recipients: list[DeliveryRecipient],
        deadline_hours: int = 32,
    ) -> DeliveryResult:
        """
        Deliver a decision packet to recipients.

        Args:
            packet: Decision packet to deliver
            recipients: List of recipients
            deadline_hours: Hours until response deadline

        Returns:
            DeliveryResult with delivery status
        """
        delivered_at = datetime.now()
        deadline = delivered_at + timedelta(hours=deadline_hours)
        notifications: list[DeliveryNotification] = []

        # Format packet for delivery
        subject = f"Decision Packet: {packet.week} — {len(packet.decisions)} decisions require input"
        body = self._format_packet_body(packet)

        # Deliver to each recipient via their preferred channel
        for recipient in recipients:
            # Dashboard (always)
            dash_notif = await self._send_to_channel(
                DeliveryChannel.DASHBOARD,
                subject,
                body,
                recipient,
            )
            notifications.append(dash_notif)

            # Email (if configured and recipient has email)
            if self._email_sender and recipient.email:
                email_notif = await self._send_to_channel(
                    DeliveryChannel.EMAIL,
                    subject,
                    body,
                    recipient,
                )
                notifications.append(email_notif)

            # Slack (if configured and recipient has slack_id)
            if self._slack_sender and recipient.slack_id:
                slack_notif = await self._send_to_channel(
                    DeliveryChannel.SLACK,
                    subject,
                    body,
                    recipient,
                )
                notifications.append(slack_notif)

            # File archive (always)
            file_notif = await self._send_to_channel(
                DeliveryChannel.FILE,
                subject,
                body,
                recipient,
            )
            notifications.append(file_notif)

        # Check if all deliveries succeeded
        success = all(n.status == DeliveryStatus.SENT for n in notifications)

        result = DeliveryResult(
            packet_id=packet.packet_id,
            delivered_at=delivered_at,
            notifications=notifications,
            success=success,
            response_deadline=deadline,
        )

        self._delivery_history.append(result)
        return result

    async def _send_to_channel(
        self,
        channel: DeliveryChannel,
        subject: str,
        body: str,
        recipient: DeliveryRecipient,
    ) -> DeliveryNotification:
        """Send notification to a specific channel."""
        notification = DeliveryNotification(
            channel=channel,
            recipient=recipient,
        )

        sender = self._get_sender(channel)
        if not sender:
            notification.status = DeliveryStatus.FAILED
            notification.error = f"Channel {channel.value} not configured"
            return notification

        try:
            success = sender.send(subject, body, recipient)
            if success:
                notification.status = DeliveryStatus.SENT
                notification.sent_at = datetime.now()
            else:
                notification.status = DeliveryStatus.FAILED
                notification.error = "Send failed"
        except Exception as e:
            notification.status = DeliveryStatus.FAILED
            notification.error = str(e)

        return notification

    def _get_sender(self, channel: DeliveryChannel) -> NotificationSender | None:
        """Get sender for channel."""
        if channel == DeliveryChannel.DASHBOARD:
            return self._dashboard_sender
        elif channel == DeliveryChannel.EMAIL:
            return self._email_sender
        elif channel == DeliveryChannel.SLACK:
            return self._slack_sender
        elif channel == DeliveryChannel.FILE:
            return self._file_sender
        return None

    def _format_packet_body(self, packet: Any) -> str:
        """Format decision packet for delivery."""
        lines = [
            f"**Decision Packet: {packet.week}**",
            f"Generated: {packet.generated_at.strftime('%Y-%m-%d %H:%M UTC')}",
            f"Deadline: {packet.deadline.strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            f"**{len(packet.decisions)} decisions require your input**",
            "",
        ]

        for i, decision in enumerate(packet.decisions, 1):
            lines.append(f"**{i}. {decision.title}**")
            lines.append(f"   Impact: {decision.impact.name} | Urgency: {decision.urgency.name}")
            lines.append(f"   Score: {decision.score}")
            lines.append(f"   Context: {decision.context[:200]}...")
            lines.append("")
            lines.append("   Options:")
            for option in decision.options:
                recommended = " (RECOMMENDED)" if option.is_recommended else ""
                lines.append(f"   - {option.label}: {option.description}{recommended}")
            lines.append("")

        if packet.deferred_decisions:
            lines.append(f"**{len(packet.deferred_decisions)} deferred decisions** (will use defaults)")
            lines.append("")

        lines.append("---")
        lines.append("**Response Instructions:**")
        lines.append("Reply with decision numbers and option letters:")
        lines.append("  D1: A, D2: B, D3: A, ...")
        lines.append("")
        lines.append("Or simply reply 'ALL DEFAULTS' to accept all recommendations.")
        lines.append("")
        lines.append("Unanswered decisions will use their recommended default at the deadline.")

        return "\n".join(lines)

    def process_response(
        self,
        packet_id: str,
        responses: dict[str, str],
    ) -> bool:
        """
        Process human response to a decision packet.

        Args:
            packet_id: Decision packet ID
            responses: Dictionary mapping decision_id to option label

        Returns:
            True if response was processed successfully
        """
        self._responses[packet_id] = responses
        return True

    def get_response(self, packet_id: str) -> dict[str, str] | None:
        """Get response for a packet."""
        return self._responses.get(packet_id)

    def get_pending_packets(self) -> list[DeliveryResult]:
        """Get packets awaiting response."""
        now = datetime.now()
        return [
            r for r in self._delivery_history
            if r.response_deadline and r.response_deadline > now and packet_id not in self._responses
            for packet_id in [r.packet_id]
        ]

    def get_overdue_packets(self) -> list[DeliveryResult]:
        """Get overdue packets."""
        now = datetime.now()
        return [
            r for r in self._delivery_history
            if r.response_deadline and r.response_deadline < now and r.packet_id not in self._responses
        ]

    def get_delivery_history(self) -> list[DeliveryResult]:
        """Get delivery history."""
        return self._delivery_history.copy()

    def get_delivery_stats(self) -> dict[str, Any]:
        """Get delivery statistics."""
        total = len(self._delivery_history)
        successful = sum(1 for r in self._delivery_history if r.success)
        responded = sum(1 for r in self._delivery_history if r.packet_id in self._responses)
        overdue = len(self.get_overdue_packets())

        return {
            "total_deliveries": total,
            "successful_deliveries": successful,
            "response_rate": responded / total if total > 0 else 0.0,
            "overdue_packets": overdue,
        }
