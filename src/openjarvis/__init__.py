"""OpenJarvis — the client-side orchestrator.

Routes a user's request across a generalist and a team of specialists via LangGraph.
"""

from openjarvis._version import __version__
from openjarvis.builtin_tools import create_builtin_registry
from openjarvis.conductor import Conductor
from openjarvis.llm_factory import create_chat_model
from openjarvis.model_types import ConductorConfig, SpecialistConfig
from openjarvis.workspace import Workspace

__all__ = [
    "Conductor",
    "ConductorConfig",
    "SpecialistConfig",
    "Workspace",
    "__version__",
    "create_builtin_registry",
    "create_chat_model",
]
