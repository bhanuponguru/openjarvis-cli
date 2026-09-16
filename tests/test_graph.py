"""Unit tests for the OpenJarvis cognitive graph protocol, blackboard, and engine."""

import json
from pathlib import Path

import pytest

from openjarvis.graph.blackboard import CycleDetectedError, StateBlackboard
from openjarvis.graph.engine import CognitiveGraphEngine
from openjarvis.graph.protocol import (
    ActObservationMessage,
    CodeDirectiveMessage,
    CodeProposalMessage,
    TaskCompleteMessage,
    TaskInitMessage,
)


def test_protocol_serialization():
    msg = TaskInitMessage(
        task_id="t1",
        goal="Fix issue #42",
        context_files=["src/main.py"],
    )
    serialized = msg.model_dump_json()
    deserialized = TaskInitMessage.model_validate_json(serialized)
    assert deserialized.task_id == "t1"
    assert deserialized.goal == "Fix issue #42"
    assert deserialized.context_files == ["src/main.py"]


def test_blackboard_compaction():
    task = TaskInitMessage(task_id="t1", goal="Test compaction")
    bb = StateBlackboard(task=task)

    # Add long observation
    long_output = "\n".join([f"line {i}" for i in range(100)])
    obs = ActObservationMessage(
        task_id="t1",
        tool_name="test_tool",
        output=long_output,
        success=True,
    )
    bb.record_message(obs)

    orch_view = bb.get_orchestrator_view()
    assert len(orch_view["history"]) == 1
    compacted = orch_view["history"][0]["output"]
    assert "lines omitted" in compacted
    assert "line 0" in compacted
    assert "line 99" in compacted


def test_blackboard_cycle_detection():
    task = TaskInitMessage(task_id="t1", goal="Test cycles")
    bb = StateBlackboard(task=task)

    directive = CodeDirectiveMessage(
        task_id="t1",
        directive="repeat directive",
        target_files=["a.py"],
    )

    bb.record_message(directive)
    bb.record_message(directive)
    with pytest.raises(CycleDetectedError, match="Graph cycle detected"):
        bb.record_message(directive)


def test_graph_engine_step_with_mock(tmp_path: Path):
    target = tmp_path / "app.py"
    target.write_text("print('hello')", encoding="utf-8")

    # Mock invoker returning orchestrator -> coder -> complete
    step_count = 0

    def mock_invoker(model: str, prompt: list[dict[str, str]]) -> str:
        nonlocal step_count
        step_count += 1
        if "orchestrator" in model:
            if step_count == 1:
                return json.dumps({
                    "action": "code",
                    "payload": {
                        "directive": "replace hello with world",
                        "target_files": [str(target)],
                    },
                })
            else:
                return json.dumps({
                    "action": "complete",
                    "payload": {"summary": "Replacement complete."},
                })
        elif "coder" in model:
            return json.dumps({
                "explanation": "Replacing string hello with world",
                "files_touched": [str(target)],
                "tool_calls": [
                    {
                        "command": "str_replace",
                        "path": str(target),
                        "old_str": "hello",
                        "new_str": "world",
                    }
                ],
                "status": "complete",
            })
        return "{}"

    engine = CognitiveGraphEngine(invoker=mock_invoker)
    task = TaskInitMessage(task_id="t1", goal="Modify app.py", context_files=[str(target)])
    bb = StateBlackboard(task=task)

    # Step 1: Orchestrator delegates to Coder, Coder issues StrReplaceCommand
    p1 = engine.step(bb)
    assert isinstance(p1, CodeProposalMessage)
    assert target.read_text(encoding="utf-8") == "print('world')"

    # Step 2: Orchestrator completes task
    p2 = engine.step(bb)
    assert isinstance(p2, TaskCompleteMessage)
    assert p2.summary == "Replacement complete."

