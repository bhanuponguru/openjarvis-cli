"""OpenJarvis — the client-side orchestrator.

Routes a user's request across a generalist and a team of specialists via LangGraph.
"""

try:
    from openjarvis._version import __version__
except ImportError:
    from importlib.metadata import version as _get_version

    __version__ = _get_version("openjarvis-cli")
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
