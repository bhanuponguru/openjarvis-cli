"""Heterogeneous Directed Cognitive Graph execution engine for OpenJarvis.

This module orchestrates communication between specialized models:
- jarvis-orchestrator-mark1-300m
- jarvis-coder-mark1-1.1b
- jarvis-reasoning-mark1-1.1b
- jarvis-act-mark1-135m

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

