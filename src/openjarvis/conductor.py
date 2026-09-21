"""Conductor orchestrator using LangGraph state machine and LangChain chat models."""

from __future__ import annotations

import contextlib
import json
import logging
import re
from collections.abc import Callable, Generator, Iterator
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import END, StateGraph

from openjarvis.config_loader import get_delegation_mask, load_config
from openjarvis.llm_factory import create_chat_model
from openjarvis.model_types import ConductorConfig, SpecialistConfig
from openjarvis.parser import is_route_tag, parse_route_tag
from openjarvis.permissions import PermissionManager
from openjarvis.prompts import build_specialist_prompt
from openjarvis.safety_classifier import SafetyClassifier
from openjarvis.tool_retriever import ToolRetriever
from openjarvis.workspace import Workspace, discover_workspace, set_current_workspace

if TYPE_CHECKING:
    from openjarvis.tools import ToolRegistry

logger = logging.getLogger(__name__)

_TAG_START = re.compile(r"(?:^|(?<=\n))[ \t]*\[[^\n]*$")


def _stream_without_tag(deltas: Iterator[str]) -> Iterator[tuple[str, str]]:
    """Pass deltas through while withholding a possibly-incomplete routing tag."""
    pending = ""
    for delta in deltas:
        pending += delta
        match = _TAG_START.search(pending)
        safe_upto = match.start() if match else len(pending)
        emit, pending = pending[:safe_upto], pending[safe_upto:]

        if pending and "\n" in pending:
            line, rest = pending.split("\n", 1)
            if not is_route_tag(line):
                emit += line + "\n"
            pending = rest

        yield delta, emit

    if pending:
        if is_route_tag(pending) or _TAG_START.search(pending):
            return
        yield "", pending


class ConductorState(TypedDict, total=False):
    """Conversation state manipulated by LangGraph nodes."""

    messages: list[dict]
    current_role: str
    previous_role: str | None
    target_role: str | None
    hops: int
    visited_specialists: list[str]
    last_response: str
    last_tool_calls: list[dict]
    final_output: str
    error: str | None
    events: list[dict]



def _extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                parts.append(str(part["text"]))
        return "".join(parts)
    return str(content or "")


