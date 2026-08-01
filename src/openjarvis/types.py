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
class ConductorConfig:
    generalist: SpecialistConfig
    specialists: dict[str, SpecialistConfig] = field(default_factory=dict)
    # Hard cap on LLM calls per user message. Without it a pair of models that
    # keep routing to each other spins forever, burning tokens with no output.
    # On reaching the cap the conductor forces a final generalist answer rather
    # than raising -- a degraded answer beats an exception.
    max_hops: int = 10
