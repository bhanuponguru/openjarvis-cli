"""MkDocs Macros module for dynamic documentation variables."""

import openjarvis


def define_env(env):
    """Define dynamic variables for MkDocs templates and markdown pages."""
    env.variables["version"] = openjarvis.__version__
