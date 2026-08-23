from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import TYPE_CHECKING, Any

from openjarvis.model_types import ToolRetrievalConfig
from openjarvis.tools import Tool, ToolRegistry

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _format_tool_for_embedding(t: Tool) -> str:
    """Format a Tool into a semantic markdown description for optimal dense embedding."""
    lines = [
        f"Tool: {t.name}",
        f"Summary: {t.description}",
    ]
    params = t.parameters.get("properties", {})
    if params:
        lines.append("Parameters:")
        for p_name, p_info in params.items():
            p_desc = p_info.get("description", "")
            p_type = p_info.get("type", "")
            lines.append(f"  - {p_name} ({p_type}): {p_desc}")
    return "\n".join(lines)


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(vec_a) != len(vec_b) or not vec_a:
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b, strict=False))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class SimpleKeywordEmbedding:
    """Fallback bag-of-words / token-overlap embedding when fastembed is not installed."""

    def __init__(self) -> None:
        self.vocab: dict[str, int] = {}

    def _tokenize(self, text: str) -> list[str]:
        import re
        return re.findall(r"[a-zA-Z0-9_]+", text.lower())

    def fit_transform(self, documents: list[str]) -> list[list[float]]:
        self.vocab = {}
        for doc in documents:
            for token in self._tokenize(doc):
                if token not in self.vocab:
                    self.vocab[token] = len(self.vocab)

        vectors: list[list[float]] = []
        for doc in documents:
            vectors.append(self.transform(doc))
        return vectors

    def transform(self, text: str) -> list[float]:
        vec = [0.0] * max(len(self.vocab), 1)
        tokens = self._tokenize(text)
        for token in tokens:
            if token in self.vocab:
                vec[self.vocab[token]] += 1.0
        return vec


class ToolRetriever:
    """Embeds tool descriptions and dynamically retrieves relevant tools for a given query or reasoning."""

    def __init__(
        self,
        registry: ToolRegistry,
        config: ToolRetrievalConfig | None = None,
        cache_dir: Path | None = None,
        model_name: str = "snowflake/snowflake-arctic-embed-xs",
    ) -> None:
        self.registry = registry
        self.config = config or ToolRetrievalConfig()
        self.cache_dir = cache_dir
        self.model_name = model_name
        self._tool_names: list[str] = []
        self._tool_vectors: list[list[float]] = []
        self._embedder: Any = None
        self._fallback_embedder: SimpleKeywordEmbedding | None = None

        self._init_embedder()

    def _init_embedder(self) -> None:
        try:
            from fastembed import TextEmbedding
            self._embedder = TextEmbedding(model_name=self.model_name)
            logger.info("Loaded fastembed TextEmbedding model: %s", self.model_name)
        except Exception:
            self._embedder = None
            self._fallback_embedder = SimpleKeywordEmbedding()
            logger.info("fastembed not installed or failed to load; using keyword embedding fallback")

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        if self._embedder is not None:
            embeddings = list(self._embedder.embed(texts))
            return [list(map(float, vec)) for vec in embeddings]
        elif self._fallback_embedder is not None:
            if not self._fallback_embedder.vocab:
                return self._fallback_embedder.fit_transform(texts)
            return [self._fallback_embedder.transform(t) for t in texts]
        return [[0.0] for _ in texts]

    def build_index(self) -> None:
        """Embed all tools currently in the registry."""
        tools = self.registry.get_tools()
        self._tool_names = list(tools.keys())
        if not self._tool_names:
            self._tool_vectors = []
            return

        descriptions = [_format_tool_for_embedding(tools[name]) for name in self._tool_names]
        if self._fallback_embedder is not None:
            self._tool_vectors = self._fallback_embedder.fit_transform(descriptions)
        else:
            self._tool_vectors = self._embed_texts(descriptions)

        self._save_cache()

    def _save_cache(self) -> None:
        if self.cache_dir:
            try:
                import json
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                cache_file = self.cache_dir / "tool_vectors.json"
                data = {
                    "tools": self._tool_names,
                    "vectors": self._tool_vectors,
                }
                cache_file.write_text(json.dumps(data), encoding="utf-8")
            except OSError as exc:
                logger.warning("Failed to cache tool vectors: %s", exc)

    def load_cache(self) -> bool:
        """Load cached vectors if valid and matching the current registry."""
        if not self.cache_dir:
            return False
        cache_file = self.cache_dir / "tool_vectors.json"
        if not cache_file.exists():
            return False

        try:
            import json
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            cached_tools = data.get("tools", [])
            current_tools = list(self.registry.get_tools().keys())
            if sorted(cached_tools) == sorted(current_tools):
                self._tool_names = cached_tools
                self._tool_vectors = data.get("vectors", [])
                return True
        except Exception:
            pass
        return False

    def ensure_index(self) -> None:
        """Ensure tool vectors are loaded or built."""
        if (not self._tool_vectors or len(self._tool_vectors) != len(self.registry.get_tools())) and not self.load_cache():
            self.build_index()

    def retrieve(self, reasoning: str) -> list[Tool]:
        """Retrieve top-K tools matching the reasoning text plus any always-on tools."""
        self.ensure_index()
        all_tools = self.registry.get_tools()
        if not all_tools or not self._tool_vectors:
            return list(all_tools.values())

        reasoning_vecs = self._embed_texts([reasoning])
        if not reasoning_vecs:
            return list(all_tools.values())
        query_vec = reasoning_vecs[0]

        scored: list[tuple[float, str]] = []
        for name, vec in zip(self._tool_names, self._tool_vectors, strict=False):
            sim = _cosine_similarity(query_vec, vec)
            scored.append((sim, name))

        scored.sort(key=lambda x: x[0], reverse=True)

        selected_names: set[str] = set()
        # Add tools passing similarity threshold up to top_k
        for sim, name in scored[: self.config.top_k]:
            if sim >= self.config.similarity_threshold or not selected_names:
                selected_names.add(name)

        # Include always-on tools
        for always_on in self.config.always_on_tools:
            if always_on in all_tools:
                selected_names.add(always_on)

        # Fallback: if no tools selected, return all
        if not selected_names:
            return list(all_tools.values())

        return [all_tools[n] for n in selected_names if n in all_tools]

    def create_retrieved_registry(self, reasoning: str) -> ToolRegistry:
        """Create a fresh ToolRegistry populated only with retrieved tools."""
        retrieved = self.retrieve(reasoning)
        new_registry = ToolRegistry()
        for t in retrieved:
            new_registry._tools[t.name] = t
        return new_registry
