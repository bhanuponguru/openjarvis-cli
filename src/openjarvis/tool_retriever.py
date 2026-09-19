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
                    "vocab": self._fallback_embedder.vocab if self._fallback_embedder else None,
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
                cached_vocab = data.get("vocab")
                if self._fallback_embedder is not None:
                    if cached_vocab and isinstance(cached_vocab, dict):
                        self._fallback_embedder.vocab = cached_vocab
                    else:
                        descriptions = [
                            _format_tool_for_embedding(self.registry.get_tools()[name])
                            for name in self._tool_names
                        ]
                        self._fallback_embedder.fit_transform(descriptions)
                return True
        except Exception:
            pass
        return False

    def ensure_index(self) -> None:
        """Ensure tool vectors are loaded or built."""
        if (not self._tool_vectors or len(self._tool_vectors) != len(self.registry.get_tools())) and not self.load_cache():
            self.build_index()

    def retrieve(
        self,
        reasoning: str,
        allowed_tools: list[str] | set[str] | None = None,
    ) -> list[Tool]:
        """Retrieve top-K tools matching the reasoning text plus any always-on tools.

        If allowed_tools is specified, candidate tools, similarity ranking, and
        always-on inclusion are strictly constrained to that permitted subset.
        """
        self.ensure_index()
        all_tools = self.registry.get_tools()
        if not all_tools:
            return []

        allowed_set = set(allowed_tools) if allowed_tools is not None else None
        if allowed_set is not None:
            candidate_tools = {k: v for k, v in all_tools.items() if k in allowed_set}
        else:
            candidate_tools = dict(all_tools)

        if not candidate_tools:
            return []

        if not self._tool_vectors:
            return list(candidate_tools.values())

        reasoning_vecs = self._embed_texts([reasoning])
        if not reasoning_vecs:
            return list(candidate_tools.values())
        query_vec = reasoning_vecs[0]

        scored: list[tuple[float, str]] = []
        for name, vec in zip(self._tool_names, self._tool_vectors, strict=False):
            if allowed_set is not None and name not in allowed_set:
                continue
            sim = _cosine_similarity(query_vec, vec)
            scored.append((sim, name))

        scored.sort(key=lambda x: x[0], reverse=True)

        selected_names: set[str] = set()
        # Add tools passing similarity threshold up to top_k
        for sim, name in scored[: self.config.top_k]:
            if sim >= self.config.similarity_threshold or not selected_names:
                selected_names.add(name)

        # Include always-on tools, constrained to permitted candidates
        for always_on in self.config.always_on_tools:
            if always_on in candidate_tools:
                selected_names.add(always_on)

        # Fallback: if no tools selected, return all candidates (never unpermitted tools)
        if not selected_names:
            return list(candidate_tools.values())

        return [candidate_tools[n] for n in selected_names if n in candidate_tools]

    def create_retrieved_registry(
        self,
        reasoning: str,
        allowed_tools: list[str] | set[str] | None = None,
    ) -> ToolRegistry:
        """Create a fresh ToolRegistry populated only with retrieved tools."""
        retrieved = self.retrieve(reasoning, allowed_tools=allowed_tools)
        new_registry = ToolRegistry()
        for t in retrieved:
            new_registry._tools[t.name] = t
        return new_registry
