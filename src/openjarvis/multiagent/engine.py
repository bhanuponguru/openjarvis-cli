"""MultiAgentSystem coordinator and execution engine for OpenJarvis.

Orchestrates concurrent agent actors, enforces dynamic topology, message routing,
depth and concurrency limits, and strict bottom-up completion.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Callable, Generator
from dataclasses import replace
from pathlib import Path
from typing import Any

from openjarvis.artifacts import ArtifactStore
from openjarvis.builtin_tools import create_builtin_registry
from openjarvis.conductor import Conductor
from openjarvis.config_loader import load_config
from openjarvis.model_types import (
    AgentProfileConfig,
    ConductorConfig,
    MultiAgentLimitsConfig,
    SpecialistConfig,
)
from openjarvis.multiagent.agent_node import AgentNode
from openjarvis.multiagent.graph_topology import DynamicAgentGraph
from openjarvis.multiagent.protocol import (
    AgentExitNotification,
    BaseAgentMessage,
    FindingsReportMessage,
    TaskAssignmentMessage,
)
from openjarvis.tools import ToolRegistry
from openjarvis.workspace import Workspace, discover_workspace, set_current_workspace

logger = logging.getLogger(__name__)


class MultiAgentSystem:
    """Multi-Agent System coordinating dynamic actor agents across a graph."""

    def __init__(
        self,
        config: ConductorConfig | None = None,
        config_path: str | Path | None = None,
        workspace: Workspace | None = None,
        tools: ToolRegistry | None = None,
        confirm_callback: Callable[[str, dict[str, Any], str], bool] | None = None,
    ) -> None:
        self.workspace = workspace or discover_workspace()
        set_current_workspace(self.workspace)
        self.confirm_callback = confirm_callback

        if config:
            self.config = config
        elif config_path:
            self.config = load_config(config_path, workspace=self.workspace)
        else:
            self.config = load_config(workspace=self.workspace)

        self.limits: MultiAgentLimitsConfig = self.config.limits
        self.artifact_store = ArtifactStore(workspace=self.workspace)
        self.base_tools = tools if tools is not None else create_builtin_registry()

        self.graph = DynamicAgentGraph()
        self.agents: dict[str, AgentNode] = {}
        self._loop: asyncio.AbstractEventLoop | None = None
        self._running_tasks: dict[str, Any] = {}
        self._event_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

        # Initialize Root Agent
        self._init_root_agent()

    def _init_root_agent(self) -> None:
        """Initialize the persistent Root Agent."""
        root_profile = self.config.root_agent or AgentProfileConfig(
            name="root",
            role="coordinator",
            system_prompt=(
                "You are the Root Agent of OpenJarvis, directly responsible for user communication "
                "and multi-agent orchestration. Spawn specialized child agents with `spawn_agent` "
                "when needed, connect agents with `connect_agents`, and call `complete_task` when "
                "all children have exited and their work is synthesized."
            ),
        )

        root_conductor = self._build_conductor_for_agent(
            agent_id="root",
            role="coordinator",
            profile=root_profile,
        )

        self.graph.add_node(agent_id="root", role="coordinator", parent_id=None)

        root_node = AgentNode(
            agent_id="root",
            role="coordinator",
            profile=root_profile,
            conductor=root_conductor,
            graph=self.graph,
            artifact_store=self.artifact_store,
            system=self,
            is_root=True,
        )
        self.agents["root"] = root_node

    def _build_conductor_for_agent(
        self,
        agent_id: str,
        role: str,
        profile: AgentProfileConfig,
    ) -> Conductor:
        """Construct an isolated Conductor instance for an agent."""
        generalist_spec = SpecialistConfig(
            name=agent_id,
            system_prompt=profile.system_prompt,
            description=profile.description or f"{role} agent",
            provider=profile.provider,
            base_url=profile.base_url,
            model=profile.model,
            api_key_env=profile.api_key_env,
            temperature=profile.temperature,
            max_tokens=profile.max_tokens,
            stop=list(profile.stop),
            timeout=profile.timeout,
            tools=profile.tools,
        )

        # Filter specialists if restricted
        allowed_specs = profile.allowed_specialists
        if allowed_specs:
            agent_specialists = {
                k: v for k, v in self.config.specialists.items() if k in allowed_specs
            }
        else:
            agent_specialists = dict(self.config.specialists)

        agent_conductor_config = ConductorConfig(
            generalist=generalist_spec,
            specialists=agent_specialists,
            max_hops=profile.max_hops,
            tool_retrieval=self.config.tool_retrieval,
            tool_permissions=self.config.tool_permissions,
            limits=self.limits,
        )

        # Scoped tools for this agent
        agent_tools = (
            self.base_tools.subset(profile.tools)
            if profile.tools is not None
            else self.base_tools.subset(list(self.base_tools._tools.keys()))
        )

        return Conductor(
            config=agent_conductor_config,
            tools=agent_tools,
            workspace=self.workspace,
            confirm_callback=self.confirm_callback,
        )

    def emit_event(self, event: dict[str, Any]) -> None:
        """Enqueue an execution event for streaming (thread-safe)."""
        target_loop = self._loop
        if target_loop and target_loop.is_running():
            try:
                current_loop = asyncio.get_running_loop()
                if current_loop is target_loop:
                    self._event_queue.put_nowait(event)
                    return
            except RuntimeError:
                pass
            target_loop.call_soon_threadsafe(self._event_queue.put_nowait, event)
        else:
            self._event_queue.put_nowait(event)

    def send_message(self, message: BaseAgentMessage) -> None:
        """Route an inter-agent message to the recipient's inbox (thread-safe)."""
        recipient = self.agents.get(message.recipient_id)
        if recipient:
            target_loop = self._loop
            if target_loop and target_loop.is_running():
                try:
                    current_loop = asyncio.get_running_loop()
                    if current_loop is target_loop:
                        recipient.inbox.put_nowait(message)
                        return
                except RuntimeError:
                    pass
                target_loop.call_soon_threadsafe(recipient.inbox.put_nowait, message)
            else:
                recipient.inbox.put_nowait(message)
        else:
            logger.warning(
                "Message routing failed: recipient '%s' does not exist.",
                message.recipient_id,
            )

    def spawn_agent(
        self,
        spawner_id: str,
        role: str,
        task: str,
        agent_id: str | None = None,
        connect_to: list[str] | None = None,
    ) -> dict[str, Any]:
        """Spawn a new child agent node subject to limits."""
        # 1. Spawner existence and depth check
        spawner_node = self.graph.nodes.get(spawner_id)
        if not spawner_node:
            return {"status": "error", "error": f"Spawner '{spawner_id}' not found."}

        target_depth = spawner_node.depth + 1
        if target_depth > self.limits.max_spawn_depth:
            return {
                "status": "rejected",
                "error": (
                    f"Spawn depth {target_depth} exceeds maximum depth limit "
                    f"({self.limits.max_spawn_depth})."
                ),
            }

        # 2. Concurrency limit check
        active = self.graph.active_agents()
        if len(active) >= self.limits.max_active_agents:
            return {
                "status": "rejected",
                "error": f"Maximum active agents limit ({self.limits.max_active_agents}) reached.",
            }

        # 3. Create ID and resolve profile
        child_id = agent_id or f"{role}_{uuid.uuid4().hex[:4]}"
        if child_id in self.graph.nodes:
            child_id = f"{child_id}_{uuid.uuid4().hex[:4]}"

        # Look up pre-configured agent profile or build default inheriting from root/generalist
        root_ref = self.config.root_agent
        default_provider = root_ref.provider if root_ref else self.config.generalist.provider
        default_base_url = root_ref.base_url if root_ref else self.config.generalist.base_url
        default_model = root_ref.model if root_ref else self.config.generalist.model
        default_api_key_env = root_ref.api_key_env if root_ref else self.config.generalist.api_key_env

        # Common role aliases
        role_alias_map = {
            "code": "coder",
            "coding": "coder",
            "developer": "coder",
            "research": "researcher",
            "search": "researcher",
            "plan": "planner",
            "planning": "planner",
            "mathematics": "math",
            "calculation": "math",
        }
        resolved_role_key = role_alias_map.get(role.lower(), role.lower())

        if resolved_role_key in self.config.agents:
            base_profile = self.config.agents[resolved_role_key]
            profile = replace(base_profile, name=child_id)
        elif role in self.config.agents:
            base_profile = self.config.agents[role]
            profile = replace(base_profile, name=child_id)
        elif role in self.config.specialists:
            spec = self.config.specialists[role]
            profile = AgentProfileConfig(
                name=child_id,
                role=role,
                description=spec.description,
                system_prompt=spec.system_prompt,
                provider=spec.provider or default_provider,
                base_url=spec.base_url or default_base_url,
                model=spec.model or default_model,
                api_key_env=spec.api_key_env or default_api_key_env,
                temperature=spec.temperature,
                max_tokens=spec.max_tokens,
                stop=list(spec.stop),
                timeout=spec.timeout,
                tools=spec.tools,
            )
        else:
            profile = AgentProfileConfig(
                name=child_id,
                role=role,
                system_prompt=(
                    f"You are the {role.upper()} agent in OpenJarvis. "
                    "Focus on your assigned sub-task, report findings to neighbors using "
                    "`report_findings`, and call `exit_agent` with your artifact when done."
                ),
                provider=default_provider,
                base_url=default_base_url,
                model=default_model,
                api_key_env=default_api_key_env,
            )

        # 4. Add to topology
        try:
            self.graph.add_node(agent_id=child_id, role=role, parent_id=spawner_id)
            if connect_to:
                for target_id in connect_to:
                    if target_id in self.graph.nodes:
                        self.graph.add_edge(child_id, target_id)
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

        # 5. Build Conductor and AgentNode
        conductor = self._build_conductor_for_agent(
            agent_id=child_id,
            role=role,
            profile=profile,
        )
        child_node = AgentNode(
            agent_id=child_id,
            role=role,
            profile=profile,
            conductor=conductor,
            graph=self.graph,
            artifact_store=self.artifact_store,
            system=self,
            is_root=False,
        )
        self.agents[child_id] = child_node

        # 6. Launch background worker task if event loop is running (cross-thread safe)
        target_loop = self._loop
        if target_loop and target_loop.is_running():
            try:
                current_loop = asyncio.get_running_loop()
                if current_loop is target_loop:
                    worker_task = target_loop.create_task(self._run_agent_worker(child_node))
                    self._running_tasks[child_id] = worker_task
                else:
                    worker_fut = asyncio.run_coroutine_threadsafe(
                        self._run_agent_worker(child_node), target_loop
                    )
                    self._running_tasks[child_id] = worker_fut
            except RuntimeError:
                worker_fut = asyncio.run_coroutine_threadsafe(
                    self._run_agent_worker(child_node), target_loop
                )
                self._running_tasks[child_id] = worker_fut
        else:
            try:
                current_loop = asyncio.get_running_loop()
                self._loop = current_loop
                worker_task = current_loop.create_task(self._run_agent_worker(child_node))
                self._running_tasks[child_id] = worker_task
            except RuntimeError:
                # No running loop (e.g. called from synchronous unit test fixture)
                pass

        # 7. Deliver initial task assignment
        assignment = TaskAssignmentMessage(
            sender_id=spawner_id,
            recipient_id=child_id,
            task=task,
            role=role,
        )
        self.send_message(assignment)

        self.emit_event({
            "type": "agent_spawned",
            "agent_id": child_id,
            "role": role,
            "parent_id": spawner_id,
            "task": task,
            "depth": target_depth,
        })

        return {
            "status": "spawned",
            "agent_id": child_id,
            "role": role,
            "depth": target_depth,
        }

    async def _run_agent_worker(self, agent: AgentNode) -> None:
        """Worker loop processing messages for a single child agent."""
        node_info = self.graph.nodes.get(agent.agent_id)
        if node_info:
            node_info.status = "RUNNING"

        try:
            while not agent.exited:
                # Wait for next message or check timeout
                try:
                    msg = await asyncio.wait_for(
                        agent.inbox.get(),
                        timeout=self.limits.turn_timeout_seconds,
                    )
                except TimeoutError:
                    logger.warning("Agent '%s' timed out waiting for input.", agent.agent_id)
                    break

                # Format message for agent step
                if isinstance(msg, TaskAssignmentMessage):
                    prompt = (
                        f"[Task Assignment from {msg.sender_id}]:\n{msg.task}\n\n"
                        "Execute this task. Use `report_findings` to share intermediate progress, "
                        "and when complete, call `exit_agent` with your final artifact deliverable."
                    )
                elif isinstance(msg, FindingsReportMessage):
                    prompt = (
                        f"[Findings from neighbor {msg.sender_id}]:\n{msg.summary}\n"
                        f"Details: {msg.details}"
                    )
                elif isinstance(msg, AgentExitNotification):
                    prompt = (
                        f"[Neighbor {msg.sender_id} completed its mission and EXITED]:\n"
                        f"Summary: {msg.summary}\n"
                        f"Artifact: {msg.artifact.get('content', '')}"
                    )
                else:
                    prompt = str(msg)

                # Check turn limit
                if agent.turn_count >= self.limits.max_agent_turns:
                    prompt = (
                        f"{prompt}\n\n[Warning: Turn limit ({self.limits.max_agent_turns}) reached. "
                        "You must finalize your work and call `exit_agent` with your deliverable immediately.]"
                    )

                response = await agent.step(prompt)

                # Check if agent completed work without an explicit exit_agent call
                if not agent.exited and not self.graph.get_active_children(agent.agent_id) and agent.inbox.empty():
                    summary = (response[:250] if response else f"{agent.role} completed mission.")
                    saved_art = self.artifact_store.save(
                        agent_id=agent.agent_id,
                        name=f"{agent.agent_id}_output",
                        content=response or "Mission completed.",
                        content_type="text",
                        metadata={"summary": summary, "role": agent.role},
                    )
                    agent.latest_artifact = saved_art
                    self.graph.mark_exited(agent.agent_id)
                    agent.exited = True

                    neighbors = self.graph.get_neighbors(agent.agent_id)
                    for n_id in neighbors:
                        exit_msg = AgentExitNotification(
                            sender_id=agent.agent_id,
                            recipient_id=n_id,
                            summary=summary,
                            artifact=saved_art.to_dict(),
                        )
                        self.send_message(exit_msg)

                    self.emit_event({
                        "type": "agent_exited",
                        "agent_id": agent.agent_id,
                        "role": agent.role,
                        "summary": summary,
                        "artifact_id": saved_art.artifact_id,
                        "disk_path": saved_art.disk_path,
                    })
                    break

                # If turn limit exceeded and agent did not exit, force-exit with fallback artifact
                if agent.turn_count > self.limits.max_agent_turns and not agent.exited:
                    saved_art = self.artifact_store.save(
                        agent_id=agent.agent_id,
                        name=f"{agent.agent_id}_forced_exit",
                        content=response or "Agent completed work upon reaching turn limit.",
                        content_type="text",
                    )
                    agent.latest_artifact = saved_art
                    self.graph.mark_exited(agent.agent_id)
                    agent.exited = True
                    self.emit_event({
                        "type": "agent_exited",
                        "agent_id": agent.agent_id,
                        "role": agent.role,
                        "summary": "Forced exit upon reaching turn limit.",
                        "artifact_id": saved_art.artifact_id,
                    })
                    break

        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.exception("Error in worker loop for agent '%s': %s", agent.agent_id, exc)
            self.emit_event({
                "type": "error",
                "agent_id": agent.agent_id,
                "content": str(exc),
            })
        finally:
            if not agent.exited:
                self.graph.mark_exited(agent.agent_id)
                agent.exited = True

    async def run(self, user_message: str) -> str:
        """Run a full multi-agent query lifecycle asynchronously."""
        self._loop = asyncio.get_running_loop()
        root = self.agents["root"]
        root.exited = False
        root.final_reply = ""

        # Step 1: Deliver initial prompt to Root Agent
        prompt = (
            f"[User Message]: {user_message}\n\n"
            "Analyze the request. If simple, answer directly using `complete_task`. "
            "If complex, spawn appropriate specialist agents via `spawn_agent`, "
            "monitor their findings, and once all children exit, call `complete_task` "
            "with the final synthesized answer and artifact."
        )

        root_reply = await root.step(prompt)

        # Step 2: Keep processing until all child tasks finish and Root finishes
        start_time = asyncio.get_running_loop().time()
        timeout_seconds = self.limits.turn_timeout_seconds or 300.0

        while asyncio.get_running_loop().time() - start_time < timeout_seconds:
            non_root_active = [aid for aid in self.graph.active_agents() if aid != "root"]

            if not non_root_active and (root.exited or root.final_reply):
                break

            # If Root has incoming messages, process them
            processed_any = False
            while not root.inbox.empty():
                msg = root.inbox.get_nowait()
                processed_any = True
                if isinstance(msg, AgentExitNotification):
                    child_prompt = (
                        f"[Child Agent {msg.sender_id} has EXITED with deliverable]:\n"
                        f"Summary: {msg.summary}\n"
                        f"Artifact: {msg.artifact.get('content', '')}\n\n"
                        "Check if other child agents are active. If all children have completed, "
                        "synthesize their work and call `complete_task` to answer the user."
                    )
                elif isinstance(msg, FindingsReportMessage):
                    child_prompt = (
                        f"[Finding from child {msg.sender_id}]: {msg.summary}\n{msg.details}"
                    )
                else:
                    child_prompt = str(msg)

                root_reply = await root.step(child_prompt)

            # Check if all subordinate agents exited and root is ready
            non_root_active = [aid for aid in self.graph.active_agents() if aid != "root"]
            if not non_root_active:
                if not root.exited:
                    # Final synthesis prompt to root
                    synth_prompt = (
                        "[All child agents have completed and exited.]\n"
                        "Please synthesize all findings and deliverables into your final answer, "
                        "and call `complete_task(reply=...)`."
                    )
                    root_reply = await root.step(synth_prompt)
                break

            # If no messages were processed, sleep briefly to yield to background child tasks
            if not processed_any:
                await asyncio.sleep(0.1)

        # Cleanup background tasks
        for task in self._running_tasks.values():
            if not task.done():
                task.cancel()

        final_answer = root.final_reply or root_reply
        self.emit_event({
            "type": "final",
            "role": "root",
            "content": final_answer,
            "artifacts": [a.to_dict() for a in self.artifact_store.all_artifacts()],
        })
        return final_answer

    def chat(self, user_message: str) -> Generator[dict[str, Any], None, str]:
        """Synchronous generator API yielding real-time events and returning final answer."""
        events: list[dict[str, Any]] = []

        async def _execute() -> str:
            # Task running the execution
            run_task = asyncio.create_task(self.run(user_message))

            while not run_task.done():
                while not self._event_queue.empty():
                    ev = self._event_queue.get_nowait()
                    events.append(ev)
                await asyncio.sleep(0.02)

            while not self._event_queue.empty():
                ev = self._event_queue.get_nowait()
                events.append(ev)

            return await run_task

        # Run within event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                res = pool.submit(asyncio.run, _execute()).result()
        else:
            res = loop.run_until_complete(_execute())

        yield from events
        return res
