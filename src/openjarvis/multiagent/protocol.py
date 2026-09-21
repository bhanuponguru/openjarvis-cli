"""Typed messaging protocol for inter-agent communication in OpenJarvis MAS."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class BaseAgentMessage:
    """Base class for all inter-agent messages."""

    sender_id: str
    recipient_id: str
    message_id: str = field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:8]}")
    created_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TaskAssignmentMessage(BaseAgentMessage):
    """Parent to Child initial mission assignment or delegation."""

    task: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    role: str = "generalist"


@dataclass
class FindingsReportMessage(BaseAgentMessage):
    """Agent reporting significant findings to connected neighbors."""

    summary: str = ""
    details: str | dict[str, Any] | None = None


@dataclass
class AgentExitNotification(BaseAgentMessage):
    """Notification emitted when an agent completes its mission and exits."""

    summary: str = ""
    artifact: dict[str, Any] = field(default_factory=dict)


@dataclass
class TopologyUpdateMessage(BaseAgentMessage):
    """Notification informing an agent of newly connected neighbors."""

    new_neighbors: list[str] = field(default_factory=list)
