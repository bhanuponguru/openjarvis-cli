"""OpenJarvis Multi-Agent System (MAS).

Autonomous, dynamic multi-agent actor graph coordinating specialized Conductor
agents, inter-agent consensus, strict bottom-up exit lifecycle, and dual-persisted artifacts.
"""

from openjarvis.multiagent.agent_node import AgentNode
from openjarvis.multiagent.engine import MultiAgentSystem
from openjarvis.multiagent.graph_topology import DynamicAgentGraph
from openjarvis.multiagent.protocol import (
    AgentExitNotification,
    BaseAgentMessage,
    FindingsReportMessage,
    TaskAssignmentMessage,
    TopologyUpdateMessage,
)

__all__ = [
    "AgentExitNotification",
    "AgentNode",
    "BaseAgentMessage",
    "DynamicAgentGraph",
    "FindingsReportMessage",
    "MultiAgentSystem",
    "TaskAssignmentMessage",
    "TopologyUpdateMessage",
]

