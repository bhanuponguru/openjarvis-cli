"""Heterogeneous Directed Cognitive Graph execution engine for OpenJarvis.

This module orchestrates communication between specialized model roles:
- Orchestrator (State evaluation and task routing)
- Coder (Code generation and surgical diff proposals)
- Reasoning (Mathematical and algorithmic derivation)
- Act (Tool execution and environment observation)

All state coordination occurs over a typed message protocol and a shared blackboard.
"""

from .blackboard import StateBlackboard
from .engine import CognitiveGraphEngine
from .protocol import (
    ActDirectiveMessage,
    ActObservationMessage,
    CodeDirectiveMessage,
    CodeProposalMessage,
    StrReplaceCommand,
    TaskCompleteMessage,
    TaskInitMessage,
)

__all__ = [
    "ActDirectiveMessage",
    "ActObservationMessage",
    "CodeDirectiveMessage",
    "CodeProposalMessage",
    "CognitiveGraphEngine",
    "StateBlackboard",
    "StrReplaceCommand",
    "TaskCompleteMessage",
    "TaskInitMessage",
]

