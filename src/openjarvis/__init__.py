"""OpenJarvis — the client-side orchestrator.

Routes a user's request across a generalist and a team of specialists, all
reached over an OpenAI-compatible HTTP API. It is deliberately model-agnostic:
nothing here knows or cares whether the backend is jarvis, Ollama, or OpenAI.
"""

from openjarvis.builtin_tools import create_builtin_registry
from openjarvis.conductor import Conductor
from openjarvis.model_types import ConductorConfig, SpecialistConfig

__all__ = ["Conductor", "ConductorConfig", "SpecialistConfig", "create_builtin_registry"]