class Conductor:
    """OpenJarvis Conductor — LangGraph state machine routing through specialists."""

    _ROLE_ECHO_RE = re.compile(r"^\[[\w]+\]:\s*")

    def __init__(
        self,
        config_path: str | None = None,
        config: ConductorConfig | None = None,
        tools: ToolRegistry | None = None,
        workspace: Workspace | None = None,
        confirm_callback: Callable[[str, dict[str, Any], str], bool] | None = None,
    ) -> None:
        self.workspace = workspace or discover_workspace()
        set_current_workspace(self.workspace)
        self._tools = tools
        self.confirm_callback = confirm_callback

        if config_path:
            self.config = load_config(config_path, workspace=self.workspace)
        elif config:
            self.config = config
        else:
            self.config = load_config(workspace=self.workspace)

        self.classifier = SafetyClassifier(
            model_dir=self.workspace.global_path("models", "safety-classifier")
        )
        self.permissions = PermissionManager(
            config=self.config.tool_permissions,
            workspace=self.workspace,
            confirm_callback=self.confirm_callback,
            classifier=self.classifier,
        )

        if self._tools:
            self._retriever: ToolRetriever | None = ToolRetriever(
                registry=self._tools,
                config=self.config.tool_retrieval,
                cache_dir=self.workspace.global_path("vectors"),
            )
        else:
            self._retriever = None

        self.history: list[dict] = []
        self._delegation_mask = get_delegation_mask(self.config.specialists)
        self._graph = self._build_graph()

    # ------------------------------------------------------------------
    # Specialist & Model Resolution
    # ------------------------------------------------------------------

    def _get_api_key(self, specialist_name: str) -> str | None:
        import os

        spec = self._get_specialist(specialist_name)
        if spec and spec.api_key_env:
            return os.environ.get(spec.api_key_env)
        return None

    def _get_effective_config(self, spec: SpecialistConfig, is_generalist: bool = False) -> SpecialistConfig:
        prefix_parts: list[str] = []
        if self.workspace:
            inst = self.workspace.instructions()
            if inst:
                prefix_parts.append(f"### Instructions\n{inst}")
            ctx = self.workspace.context()
            if ctx:
                prefix_parts.append(f"### Context\n{ctx}")
        effective_prompt = spec.system_prompt
        if prefix_parts:
            merged_prefix = "\n\n".join(prefix_parts)
            effective_prompt = f"{merged_prefix}\n\n{effective_prompt}"

        templated_prompt = build_specialist_prompt(
            spec=replace(spec, system_prompt=effective_prompt),
            available_specialists=self.config.specialists,
            is_generalist=is_generalist,
        )
        return replace(spec, system_prompt=templated_prompt)

    def _get_specialist(self, name: str) -> SpecialistConfig | None:
        spec: SpecialistConfig | None = None
        is_generalist = False
        if name == "generalist" or name == self.config.generalist.name:
            spec = self.config.generalist
            is_generalist = True
        else:
            spec = self.config.specialists.get(name)
        if spec is None:
            return None
        return self._get_effective_config(spec, is_generalist=is_generalist)

    def _get_chat_model(self, name: str, **kwargs: Any) -> Any:
        spec = self._get_specialist(name)
        if not spec:
            raise ValueError(f"Specialist '{name}' not found")
        api_key = self._get_api_key(name)
        return create_chat_model(spec, api_key=api_key, **kwargs)

    def _strip_role_echo(self, content: str) -> str:
        return self._ROLE_ECHO_RE.sub("", content, count=1)

    def _final_answer_prompt(self) -> str:
        return (
            "[Hop limit reached. Stop routing and answer the user directly using "
            "everything discussed so far. End your reply with [ROUTE: return].]"
        )

    # ------------------------------------------------------------------
    # Message Conversion
    # ------------------------------------------------------------------

    def _format_messages_for_langchain(self, messages_dict: list[dict]) -> list[BaseMessage]:
        """Convert internal dict-based message history to LangChain BaseMessage objects."""
        lc_messages: list[BaseMessage] = []
        for msg in messages_dict:
            role = msg.get("role")
            content = msg.get("content") or ""

            if role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "tool":
                lc_messages.append(
                    ToolMessage(
                        content=content,
                        tool_call_id=msg.get("tool_call_id", ""),
                        name=msg.get("name", ""),
                    )
                )
            elif role == "assistant" and "tool_calls" in msg:
                lc_messages.append(
                    AIMessage(
                        content=content,
                        tool_calls=[
                            {
                                "id": tc.get("id", ""),
                                "name": tc.get("function", {}).get("name", tc.get("name", "")),
                                "args": (
                                    json.loads(tc["function"]["arguments"])
                                    if isinstance(tc.get("function", {}).get("arguments"), str)
                                    else tc.get("function", {}).get("arguments", tc.get("args", {}))
                                ),
                            }
                            for tc in msg["tool_calls"]
                        ],
                    )
                )
            else:
                lc_messages.append(SystemMessage(content=f"(Response from {role} specialist:)"))
                lc_messages.append(AIMessage(content=content))
        return lc_messages

    # ------------------------------------------------------------------
    # LangGraph Node Factories
    # ------------------------------------------------------------------

    def _make_agent_node(self, role_name: str) -> Any:
        """Factory creating a LangGraph node function for a specific agent role."""

        def agent_node(state: ConductorState) -> dict[str, Any]:
            spec = self._get_specialist(role_name)
            if not spec:
                return {
                    **state,
                    "error": f"Unknown role '{role_name}' — no config found.",
                    "target_role": "end",
                }

            events: list[dict] = []
            previous_role = state.get("previous_role")
            if previous_role and previous_role != role_name:
                events.append({"type": "route", "from_role": previous_role, "to_role": role_name})

            messages_history = list(state.get("messages", []))
            lc_messages = self._format_messages_for_langchain(messages_history)
            full_lc_messages: list[BaseMessage] = [SystemMessage(content=spec.system_prompt)] + lc_messages

            # Resolve active tools (applying specialist-level tool permissions)
            active_tools = self._tools
            allowed_tools = spec.tools
            if active_tools is not None and allowed_tools is not None:
                active_tools = active_tools.subset(allowed_tools)

            if (
                active_tools
                and len(active_tools.get_tools()) > 0
                and self.config.tool_retrieval.enabled
                and self._retriever
            ):
                reasoning_prompt = SystemMessage(
                    content=(
                        "Before responding, briefly state your reasoning and whether you need external tools "
                        "(e.g. calculation, file search/editing, web search, memory). "
                        "State the required tools and query parameters."
                    )
                )
                try:
                    base_model = self._get_chat_model(role_name)
                    reasoning_resp = base_model.invoke(full_lc_messages + [reasoning_prompt])
                    reasoning_text = _extract_text(reasoning_resp.content)
                    active_tools = self._retriever.create_retrieved_registry(
                        reasoning_text,
                        allowed_tools=allowed_tools,
                    )
                except Exception as exc:
                    logger.warning("RAG tool retrieval failed, using permitted tools: %s", exc)

            openai_tools = (
                active_tools.to_openai_format()
                if active_tools and len(active_tools.get_tools()) > 0
                else []
            )
            model = self._get_chat_model(role_name)
            if openai_tools:
                with contextlib.suppress(Exception):
                    model = model.bind_tools(openai_tools)

            try:
                response = model.invoke(full_lc_messages)
            except Exception as exc:
                err = f"Error calling {role_name}: {exc}"
                events.append({"type": "error", "content": err})
                return {
                    **state,
                    "error": err,
                    "events": events,
                    "target_role": "end",
                }

            # Check for tool calls
            tool_calls: list[dict] = []
            if hasattr(response, "tool_calls") and response.tool_calls:
                tool_calls = response.tool_calls
            elif hasattr(response, "additional_kwargs") and "tool_calls" in response.additional_kwargs:
                tool_calls = response.additional_kwargs["tool_calls"]

            raw_content = _extract_text(response.content)

            if tool_calls:
                standardized_tool_calls = []
                for tc in tool_calls:
                    tc_id = tc.get("id", "")
                    tc_name = tc.get("name") or tc.get("function", {}).get("name", "")
                    tc_args = tc.get("args") or tc.get("function", {}).get("arguments", {})
                    args_str = json.dumps(tc_args) if isinstance(tc_args, dict) else str(tc_args)
                    standardized_tool_calls.append(
                        {
                            "id": tc_id,
                            "type": "function",
                            "function": {"name": tc_name, "arguments": args_str},
                        }
                    )

                assistant_msg = {
                    "role": "assistant",
                    "content": raw_content,
                    "tool_calls": standardized_tool_calls,
                }
                messages_history.append(assistant_msg)

                return {
                    **state,
                    "messages": messages_history,
                    "current_role": role_name,
                    "previous_role": role_name,
                    "last_tool_calls": standardized_tool_calls,
                    "target_role": "tool_execution",
                    "events": events,
                }

            # No tool calls: parse routing tag
            cleaned_content, route_target = parse_route_tag(raw_content)
            cleaned_content = self._strip_role_echo(cleaned_content)
            new_hops = state.get("hops", 0) + 1

            messages_history.append(
                {
                    "role": role_name,
                    "content": cleaned_content,
                    "route": route_target,
                }
            )

            is_generalist = role_name == "generalist"
            visited = list(state.get("visited_specialists", []))
            if not is_generalist and role_name not in visited:
                visited.append(role_name)

            final_output = ""
            if is_generalist and route_target == "return":
                events.append({"type": "final", "content": cleaned_content, "role": role_name})
                final_output = cleaned_content
            elif is_generalist and route_target == "generalist":
                events.append(
                    {
                        "type": "error",
                        "content": "The generalist routed to itself; treating as a final answer.",
                    }
                )
                events.append({"type": "final", "content": cleaned_content, "role": role_name})
                final_output = cleaned_content
            else:
                events.append({"type": "intermediate", "role": role_name, "content": cleaned_content})

            return {
                **state,
                "messages": messages_history,
                "current_role": role_name,
                "previous_role": role_name,
                "hops": new_hops,
                "visited_specialists": visited,
                "last_response": cleaned_content,
                "final_output": final_output,
                "target_role": route_target,
                "events": events,
            }

        return agent_node

    def _tool_execution_node(self, state: ConductorState) -> ConductorState:
        """Execute tool calls with security permissions and return to calling agent."""
        tool_calls = state.get("last_tool_calls", [])
        events: list[dict] = []
        messages_history = list(state.get("messages", []))
        calling_role = state.get("current_role", "generalist")
        calling_spec = self._get_specialist(calling_role)
        allowed_tools = calling_spec.tools if calling_spec else None

        active_tools = self._tools
        if active_tools is not None and allowed_tools is not None:
            active_tools = active_tools.subset(allowed_tools)

        is_terminal = False
        terminal_output = ""

        for tc in tool_calls:
            func = tc.get("function", {})
            name = func.get("name", "")
            raw_args = func.get("arguments", "{}")
            parsed_args: dict[str, Any] = {}
            if isinstance(raw_args, str):
                try:
                    parsed_args = json.loads(raw_args)
                except Exception:
                    parsed_args = {}
            elif isinstance(raw_args, dict):
                parsed_args = raw_args

            # Check specialist-level tool permissions
            if allowed_tools is not None and name not in set(allowed_tools):
                result = {"error": f"Tool '{name}' is not permitted for specialist '{calling_role}'."}
                events.append({
                    "type": "error",
                    "content": f"Security blocked unpermitted tool '{name}' for specialist '{calling_role}'.",
                })
            else:
                decision = self.permissions.check(name, parsed_args)
                if decision.action == "deny":
                    result = {"error": f"Permission denied: {decision.reason}"}
                    events.append({"type": "error", "content": f"Security blocked tool '{name}': {decision.reason}"})
                elif decision.action == "confirm" and self.confirm_callback:
                    approved = self.confirm_callback(name, parsed_args, decision.reason)
                    if approved:
                        events.append({"type": "tool_call", "name": name, "arguments": raw_args})
                        result = (
                            active_tools.execute({"name": name, "arguments": raw_args})
                            if active_tools else {"error": "No tool registry"}
                        )
                        events.append({"type": "tool_result", "name": name, "result": result})
                    else:
                        result = {"error": "Tool call cancelled by user"}
                        events.append({"type": "error", "content": f"User denied permission for tool '{name}'"})
                else:
                    events.append({"type": "tool_call", "name": name, "arguments": raw_args})
                    result = (
                        active_tools.execute({"name": name, "arguments": raw_args})
                        if active_tools else {"error": "No tool registry"}
                    )
                    events.append({"type": "tool_result", "name": name, "result": result})

            # Check if this tool is a successful terminal action
            if name == "complete_task":
                try:
                    res_data = json.loads(result) if isinstance(result, str) else result
                    if isinstance(res_data, dict) and res_data.get("status") == "completed":
                        is_terminal = True
                        terminal_output = str(parsed_args.get("reply") or parsed_args.get("response") or parsed_args.get("message") or "")
                except Exception:
                    pass
            elif name == "exit_agent":
                try:
                    res_data = json.loads(result) if isinstance(result, str) else result
                    if isinstance(res_data, dict) and res_data.get("status") == "exited":
                        is_terminal = True
                        terminal_output = str(parsed_args.get("summary") or parsed_args.get("result") or "")
                except Exception:
                    pass

            messages_history.append(
                {
                    "role": "tool",
                    "name": name,
                    "tool_call_id": tc.get("id", ""),
                    "content": json.dumps(result) if not isinstance(result, str) else result,
                }
            )

        target_role = "end" if is_terminal else state.get("current_role", "generalist")
        final_output = terminal_output if is_terminal else state.get("final_output", "")
        if is_terminal and final_output:
            events.append({"type": "final", "content": final_output, "role": calling_role})

        return {
            **state,
            "messages": messages_history,
            "last_tool_calls": [],
            "target_role": target_role,
            "final_output": final_output,
            "events": events,
        }

    def _forced_final_node(self, state: ConductorState) -> ConductorState:
        """Synthesize final response from generalist when hop limit is reached."""
        events: list[dict] = [
            {
                "type": "error",
                "content": (
                    f"Hop limit of {self.config.max_hops} reached; forcing a "
                    "final answer from the generalist."
                ),
            }
        ]
        messages_history = list(state.get("messages", []))
        messages_history.append(
            {"role": "system", "content": self._final_answer_prompt(), "route": None}
        )

        try:
            model = self._get_chat_model("generalist")
            lc_messages = self._format_messages_for_langchain(messages_history)
            response = model.invoke(lc_messages)
            raw = _extract_text(response.content)
            content, _ = parse_route_tag(raw)
            cleaned_content = self._strip_role_echo(content)
            messages_history.append({"role": "generalist", "content": cleaned_content, "route": "return"})
            events.append({"type": "final", "content": cleaned_content, "role": "generalist"})
            return {
                **state,
                "messages": messages_history,
                "current_role": "generalist",
                "last_response": cleaned_content,
                "final_output": cleaned_content,
                "events": events,
            }
        except Exception as exc:
            err = f"Error calling generalist: {exc}"
            events.append({"type": "error", "content": err})
            return {
                **state,
                "error": err,
                "events": events,
            }

    def _invalid_target_node(self, state: ConductorState) -> ConductorState:
        """Handle attempt to route to an undeclared specialist."""
        prev_role = state.get("previous_role")
        prev = prev_role if prev_role is not None else "specialist"
        target_role = state.get("target_role")
        target = target_role if target_role is not None else "unknown"
        events: list[dict[str, Any]] = [
            {"type": "error", "content": f"Cannot route to '{target}': unknown specialist."},
            {"type": "route", "from_role": prev, "to_role": "generalist"},
        ]
        messages_history = list(state.get("messages", []))
        messages_history.append(
            {
                "role": "system",
                "content": f"[The {prev} tried to route to '{target}' which does not exist. You are the generalist — handle this.]",
                "route": None,
            }
        )
        return {
            **state,
            "messages": messages_history,
            "current_role": "generalist",
            "previous_role": "generalist",
            "events": events,
        }

    def _forbidden_delegation_node(self, state: ConductorState) -> ConductorState:
        """Handle delegation violation."""
        prev_role = state.get("previous_role")
        prev = prev_role if prev_role is not None else "specialist"
        target_role = state.get("target_role")
        target = target_role if target_role is not None else "unknown"
        allowed = self._delegation_mask.get(prev, [])
        events: list[dict[str, Any]] = [
            {"type": "error", "content": f"'{prev}' cannot delegate to '{target}'. Allowed targets: {allowed}"},
            {"type": "route", "from_role": prev, "to_role": "generalist"},
        ]
        messages_history = list(state.get("messages", []))
        messages_history.append(
            {
                "role": "system",
                "content": f"[The {prev} specialist attempted to delegate to {target}, which is not permitted. You are the generalist — handle this.]",
                "route": None,
            }
        )
        return {
            **state,
            "messages": messages_history,
            "current_role": "generalist",
            "previous_role": "generalist",
            "events": events,
        }

    def _loop_detected_node(self, state: ConductorState) -> ConductorState:
        """Prevent infinite routing loops back to already visited specialists."""
        target = state.get("target_role", "specialist")
        messages_history = list(state.get("messages", []))
        messages_history.append(
            {
                "role": "system",
                "content": (
                    f"[You already received an answer from the '{target}' specialist for this question. "
                    "Do NOT route again. Synthesize a final response using everything discussed "
                    "so far and end with [ROUTE: return].]"
                ),
                "route": None,
            }
        )
        return {
            **state,
            "messages": messages_history,
            "current_role": "generalist",
        }

    # ------------------------------------------------------------------
    # Graph Construction & Conditional Routing
    # ------------------------------------------------------------------

    def _make_route_edge(self, role_name: str) -> Callable[[ConductorState], str]:
        """Create conditional routing edge logic for a specific agent role."""

        def route_edge(state: ConductorState) -> str:
            if state.get("error"):
                return "end"

            target_role = state.get("target_role")
            if target_role == "tool_execution":
                return "tool_execution"

            is_generalist = role_name == "generalist"

            if state.get("hops", 0) >= self.config.max_hops:
                return "end" if is_generalist else "forced_final"

            if target_role == "return":
                return "end" if is_generalist else "generalist"

            if is_generalist and target_role == "generalist":
                return "end"

            if target_role not in self.config.specialists and target_role != "generalist":
                return "invalid_target"

            if not is_generalist:
                allowed = self._delegation_mask.get(role_name, [])
                if target_role not in allowed:
                    return "forbidden_delegation"

            if target_role in state.get("visited_specialists", []):
                return "loop_detected"

            return target_role

        return route_edge

    def _build_graph(self) -> Any:
        """Construct the compiled LangGraph StateGraph connecting all agents and tools."""
        builder = StateGraph(ConductorState)

        all_roles = ["generalist"] + list(self.config.specialists.keys())

        # Add agent nodes
        for role in all_roles:
            builder.add_node(role, self._make_agent_node(role))

        # Add tool and recovery nodes
        builder.add_node("tool_execution", self._tool_execution_node)
        builder.add_node("forced_final", self._forced_final_node)
        builder.add_node("invalid_target", self._invalid_target_node)
        builder.add_node("forbidden_delegation", self._forbidden_delegation_node)
        builder.add_node("loop_detected", self._loop_detected_node)

        # Set entry point
        builder.set_entry_point("generalist")

        # Routing edges mapping
        destination_map: dict[Any, str] = {r: r for r in all_roles}
        destination_map.update(
            {
                "tool_execution": "tool_execution",
                "forced_final": "forced_final",
                "invalid_target": "invalid_target",
                "forbidden_delegation": "forbidden_delegation",
                "loop_detected": "loop_detected",
                "end": END,
            }
        )

        for role in all_roles:
            builder.add_conditional_edges(role, self._make_route_edge(role), destination_map)

        # Return from tool execution back to active calling role, or END if terminal
        def _route_after_tools(state: ConductorState) -> str:
            if state.get("target_role") == "end":
                return "end"
            return state.get("current_role", "generalist")

        builder.add_conditional_edges(
            "tool_execution",
            _route_after_tools,
            {**{r: r for r in all_roles}, "end": END},
        )

        # Recovery nodes return to generalist
        builder.add_edge("invalid_target", "generalist")
        builder.add_edge("forbidden_delegation", "generalist")
        builder.add_edge("loop_detected", "generalist")
        builder.add_edge("forced_final", END)

        return builder.compile()

    # ------------------------------------------------------------------
    # Public Execution APIs
    # ------------------------------------------------------------------

    def chat(self, message: str) -> Generator[dict, None, str]:
        """Send a user message and run the multi-agent routing loop via LangGraph."""
        self.history.append({"role": "user", "content": message, "route": None})

        initial_state: ConductorState = {
            "messages": list(self.history),
            "current_role": "generalist",
            "previous_role": None,
            "target_role": None,
            "hops": 0,
            "visited_specialists": [],
            "last_response": "",
            "last_tool_calls": [],
            "final_output": "",
            "error": None,
            "events": [],
        }

        current_state = dict(initial_state)

        for output in self._graph.stream(initial_state, stream_mode="updates"):
            for _, node_update in output.items():
                if not isinstance(node_update, dict):
                    continue
                current_state.update(node_update)
                yield from node_update.get("events", [])

        msgs = current_state.get("messages", self.history)
        if isinstance(msgs, list):
            self.history = msgs
        final_output_val = current_state.get("final_output") or current_state.get("last_response", "")
        return str(final_output_val)

    def chat_stream(self, message: str) -> Iterator[str]:
        """Stream generalist output tokens as they are produced."""
        self.history.append({"role": "user", "content": message, "route": None})

        current_role = "generalist"
        hops = 0
        visited_specialists: set[str] = set()

        while True:
            if hops >= self.config.max_hops:
                # Forced final answer from generalist
                messages = list(self.history)
                messages.append({"role": "system", "content": self._final_answer_prompt(), "route": None})
                model = self._get_chat_model("generalist")
                lc_messages = self._format_messages_for_langchain(messages)
                res = model.invoke(lc_messages)
                content = _extract_text(res.content)
                cleaned, _ = parse_route_tag(content)
                self.history.append({"role": "generalist", "content": cleaned, "route": "return"})
                yield cleaned
                return

            specialist_config = self._get_specialist(current_role)
            if specialist_config is None:
                yield f"[error] Unknown role '{current_role}' — no config found."
                return

            is_generalist = current_role == "generalist"
            state: ConductorState = {
                "messages": list(self.history),
                "current_role": current_role,
                "hops": hops,
                "visited_specialists": list(visited_specialists),
            }

            if self._tools:
                agent_node_fn = self._make_agent_node(current_role)
                while True:
                    update_dict = agent_node_fn(state)
                    state.update(update_dict)
                    if state.get("target_role") == "tool_execution":
                        update_dict = self._tool_execution_node(state)
                        state.update(update_dict)
                        if state.get("target_role") == "end":
                            break
                    else:
                        break
                response = state.get("final_output") or state.get("last_response", "")
                if is_generalist and response:
                    yield response
            elif is_generalist:
                chunks: list[str] = []
                model = self._get_chat_model(current_role)
                lc_messages = [SystemMessage(content=specialist_config.system_prompt)] + self._format_messages_for_langchain(self.history)
                try:
                    for chunk in model.stream(lc_messages):
                        delta = _extract_text(chunk.content)
                        chunks.append(delta)
                    for _, emit in _stream_without_tag(iter(chunks)):
                        if emit:
                            yield emit
                    response = "".join(chunks)
                except Exception as exc:
                    yield f"[error] Error calling {current_role}: {exc}"
                    return
            else:
                model = self._get_chat_model(current_role)
                lc_messages = [SystemMessage(content=specialist_config.system_prompt)] + self._format_messages_for_langchain(self.history)
                try:
                    res = model.invoke(lc_messages)
                    response = _extract_text(res.content)
                except Exception as exc:
                    yield f"[error] Error calling {current_role}: {exc}"
                    return

            hops += 1
            cleaned_content, route_target = parse_route_tag(response)
            cleaned_content = self._strip_role_echo(cleaned_content)
            self.history.append(
                {"role": current_role, "content": cleaned_content, "route": route_target}
            )

            if route_target == "return":
                if is_generalist:
                    return
                visited_specialists.add(current_role)
                current_role = "generalist"
                continue

            if is_generalist and route_target == "generalist":
                return

            if route_target not in self.config.specialists:
                self.history.append(
                    {
                        "role": "system",
                        "content": f"[The {current_role} tried to route to '{route_target}' which does not exist. You are the generalist — handle this.]",
                        "route": None,
                    }
                )
                current_role = "generalist"
                continue

            if not is_generalist and route_target not in self._delegation_mask.get(current_role, []):
                self.history.append(
                    {
                        "role": "system",
                        "content": f"[The {current_role} specialist attempted to delegate to {route_target}, which is not permitted. You are the generalist — handle this.]",
                        "route": None,
                    }
                )
                current_role = "generalist"
                continue

            if route_target in visited_specialists:
                self.history.append(
                    {
                        "role": "system",
                        "content": f"[You already received an answer from the '{route_target}' specialist for this question. Do NOT route again. Synthesize a final response using everything discussed so far and end with [ROUTE: return].]",
                        "route": None,
                    }
                )
                current_role = "generalist"
                continue

            current_role = route_target

    def save_history(self, path: str) -> None:
        Path(path).write_text(json.dumps(self.history, indent=2))

    def load_history(self, path: str) -> None:
        self.history = json.loads(Path(path).read_text())
