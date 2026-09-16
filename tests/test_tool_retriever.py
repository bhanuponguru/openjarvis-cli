from pathlib import Path

from openjarvis.builtin_tools import create_builtin_registry
from openjarvis.model_types import ToolRetrievalConfig
from openjarvis.tool_retriever import ToolRetriever


def test_tool_retriever_indexing_and_retrieval(tmp_path: Path):
    tools = create_builtin_registry()
    cfg = ToolRetrievalConfig(
        enabled=True,
        top_k=3,
        similarity_threshold=0.1,
        always_on_tools=["store_note", "recall_note"],
    )
    retriever = ToolRetriever(registry=tools, config=cfg, cache_dir=tmp_path)
    retriever.build_index()

    assert len(retriever._tool_names) > 0
    assert len(retriever._tool_vectors) == len(retriever._tool_names)
    assert (tmp_path / "tool_vectors.json").exists()

    # Retrieve math tools
    retrieved = retriever.retrieve("I need to solve a math equation and calculate formula")
    retrieved_names = {t.name for t in retrieved}
    assert "solve_equation" in retrieved_names or "evaluate_expression" in retrieved_names
    # Always-on tools must be present
    assert "store_note" in retrieved_names
    assert "recall_note" in retrieved_names


def test_tool_retriever_load_cache(tmp_path: Path):
    tools = create_builtin_registry()
    cfg = ToolRetrievalConfig(enabled=True, top_k=2)
    retriever1 = ToolRetriever(registry=tools, config=cfg, cache_dir=tmp_path)
    retriever1.build_index()

    retriever2 = ToolRetriever(registry=tools, config=cfg, cache_dir=tmp_path)
    loaded = retriever2.load_cache()
    assert loaded is True
    assert len(retriever2._tool_vectors) == len(retriever1._tool_vectors)

    # Retrieval after loading from cache must succeed with non-zero vector match
    retrieved = retriever2.retrieve("Calculate mathematical formula and arithmetic expression")
    assert len(retrieved) > 0
    retrieved_names = {t.name for t in retrieved}
    assert "evaluate_expression" in retrieved_names or "solve_equation" in retrieved_names
