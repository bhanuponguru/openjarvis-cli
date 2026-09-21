"""Unit tests for ArtifactStore and AgentArtifact dual persistence."""

from pathlib import Path

from openjarvis.artifacts import ArtifactStore


def test_artifact_store_save_and_retrieve(tmp_path: Path):
    store = ArtifactStore(artifacts_dir=tmp_path)

    # Markdown artifact
    art = store.save(
        agent_id="researcher-1",
        name="research_report",
        content="# Findings\n\n- Key item 1\n- Key item 2",
        content_type="markdown",
        metadata={"status": "complete"},
    )

    assert art.artifact_id.startswith("art-")
    assert art.disk_path is not None
    assert Path(art.disk_path).exists()
    assert "# Findings" in Path(art.disk_path).read_text(encoding="utf-8")

    # In-memory retrieval
    retrieved = store.get(art.artifact_id)
    assert retrieved is not None
    assert retrieved.name == "research_report"
    assert retrieved.content_type == "markdown"
    assert retrieved.metadata["status"] == "complete"

    # Agent listing
    agent_arts = store.list_for_agent("researcher-1")
    assert len(agent_arts) == 1
    assert agent_arts[0].artifact_id == art.artifact_id


def test_artifact_json_and_code(tmp_path: Path):
    store = ArtifactStore(artifacts_dir=tmp_path)

    # JSON artifact
    json_data = {"metrics": {"accuracy": 0.95, "loss": 0.05}}
    art_json = store.save(
        agent_id="evaluator",
        name="metrics_data",
        content=json_data,
        content_type="json",
    )
    assert Path(art_json.disk_path).suffix == ".json"
    assert '"accuracy": 0.95' in Path(art_json.disk_path).read_text(encoding="utf-8")

    # Code artifact
    code_content = "def add(a, b):\n    return a + b\n"
    art_code = store.save(
        agent_id="coder",
        name="calculator_patch",
        content=code_content,
        content_type="python",
    )
    assert Path(art_code.disk_path).suffix == ".py"
    assert "def add(a, b):" in Path(art_code.disk_path).read_text(encoding="utf-8")

