"""State Blackboard for OpenJarvis Cognitive Graph.

Maintains shared global state across all cognitive graph nodes, performs
active context management (pruning/compacting history so sequences stay well
within the native 8,192 context window and under 1,500 for orchestrator),
and tracks execution cycles to prevent loops.
"""

from __future__ import annotations

import hashlib
from typing import Any

from pydantic import BaseModel, Field

from .protocol import (
    ActDirectiveMessage,
    ActObservationMessage,
    CodeDirectiveMessage,
    CodeProposalMessage,
    TaskInitMessage,
)


class CycleDetectedError(RuntimeError):
    """Raised when an identical directive or action is repeated >= 3 times."""


class StateBlackboard(BaseModel):
    """Shared state container for graph node execution."""

    task: TaskInitMessage
    messages: list[BaseModel] = Field(default_factory=list)
    modified_files: dict[str, str] = Field(default_factory=dict)
    iteration: int = 0
    max_context_tokens: int = 6000
    orchestrator_max_tokens: int = 1500
    action_hashes: list[str] = Field(default_factory=list)

    def record_message(self, message: BaseModel) -> None:
        """Append a message to the blackboard and check for execution cycles."""
        self.messages.append(message)
        self.iteration += 1

        # Cycle detection on directives and actions
        if isinstance(message, (ActDirectiveMessage, CodeDirectiveMessage)):
            msg_repr = message.model_dump_json()
            h = hashlib.sha256(msg_repr.encode("utf-8")).hexdigest()
            self.action_hashes.append(h)
            # Check if this exact action appeared >= 3 times
            if self.action_hashes.count(h) >= 3:
                raise CycleDetectedError(
                    f"Graph cycle detected: directive repeated 3 times: {message}"
                )

    def record_file_change(self, file_path: str, content_or_diff: str) -> None:
        """Track file modifications across iterations."""
        self.modified_files[file_path] = content_or_diff

    def get_orchestrator_view(self) -> dict[str, Any]:
        """Generate a concise, compacted view tailored for the 300M Orchestrator (<1,500 tokens)."""
        recent_events: list[dict[str, Any]] = []

        # Keep initial goal and last 5 interactions, compacting observations
        for msg in self.messages[-6:]:
            if isinstance(msg, ActObservationMessage):
                output_lines = msg.output.splitlines()
                if len(output_lines) > 10:
                    compacted = "\n".join(output_lines[:4] + [f"... [{len(output_lines) - 8} lines omitted] ..."] + output_lines[-4:])
                else:
                    compacted = msg.output
                recent_events.append({
                    "type": "observation",
                    "tool": msg.tool_name,
                    "success": msg.success,
                    "output": compacted,
                })
            elif isinstance(msg, CodeProposalMessage):
                recent_events.append({
                    "type": "code_proposal",
                    "explanation": msg.explanation,
                    "files": msg.files_touched,
                    "status": msg.status,
                })
            elif isinstance(msg, (CodeDirectiveMessage, ActDirectiveMessage)):
                recent_events.append({
                    "type": "directive",
                    "content": msg.model_dump(),
                })

        return {
            "task_id": self.task.task_id,
            "goal": self.task.goal,
            "modified_files": list(self.modified_files.keys()),
            "iteration": self.iteration,
            "history": recent_events,
        }

    def get_specialist_view(self, specialist_type: str) -> dict[str, Any]:
        """Generate full context view for domain specialists (Coder/Act/Reasoning) within 8k."""
        events: list[dict[str, Any]] = []
        for msg in self.messages:
            if isinstance(msg, ActObservationMessage):
                # Head and tail observation compaction
                output_lines = msg.output.splitlines()
                if len(output_lines) > 60:
                    compacted = "\n".join(output_lines[:25] + [f"... [{len(output_lines) - 50} lines compacted] ..."] + output_lines[-25:])
                else:
                    compacted = msg.output
                events.append({
                    "type": "observation",
                    "tool": msg.tool_name,
                    "success": msg.success,
                    "output": compacted,
                })
            else:
                events.append({
                    "type": msg.__class__.__name__,
                    "data": msg.model_dump(),
                })

        return {
            "task_id": self.task.task_id,
            "goal": self.task.goal,
            "specialist": specialist_type,
            "modified_files": self.modified_files,
            "events": events,
        }

