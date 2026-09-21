"""Dynamic Agent Graph topology for OpenJarvis MAS.

Maintains nodes, parent-child hierarchies, dynamic communication edges,
and enforces the strict bottom-up exit constraint.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AgentNodeInfo:
    """Metadata for an agent node within the dynamic topology."""

    agent_id: str
    role: str
    parent_id: str | None = None
    children_ids: set[str] = field(default_factory=set)
    status: str = "IDLE"  # IDLE | RUNNING | EXITED
    depth: int = 0


class DynamicAgentGraph:
    """Dynamic graph topology managing agents, edges, and lifecycle constraints."""

    def __init__(self) -> None:
        self.nodes: dict[str, AgentNodeInfo] = {}
        self._adjacency: dict[str, set[str]] = {}

    def add_node(
        self,
        agent_id: str,
        role: str,
        parent_id: str | None = None,
    ) -> AgentNodeInfo:
        """Register a new agent node and wire the default parent-child edge."""
        if agent_id in self.nodes:
            raise ValueError(f"Agent node '{agent_id}' already exists in topology.")

        depth = 0
        if parent_id is not None:
            if parent_id not in self.nodes:
                raise ValueError(f"Parent agent '{parent_id}' does not exist in topology.")
            depth = self.nodes[parent_id].depth + 1
            self.nodes[parent_id].children_ids.add(agent_id)

        node = AgentNodeInfo(
            agent_id=agent_id,
            role=role,
            parent_id=parent_id,
            depth=depth,
            status="IDLE",
        )
        self.nodes[agent_id] = node
        self._adjacency[agent_id] = set()

        if parent_id is not None:
            self.add_edge(parent_id, agent_id)

        return node

    def add_edge(self, node_a: str, node_b: str, bidirectional: bool = True) -> None:
        """Create a communication edge between two existing agents."""
        if node_a not in self.nodes:
            raise ValueError(f"Agent '{node_a}' does not exist in topology.")
        if node_b not in self.nodes:
            raise ValueError(f"Agent '{node_b}' does not exist in topology.")

        self._adjacency.setdefault(node_a, set()).add(node_b)
        if bidirectional:
            self._adjacency.setdefault(node_b, set()).add(node_a)

    def get_neighbors(self, agent_id: str) -> list[str]:
        """Return a list of all agent IDs connected to the specified agent."""
        return sorted(self._adjacency.get(agent_id, set()))

    def get_active_children(self, agent_id: str) -> list[str]:
        """Return a list of active child agent IDs spawned by this agent."""
        node = self.nodes.get(agent_id)
        if not node:
            return []
        return sorted(
            child_id
            for child_id in node.children_ids
            if self.nodes.get(child_id) and self.nodes[child_id].status != "EXITED"
        )

    def can_exit(self, agent_id: str) -> tuple[bool, str]:
        """Check if an agent is allowed to exit (strict bottom-up termination).

        An agent can only exit when all child agents it spawned have exited.
        """
        node = self.nodes.get(agent_id)
        if not node:
            return False, f"Agent '{agent_id}' does not exist in topology."

        active_children = self.get_active_children(agent_id)
        if active_children:
            return (
                False,
                f"Agent '{agent_id}' cannot exit: spawned children {active_children} are still active.",
            )

        return True, "OK"

    def mark_exited(self, agent_id: str) -> None:
        """Transition an agent node to EXITED state."""
        node = self.nodes.get(agent_id)
        if not node:
            raise ValueError(f"Agent '{agent_id}' does not exist in topology.")
        node.status = "EXITED"

    def active_agents(self) -> list[str]:
        """Return all agent IDs currently in IDLE or RUNNING status."""
        return sorted(
            aid for aid, node in self.nodes.items() if node.status != "EXITED"
        )

    def is_exited(self, agent_id: str) -> bool:
        """Check if an agent is in EXITED status."""
        node = self.nodes.get(agent_id)
        return bool(node and node.status == "EXITED")

