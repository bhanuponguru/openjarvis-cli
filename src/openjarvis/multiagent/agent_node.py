"""AgentNode representing an autonomous Conductor actor within the MAS graph."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import TYPE_CHECKING, Any

from openjarvis.artifacts import AgentArtifact, ArtifactStore
from openjarvis.conductor import Conductor
from openjarvis.model_types import (
    AgentProfileConfig,
)
from openjarvis.multiagent.graph_topology import DynamicAgentGraph
from openjarvis.multiagent.protocol import (
    AgentExitNotification,
    BaseAgentMessage,
    FindingsReportMessage,
)
from openjarvis.tools import Tool, ToolRegistry

if TYPE_CHECKING:
    from openjarvis.multiagent.engine import MultiAgentSystem

logger = logging.getLogger(__name__)


class AgentNode:
    """An autonomous agent node in the multi-agent system."""

    def __init__(
        self,
        agent_id: str,
        role: str,
        profile: AgentProfileConfig,
        conductor: Conductor,
        graph: DynamicAgentGraph,
        artifact_store: ArtifactStore,
        system: MultiAgentSystem,
        is_root: bool = False,
    ) -> None:
        self.agent_id = agent_id
        self.role = role
        self.profile = profile
        self.conductor = conductor
        self.graph = graph
        self.artifact_store = artifact_store
        self.system = system
        self.is_root = is_root

        self.inbox: asyncio.Queue[BaseAgentMessage] = asyncio.Queue()
        self.turn_count = 0
        self.exited = False
        self.latest_artifact: AgentArtifact | None = None
        self.final_reply: str = ""

        # Register MAS meta-tools into this conductor's registry
        self._register_meta_tools()

    def _register_meta_tools(self) -> None:
        """Inject meta-tools for dynamic spawning, edge connection, consensus, and exit."""
        tools = self.conductor._tools
        if tools is None:
            tools = ToolRegistry()
            self.conductor._tools = tools

        # 1. spawn_agent
        def spawn_agent(
            role: str = "",
            task: str = "",
            agent_id: str | None = None,
            connect_to: list[str] | None = None,
            **kwargs: Any,
        ) -> str:
            """Spawn a new subordinate agent node to work on a sub-task.

            Args:
                role: Role or agent profile name (e.g. researcher, coder, math, planner).
                task: Clear description of the assignment or objective for the spawned agent.
                agent_id: Optional unique identifier. Auto-generated if omitted.
                connect_to: Optional list of additional agent IDs to connect with in the graph.
            """
            resolved_role = role or str(kwargs.get("agent_type") or kwargs.get("profile") or "generalist")
            resolved_task = task or str(kwargs.get("prompt") or kwargs.get("assignment") or kwargs.get("instruction") or "")
            resolved_agent_id = agent_id or kwargs.get("id") or kwargs.get("name")
            resolved_connect = connect_to or kwargs.get("connect")
            result = self.system.spawn_agent(
                spawner_id=self.agent_id,
                role=resolved_role,
                task=resolved_task,
                agent_id=resolved_agent_id,
                connect_to=resolved_connect,
            )
            return json.dumps(result)

        tools.register(
            Tool(
                name="spawn_agent",
                description="Spawn a new subordinate agent node to work on a sub-task.",
                parameters={
                    "type": "object",
                    "properties": {
                        "role": {
                            "type": "string",
                            "description": "Role or profile name (e.g. researcher, coder, math, planner).",
                        },
                        "task": {
                            "type": "string",
                            "description": "Detailed task description for the spawned agent.",
                        },
                        "agent_id": {
                            "type": "string",
                            "description": "Optional custom ID for the spawned agent.",
                        },
                        "connect_to": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of additional agent IDs to connect to.",
                        },
                    },
                    "required": ["role", "task"],
                },
                func=spawn_agent,
            )
        )

        # 2. connect_agents
        def connect_agents(target_agent_id: str = "", **kwargs: Any) -> str:
            """Create a bidirectional communication edge between this agent and another agent.

            Args:
                target_agent_id: The ID of the target agent to connect with.
            """
            target = target_agent_id or str(kwargs.get("agent_id") or kwargs.get("target") or "")
            if not target:
                return json.dumps({"status": "error", "error": "target_agent_id required"})
            try:
                self.graph.add_edge(self.agent_id, target)
                self.system.emit_event({
                    "type": "agent_connected",
                    "source_id": self.agent_id,
                    "target_id": target,
                })
                return json.dumps({
                    "status": "success",
                    "connected": [self.agent_id, target],
                })
            except Exception as exc:
                return json.dumps({"status": "error", "error": str(exc)})

        tools.register(
            Tool(
                name="connect_agents",
                description="Create a bidirectional communication edge between this agent and another agent in the graph.",
                parameters={
                    "type": "object",
                    "properties": {
                        "target_agent_id": {
                            "type": "string",
                            "description": "The ID of the target agent to connect with.",
                        },
                    },
                    "required": ["target_agent_id"],
                },
                func=connect_agents,
            )
        )

        # 3. report_findings
        def report_findings(
            summary: str = "",
            details: str | dict[str, Any] | None = None,
            target_neighbors: list[str] | None = None,
            **kwargs: Any,
        ) -> str:
            """Report significant findings, evidence, or progress to connected neighbors.

            Args:
                summary: Concise high-level finding summary.
                details: Detailed findings, calculations, diffs, or data points.
                target_neighbors: Optional list of specific connected neighbors. Broadcasts to all connected neighbors if omitted.
            """
            resolved_summary = summary or str(kwargs.get("findings") or kwargs.get("finding") or kwargs.get("message") or "")
            resolved_details = details or kwargs.get("data") or kwargs.get("content")
            resolved_targets = target_neighbors or kwargs.get("neighbors") or kwargs.get("recipients")

            neighbors = self.graph.get_neighbors(self.agent_id)
            if not neighbors:
                return json.dumps({"status": "warning", "message": "No connected neighbors to report to."})

            recipients = [n for n in resolved_targets if n in neighbors] if resolved_targets else neighbors
            if not recipients:
                return json.dumps({"status": "error", "message": f"None of {resolved_targets} are connected neighbors."})

            for r_id in recipients:
                msg = FindingsReportMessage(
                    sender_id=self.agent_id,
                    recipient_id=r_id,
                    summary=resolved_summary,
                    details=resolved_details,
                )
                self.system.send_message(msg)

            self.system.emit_event({
                "type": "findings_reported",
                "sender_id": self.agent_id,
                "recipients": recipients,
                "summary": resolved_summary,
            })

            return json.dumps({
                "status": "success",
                "recipients": recipients,
                "summary": resolved_summary,
            })

        tools.register(
            Tool(
                name="report_findings",
                description="Report significant findings, calculations, or status to connected neighbor agents.",
                parameters={
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Concise summary of findings.",
                        },
                        "details": {
                            "description": "Optional detailed findings, code, data, or notes.",
                        },
                        "target_neighbors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional specific connected neighbors. Defaults to all neighbors.",
                        },
                    },
                    "required": ["summary"],
                },
                func=report_findings,
            )
        )

        # 4. exit_agent (for non-root agents)
        if not self.is_root:
            def exit_agent(
                summary: str = "",
                artifact: str | dict[str, Any] | None = None,
                artifact_type: str = "markdown",
                **kwargs: Any,
            ) -> str:
                """Conclude your assignment and exit the multi-agent graph with a deliverables artifact.

                Args:
                    summary: Executive summary of what was accomplished.
                    artifact: Full artifact content (markdown report, code, analysis, or data).
                    artifact_type: Format of the artifact (markdown, code, json, text).
                """
                resolved_summary = summary or str(kwargs.get("description") or kwargs.get("result") or "Mission complete.")
                raw_art = artifact if artifact is not None else kwargs.get("deliverable") or kwargs.get("content") or kwargs.get("report") or resolved_summary
                resolved_type = artifact_type or str(kwargs.get("type") or "markdown")

                can_exit, reason = self.graph.can_exit(self.agent_id)
                if not can_exit:
                    return json.dumps({"status": "blocked", "message": reason})

                # Persist artifact
                saved_artifact = self.artifact_store.save(
                    agent_id=self.agent_id,
                    name=f"{self.agent_id}_output",
                    content=raw_art,
                    content_type=resolved_type,
                    metadata={"summary": resolved_summary, "role": self.role},
                )
                self.latest_artifact = saved_artifact

                # Mark exited in topology
                self.graph.mark_exited(self.agent_id)
                self.exited = True

                # Notify all connected neighbors with exit artifact
                neighbors = self.graph.get_neighbors(self.agent_id)
                for n_id in neighbors:
                    exit_msg = AgentExitNotification(
                        sender_id=self.agent_id,
                        recipient_id=n_id,
                        summary=resolved_summary,
                        artifact=saved_artifact.to_dict(),
                    )
                    self.system.send_message(exit_msg)

                self.system.emit_event({
                    "type": "agent_exited",
                    "agent_id": self.agent_id,
                    "role": self.role,
                    "summary": resolved_summary,
                    "artifact_id": saved_artifact.artifact_id,
                    "disk_path": saved_artifact.disk_path,
                })

                return json.dumps({
                    "status": "exited",
                    "artifact_id": saved_artifact.artifact_id,
                    "disk_path": saved_artifact.disk_path,
                    "summary": resolved_summary,
                })

            tools.register(
                Tool(
                    name="exit_agent",
                    description="Conclude your mission and exit the active graph by publishing your deliverables artifact. All spawned child agents must have exited first.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "Summary of the completed mission and findings.",
                            },
                            "artifact": {
                                "description": "The final deliverable artifact (markdown report, code, json, etc.).",
                            },
                            "artifact_type": {
                                "type": "string",
                                "enum": ["markdown", "code", "json", "text"],
                                "description": "Content type of the artifact.",
                            },
                        },
                        "required": ["summary", "artifact"],
                    },
                    func=exit_agent,
                )
            )

        # 5. complete_task (for root agent)
        if self.is_root:
            def complete_task(
                reply: str = "",
                artifact: str | dict[str, Any] | None = None,
                artifact_type: str = "markdown",
                **kwargs: Any,
            ) -> str:
                """Complete the user query with a final response and optional synthesized artifact.

                Args:
                    reply: Final synthesized answer presented to the user.
                    artifact: Optional synthesized final deliverable artifact.
                    artifact_type: Format of the optional artifact.
                """
                resolved_reply = reply or str(kwargs.get("response") or kwargs.get("message") or kwargs.get("answer") or kwargs.get("output") or "")
                raw_art = artifact if artifact is not None else kwargs.get("deliverable") or kwargs.get("content")
                resolved_type = artifact_type or str(kwargs.get("type") or "markdown")

                active_children = self.graph.get_active_children(self.agent_id)
                if active_children:
                    return json.dumps({
                        "status": "blocked",
                        "message": (
                            f"Cannot complete task yet: child agents {active_children} are still working. "
                            "Wait for them to exit and publish their artifacts before completing."
                        ),
                    })

                self.final_reply = resolved_reply
                if raw_art:
                    saved_artifact = self.artifact_store.save(
                        agent_id=self.agent_id,
                        name="final_output",
                        content=raw_art,
                        content_type=resolved_type,
                    )
                    self.latest_artifact = saved_artifact
                    self.system.emit_event({
                        "type": "artifact_saved",
                        "agent_id": self.agent_id,
                        "artifact_id": saved_artifact.artifact_id,
                        "disk_path": saved_artifact.disk_path,
                    })

                self.exited = True
                return json.dumps({"status": "completed", "reply_length": len(resolved_reply)})

            tools.register(
                Tool(
                    name="complete_task",
                    description="Complete user request with a synthesized response and optional deliverable artifact once all child agents exit.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "reply": {
                                "type": "string",
                                "description": "Final response to provide to the user.",
                            },
                            "artifact": {
                                "description": "Optional deliverable artifact to persist for the user.",
                            },
                            "artifact_type": {
                                "type": "string",
                                "enum": ["markdown", "code", "json", "text"],
                                "description": "Content type of the artifact.",
                            },
                        },
                        "required": ["reply"],
                    },
                    func=complete_task,
                )
            )

    async def step(self, incoming_prompt: str) -> str:
        """Execute a single internal Conductor turn for this agent."""
        self.turn_count += 1
        output_events: list[dict] = []

        def run_conductor() -> str:
            resp = ""
            for event in self.conductor.chat(incoming_prompt):
                output_events.append(event)
                # Forward relevant events to system (excluding internal final events,
                # since the MAS engine emits the authoritative system final event).
                if event.get("type") != "final":
                    self.system.emit_event({
                        "agent_id": self.agent_id,
                        "role": self.role,
                        **event,
                    })
            # 1. If terminal tool set final_reply
            if self.is_root and self.final_reply:
                return self.final_reply
            if not self.is_root and self.latest_artifact:
                return self.latest_artifact.metadata.get("summary", "") or str(self.latest_artifact.content)
            # 2. Check final event
            for ev in reversed(output_events):
                if ev.get("type") == "final" and ev.get("content"):
                    return str(ev["content"])
            # 3. Check conductor history
            if self.conductor.history:
                for msg in reversed(self.conductor.history):
                    if isinstance(msg, dict) and msg.get("content") and msg.get("role") in ("assistant", "generalist", self.role):
                        return str(msg["content"])
            return resp

        # Run conductor in worker thread to prevent blocking event loop
        loop = asyncio.get_running_loop()
        final_text = await loop.run_in_executor(None, run_conductor)
        return final_text
