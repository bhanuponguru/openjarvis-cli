from dataclasses import dataclass, field


@dataclass
class SpecialistConfig:
    name: str
    system_prompt: str
    description: str | None = None
    provider: str = "openai"
    base_url: str = "http://localhost:11434/v1"
    model: str = "llama3"
    api_key_env: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    stop: list[str] = field(default_factory=list)
    timeout: float = 60.0
    delegates_to: list[str] = field(default_factory=list)
    tools: list[str] | None = None


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
class AgentProfileConfig:
    name: str
    role: str = "generalist"
    description: str | None = None
    system_prompt: str = ""
    provider: str = "openai"
    base_url: str = "http://localhost:11434/v1"
    model: str = "llama3"
    api_key_env: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    stop: list[str] = field(default_factory=list)
    timeout: float = 60.0
    tools: list[str] | None = None
    allowed_specialists: list[str] = field(default_factory=list)
    max_hops: int = 10


@dataclass
class MultiAgentLimitsConfig:
    max_active_agents: int = 8
    max_spawn_depth: int = 3
    max_agent_turns: int = 15
    turn_timeout_seconds: float = 300.0


@dataclass
class ConductorConfig:
    root_agent: AgentProfileConfig | None = None
    agents: dict[str, AgentProfileConfig] = field(default_factory=dict)
    generalist: SpecialistConfig = field(
        default_factory=lambda: SpecialistConfig(name="generalist", system_prompt="You are OpenJarvis.")
    )
    specialists: dict[str, SpecialistConfig] = field(default_factory=dict)
    # Hard cap on LLM calls per user message for a single conductor.
    max_hops: int = 10
    tool_retrieval: ToolRetrievalConfig = field(default_factory=ToolRetrievalConfig)
    tool_permissions: ToolPermissionConfig = field(default_factory=ToolPermissionConfig)
    limits: MultiAgentLimitsConfig = field(default_factory=MultiAgentLimitsConfig)


