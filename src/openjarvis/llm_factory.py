import os
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from .model_types import SpecialistConfig


def create_chat_model(config: SpecialistConfig, api_key: str | None = None, **extra_kwargs: Any) -> BaseChatModel:
    kwargs: dict[str, Any] = {
        "model": config.model,
        "temperature": config.temperature,
    }
    if config.max_tokens:
        kwargs["max_tokens"] = config.max_tokens
    if config.stop:
        kwargs["stop"] = config.stop
    
    kwargs.update(extra_kwargs)

    provider = config.provider.lower()
    
    def resolve_api_key() -> str | None:
        if api_key:
            return api_key
        if config.api_key_env and config.api_key_env in os.environ:
            return os.environ[config.api_key_env]
        return None

    if provider in ("openai", "custom"):
        from langchain_openai import ChatOpenAI
        resolved_key = resolve_api_key()
        if resolved_key:
            kwargs["api_key"] = resolved_key
        elif "api_key" not in kwargs:
            env_key = os.environ.get("OPENAI_API_KEY")
            kwargs["api_key"] = env_key if env_key else "dummy"
        if config.base_url:
            kwargs["base_url"] = config.base_url
        return ChatOpenAI(**kwargs)
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        resolved_key = resolve_api_key()
        if resolved_key:
            kwargs["api_key"] = resolved_key
        if config.base_url:
            kwargs["base_url"] = config.base_url
        return ChatAnthropic(**kwargs)
    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        resolved_key = resolve_api_key()
        if resolved_key:
            kwargs["google_api_key"] = resolved_key
        return ChatGoogleGenerativeAI(**kwargs)
    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        if config.base_url:
            kwargs["base_url"] = config.base_url
        return ChatOllama(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")
