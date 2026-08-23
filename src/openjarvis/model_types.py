from dataclasses import dataclass, field


@dataclass
class SpecialistConfig:
    name: str
    system_prompt: str
    provider: str = "openai"
    base_url: str = "http://localhost:11434/v1"
    model: str = "llama3"
    api_key_env: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    stop: list[str] = field(default_factory=list)
    timeout: float = 60.0
    delegates_to: list[str] = field(default_factory=list)


@dataclass
class ToolRetrievalConfig:
    enabled: bool = False
    top_k: int = 5
    similarity_threshold: float = 0.35
    always_on_tools: list[str] = field(default_factory=list)


@dataclass
class ToolPermissionConfig:
    mode: str = "interactive"  # interactive | allowlist | autonomous
    allowed_tools: list[str] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)
    rules: dict[str, dict] = field(default_factory=dict)
    remembered_decisions: dict[str, str] = field(default_factory=dict)


@dataclass
class ConductorConfig:
    generalist: SpecialistConfig
    specialists: dict[str, SpecialistConfig] = field(default_factory=dict)
    # Hard cap on LLM calls per user message. Without it a pair of models that
    # keep routing to each other spins forever, burning tokens with no output.
    # On reaching the cap the conductor forces a final generalist answer rather
    # than raising -- a degraded answer beats an exception.
    max_hops: int = 10
    tool_retrieval: ToolRetrievalConfig = field(default_factory=ToolRetrievalConfig)
    tool_permissions: ToolPermissionConfig = field(default_factory=ToolPermissionConfig)

