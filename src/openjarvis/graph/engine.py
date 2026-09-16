"""Directed Cognitive Graph Execution Engine for OpenJarvis.

Orchestrates execution of the heterogeneous cognitive graph:
Orchestrator <-> Coder <-> Act / Reasoning specialists,
coordinating over the State Blackboard and typed message protocol.
"""

from __future__ import annotations

import json
from collections.abc import Callable

from pydantic import BaseModel

from openjarvis.builtin_tools.editor_tools import str_replace_editor
from openjarvis.tools import ToolRegistry

from .blackboard import StateBlackboard
from .protocol import (
    ActDirectiveMessage,
    ActObservationMessage,
    CodeDirectiveMessage,
    CodeProposalMessage,
    StrReplaceCommand,
    TaskCompleteMessage,
)


class CognitiveGraphEngine:
    """Execution engine coordinating the heterogeneous cognitive graph."""

    def __init__(
        self,
        invoker: Callable[[str, list[dict[str, str]]], str] | None = None,
        tool_registry: ToolRegistry | None = None,
        max_iterations: int = 25,
        orchestrator_model: str = "orchestrator",
        coder_model: str = "coder",
    ):
        """Args:
            invoker: Callable taking (model_name, prompt_messages) and returning model response string.
            tool_registry: Optional ToolRegistry for executing actions and tool commands.
            max_iterations: Maximum cognitive graph cycles before aborting.
            orchestrator_model: Model name/identifier for the orchestrator role.
            coder_model: Model name/identifier for the coder specialist role.
        """
        self.invoker = invoker
        self.tool_registry = tool_registry
        self.max_iterations = max_iterations
        self.orchestrator_model = orchestrator_model
        self.coder_model = coder_model

    def run_tool_command(self, cmd: StrReplaceCommand) -> str:
        """Execute a StrReplaceCommand against the native editor tool."""
        return str_replace_editor(
            command=cmd.command,
            path=cmd.path,
            file_text=cmd.file_text,
            old_str=cmd.old_str,
            new_str=cmd.new_str,
            insert_line=cmd.insert_line,
            view_range=cmd.view_range,
        )

    def execute_directive(
        self, blackboard: StateBlackboard, directive: ActDirectiveMessage
    ) -> ActObservationMessage:
        """Execute an ActDirectiveMessage using registered tools."""
        if directive.tool_name == "str_replace_editor":
            params = directive.parameters
            cmd = StrReplaceCommand(
                command=params.get("command", "view"),
                path=params.get("path", ""),
                file_text=params.get("file_text"),
                old_str=params.get("old_str"),
                new_str=params.get("new_str"),
                insert_line=params.get("insert_line"),
                view_range=params.get("view_range"),
            )
            output = self.run_tool_command(cmd)
            obs = ActObservationMessage(
                task_id=directive.task_id,
                tool_name=directive.tool_name,
                output=output,
                success=not output.startswith("Error:"),
                error=output if output.startswith("Error:") else None,
            )
        elif self.tool_registry and directive.tool_name in self.tool_registry._tools:
            try:
                res = self.tool_registry.execute({
                    "name": directive.tool_name,
                    "arguments": directive.parameters,
                })
                output = str(res)
                obs = ActObservationMessage(
                    task_id=directive.task_id,
                    tool_name=directive.tool_name,
                    output=output,
                    success=True,
                )
            except Exception as e:
                obs = ActObservationMessage(
                    task_id=directive.task_id,
                    tool_name=directive.tool_name,
                    output=f"Error: {e}",
                    success=False,
                    error=str(e),
                )
        else:
            obs = ActObservationMessage(
                task_id=directive.task_id,
                tool_name=directive.tool_name,
                output=f"Error: Tool '{directive.tool_name}' not found.",
                success=False,
                error="ToolNotFound",
            )

        blackboard.record_message(obs)
        return obs

    def step(self, blackboard: StateBlackboard) -> BaseModel:
        """Run a single step of the cognitive graph based on current blackboard state."""
        if self.invoker is None:
            raise RuntimeError("Cannot step cognitive graph without a configured model invoker.")

        # 1. Orchestrator inspects blackboard
        orch_view = blackboard.get_orchestrator_view()
        prompt = [
            {
                "role": "system",
                "content": (
                    "You are the OpenJarvis Orchestrator. "
                    "Analyze state and return JSON with 'action' ('code', 'act', 'complete') and 'payload'."
                ),
            },
            {"role": "user", "content": json.dumps(orch_view)},
        ]

        response = self.invoker(self.orchestrator_model, prompt)
        try:
            parsed = json.loads(response)
        except Exception:
            # Fallback if raw text returned
            parsed = {"action": "complete", "payload": {"summary": response}}

        action = parsed.get("action")
        payload = parsed.get("payload", {})

        if action == "code":
            directive = CodeDirectiveMessage(
                task_id=blackboard.task.task_id,
                directive=payload.get("directive", ""),
                target_files=payload.get("target_files", []),
                constraints=payload.get("constraints", []),
                iteration=blackboard.iteration,
            )
            blackboard.record_message(directive)

            # Invoke Coder
            coder_view = blackboard.get_specialist_view("coder")
            coder_prompt = [
                {
                    "role": "system",
                    "content": "You are the OpenJarvis Coder specialist. Propose code modifications and tool calls.",
                },
                {"role": "user", "content": json.dumps(coder_view)},
            ]
            coder_resp = self.invoker(self.coder_model, coder_prompt)
            try:
                c_parsed = json.loads(coder_resp)
                tool_calls = [
                    StrReplaceCommand(**tc) for tc in c_parsed.get("tool_calls", [])
                ]
                proposal = CodeProposalMessage(
                    task_id=blackboard.task.task_id,
                    explanation=c_parsed.get("explanation", ""),
                    files_touched=c_parsed.get("files_touched", []),
                    diff=c_parsed.get("diff"),
                    tool_calls=tool_calls,
                    status=c_parsed.get("status", "proposed"),
                )
            except Exception:
                proposal = CodeProposalMessage(
                    task_id=blackboard.task.task_id,
                    explanation=coder_resp,
                )

            blackboard.record_message(proposal)

            # Auto-execute proposed editor tool calls
            for tc in proposal.tool_calls:
                out = self.run_tool_command(tc)
                obs = ActObservationMessage(
                    task_id=blackboard.task.task_id,
                    tool_name="str_replace_editor",
                    output=out,
                    success=not out.startswith("Error:"),
                )
                blackboard.record_message(obs)

            return proposal

        elif action == "act":
            act_directive = ActDirectiveMessage(
                task_id=blackboard.task.task_id,
                tool_name=payload.get("tool_name", ""),
                parameters=payload.get("parameters", {}),
                rationale=payload.get("rationale", ""),
            )
            blackboard.record_message(act_directive)
            return self.execute_directive(blackboard, act_directive)

        else:
            completion = TaskCompleteMessage(
                task_id=blackboard.task.task_id,
                summary=payload.get("summary", "Task completed."),
                resolution_status=payload.get("resolution_status", "completed"),
            )
            blackboard.record_message(completion)
            return completion

