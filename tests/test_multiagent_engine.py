"""Unit and integration tests for MultiAgentSystem."""

import json

import pytest

from openjarvis.model_types import (
    AgentProfileConfig,
    ConductorConfig,
    MultiAgentLimitsConfig,
    SpecialistConfig,
)
from openjarvis.multiagent.engine import MultiAgentSystem
from openjarvis.multiagent.protocol import AgentExitNotification, FindingsReportMessage


@pytest.fixture
def mas_config():
    root = AgentProfileConfig(
        name="root",
        role="coordinator",
        system_prompt="You are Root.",
        base_url="http://test/v1",
        model="test-model",
    )
    researcher = AgentProfileConfig(
        name="researcher",
        role="researcher",
        system_prompt="You are Researcher.",
        base_url="http://test/v1",
        model="test-model",
    )
    limits = MultiAgentLimitsConfig(
        max_active_agents=3,
        max_spawn_depth=2,
        max_agent_turns=5,
    )
    return ConductorConfig(
        root_agent=root,
        agents={"researcher": researcher},
        specialists={"math": SpecialistConfig(name="math", system_prompt="Math")},
        limits=limits,
    )


def test_mas_init(mas_config, tmp_path):
    mas = MultiAgentSystem(config=mas_config)
    assert "root" in mas.agents
    assert mas.graph.nodes["root"].role == "coordinator"
    assert mas.graph.nodes["root"].depth == 0


def test_mas_spawning_and_limits(mas_config):
    mas = MultiAgentSystem(config=mas_config)

    # Spawn 1 (depth 1)
    res1 = mas.spawn_agent("root", role="researcher", task="Find specs", agent_id="r1")
    assert res1["status"] == "spawned"
    assert res1["agent_id"] == "r1"
    assert res1["depth"] == 1
    assert "r1" in mas.graph.nodes["root"].children_ids
    assert "r1" in mas.graph.get_neighbors("root")

    # Spawn 2 (depth 2 from r1)
    res2 = mas.spawn_agent("r1", role="coder", task="Implement specs", agent_id="c1")
    assert res2["status"] == "spawned"
    assert res2["depth"] == 2

    # Spawn 3 from c1 (would be depth 3, exceeding max_spawn_depth=2)
    res3 = mas.spawn_agent("c1", role="reviewer", task="Review code")
    assert res3["status"] == "rejected"
    assert "exceeds maximum depth limit" in res3["error"]

    # Concurrency limit check: max_active_agents is 3 (root, r1, c1 = 3 active)
    res_max = mas.spawn_agent("root", role="planner", task="Plan more")
    assert res_max["status"] == "rejected"
    assert "Maximum active agents limit" in res_max["error"]


def test_mas_neighbor_findings_and_exit(mas_config):
    mas = MultiAgentSystem(config=mas_config)
    mas.spawn_agent("root", role="researcher", task="Find specs", agent_id="r1")

    r1_node = mas.agents["r1"]
    root_node = mas.agents["root"]

    # Call report_findings from r1
    report_tool = r1_node.conductor._tools.get("report_findings")
    assert report_tool is not None
    rep_res = json.loads(report_tool.func(summary="Found 3 papers"))
    assert rep_res["status"] == "success"
    assert "root" in rep_res["recipients"]

    # Root inbox should have received FindingsReportMessage
    assert not root_node.inbox.empty()
    msg = root_node.inbox.get_nowait()
    assert isinstance(msg, FindingsReportMessage)
    assert msg.sender_id == "r1"
    assert msg.summary == "Found 3 papers"

    # r1 calls exit_agent
    exit_tool = r1_node.conductor._tools.get("exit_agent")
    assert exit_tool is not None
    exit_res = json.loads(exit_tool.func(summary="Finished research", artifact="# Report Content"))
    assert exit_res["status"] == "exited"
    assert r1_node.exited
    assert mas.graph.is_exited("r1")

    # Root inbox should receive AgentExitNotification with artifact
    assert not root_node.inbox.empty()
    exit_msg = root_node.inbox.get_nowait()
    assert isinstance(exit_msg, AgentExitNotification)
    assert exit_msg.sender_id == "r1"
    assert exit_msg.artifact["name"] == "r1_output"
    assert exit_msg.artifact["content"] == "# Report Content"


def test_mas_root_complete_blocked_by_active_children(mas_config):
    mas = MultiAgentSystem(config=mas_config)
    mas.spawn_agent("root", role="researcher", task="Do work", agent_id="r1")

    root_node = mas.agents["root"]
    complete_tool = root_node.conductor._tools.get("complete_task")
    assert complete_tool is not None

    # Cannot complete while r1 is active
    res = json.loads(complete_tool.func(reply="All done!"))
    assert res["status"] == "blocked"
    assert "still working" in res["message"]

    # Once r1 exits
    mas.graph.mark_exited("r1")
    res2 = json.loads(complete_tool.func(reply="Now truly done!"))
    assert res2["status"] == "completed"
    assert root_node.final_reply == "All done!" or root_node.final_reply == "Now truly done!"


def test_mas_meta_tool_aliases(mas_config):
    mas = MultiAgentSystem(config=mas_config)
    # Test spawn_agent with kwargs alias
    spawn_tool = mas.agents["root"].conductor._tools.get("spawn_agent")
    assert spawn_tool is not None
    spawn_res = json.loads(spawn_tool.func(agent_type="researcher", prompt="Do research", id="r_alias"))
    assert spawn_res["status"] == "spawned"
    assert spawn_res["agent_id"] == "r_alias"

    # Test exit_agent with kwargs alias
    r_node = mas.agents["r_alias"]
    exit_tool = r_node.conductor._tools.get("exit_agent")
    assert exit_tool is not None
    exit_res = json.loads(exit_tool.func(result="Found findings", deliverable="Artifact details"))
    assert exit_res["status"] == "exited"

    # Test complete_task with kwargs alias
    complete_tool = mas.agents["root"].conductor._tools.get("complete_task")
    assert complete_tool is not None
    comp_res = json.loads(complete_tool.func(response="Synthesized answer"))
    assert comp_res["status"] == "completed"
    assert mas.agents["root"].final_reply == "Synthesized answer"


def test_mas_role_alias_resolution_and_inheritance(mas_config):
    mas = MultiAgentSystem(config=mas_config)
    # Spawn "code" should resolve or inherit
    res = mas.spawn_agent("root", role="code", task="Write python script", agent_id="c_test")
    assert res["status"] == "spawned"
    child = mas.agents["c_test"]
    assert child.profile.model == "test-model"
    assert child.profile.base_url == "http://test/v1"


def test_meta_tools_permission_exemption():
    from openjarvis.permissions import PermissionManager
    pm = PermissionManager()
    # meta-tools must be allowed automatically in interactive mode
    assert pm.check("complete_task", {}).action == "allow"
    assert pm.check("exit_agent", {}).action == "allow"
    assert pm.check("spawn_agent", {}).action == "allow"
    assert pm.check("connect_agents", {}).action == "allow"
    assert pm.check("report_findings", {}).action == "allow"
    # non-meta tool requires confirmation in interactive mode
    assert pm.check("bash", {}).action == "confirm"

