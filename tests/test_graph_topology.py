"""Unit tests for DynamicAgentGraph topology and exit constraints."""

import pytest

from openjarvis.multiagent.graph_topology import DynamicAgentGraph


def test_add_node_hierarchy():
    graph = DynamicAgentGraph()
    root = graph.add_node("root", role="coordinator", parent_id=None)
    assert root.depth == 0
    assert root.status == "IDLE"

    child1 = graph.add_node("child1", role="researcher", parent_id="root")
    assert child1.depth == 1
    assert "child1" in graph.nodes["root"].children_ids
    assert "child1" in graph.get_neighbors("root")
    assert "root" in graph.get_neighbors("child1")

    child2 = graph.add_node("child2", role="coder", parent_id="child1")
    assert child2.depth == 2
    assert "child2" in graph.nodes["child1"].children_ids


def test_add_edge_arbitrary():
    graph = DynamicAgentGraph()
    graph.add_node("root", role="coordinator")
    graph.add_node("agent_a", role="researcher", parent_id="root")
    graph.add_node("agent_b", role="coder", parent_id="root")

    # Initially A and B are connected to root, not to each other
    assert "agent_b" not in graph.get_neighbors("agent_a")

    # Connect A and B
    graph.add_edge("agent_a", "agent_b")
    assert "agent_b" in graph.get_neighbors("agent_a")
    assert "agent_a" in graph.get_neighbors("agent_b")


def test_strict_bottom_up_exit_constraint():
    graph = DynamicAgentGraph()
    graph.add_node("root", role="coordinator")
    graph.add_node("parent", role="planner", parent_id="root")
    graph.add_node("child1", role="researcher", parent_id="parent")
    graph.add_node("child2", role="coder", parent_id="parent")

    # Parent cannot exit while child1 and child2 are active
    can_exit, reason = graph.can_exit("parent")
    assert not can_exit
    assert "still active" in reason

    # Leaf child can exit immediately
    can_child_exit, _ = graph.can_exit("child1")
    assert can_child_exit
    graph.mark_exited("child1")

    # Parent still cannot exit because child2 is active
    can_exit, _ = graph.can_exit("parent")
    assert not can_exit

    # Exit child2
    graph.mark_exited("child2")

    # Now parent can exit!
    can_exit, _ = graph.can_exit("parent")
    assert can_exit
    graph.mark_exited("parent")
    assert graph.is_exited("parent")


def test_unknown_node_errors():
    graph = DynamicAgentGraph()
    with pytest.raises(ValueError, match="does not exist in topology"):
        graph.add_node("child", role="coder", parent_id="nonexistent")

    with pytest.raises(ValueError, match="already exists"):
        graph.add_node("node1", role="coder")
        graph.add_node("node1", role="coder")

