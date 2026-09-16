"""Typed JSON message protocol for the OpenJarvis Cognitive Graph.

Defines the message contracts exchanged between Orchestrator, Coder,
Reasoning, and Action specialist nodes in the execution graph.
Zero torch or neural model dependencies.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TaskInitMessage(BaseModel):
    """Initial user goal and environment context dispatched to the cognitive graph."""

    task_id: str
    goal: str
    context_files: list[str] = Field(default_factory=list)
    system_instructions: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class StrReplaceCommand(BaseModel):
    """Tool invocation command matching the SWE benchmark and Open-SWE-Traces format."""

    command: Literal["view", "create", "str_replace", "insert", "undo_edit"]
    path: str
    file_text: str | None = None
    old_str: str | None = None
    new_str: str | None = None
    insert_line: int | None = None
    view_range: list[int] | None = None


class CodeDirectiveMessage(BaseModel):
    """Directive sent from Orchestrator/Reasoning node to Coder specialist."""

    task_id: str
    directive: str
    target_files: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    iteration: int = 0


class CodeProposalMessage(BaseModel):
    """Code change proposed by Coder specialist."""

    task_id: str
    explanation: str
    files_touched: list[str] = Field(default_factory=list)
    diff: str | None = None
    tool_calls: list[StrReplaceCommand] = Field(default_factory=list)
    status: Literal["proposed", "complete", "need_info"] = "proposed"


class ActDirectiveMessage(BaseModel):
    """Directive sent to Action specialist to execute tools or commands."""

    task_id: str
    tool_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""


class ActObservationMessage(BaseModel):
    """Result of tool execution observed by Action specialist."""

    task_id: str
    tool_name: str
    output: str
    success: bool = True
    error: str | None = None


class TaskCompleteMessage(BaseModel):
    """Terminal state message signaling task completion and synthesis."""

    task_id: str
    summary: str
    resolution_status: Literal["completed", "failed", "aborted"] = "completed"
    artifacts: list[str] = Field(default_factory=list)

