"""OpenJarvis — the client-side orchestrator.

Routes a user's request across a generalist and a team of specialists, all
reached over an OpenAI-compatible HTTP API. It is deliberately model-agnostic:
nothing here knows or cares whether the backend is jarvis, Ollama, or OpenAI.
"""

from openjarvis.conductor import Conductor
from openjarvis.types import ConductorConfig, SpecialistConfig

__all__ = ["Conductor", "ConductorConfig", "SpecialistConfig"]
