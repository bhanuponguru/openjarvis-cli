from __future__ import annotations

import fnmatch
import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from openjarvis.model_types import ToolPermissionConfig
from openjarvis.workspace import Workspace, get_current_workspace

logger = logging.getLogger(__name__)


@dataclass
class PermissionDecision:
    action: str  # "allow" | "deny" | "confirm"
    reason: str
    rule_source: str = "default"  # "blocklist" | "allowlist" | "pattern" | "remembered" | "mode" | "classifier"


class PermissionManager:
    """Evaluates tool call security and enforces guardrails based on modes and rules."""

    def __init__(
        self,
        config: ToolPermissionConfig | None = None,
        workspace: Workspace | None = None,
        confirm_callback: Callable[[str, dict[str, Any], str], bool] | None = None,
        classifier: Any = None,
    ) -> None:
        self.config = config or ToolPermissionConfig()
        self.workspace = workspace or get_current_workspace()
        self.confirm_callback = confirm_callback
        self.classifier = classifier

        self._load_persisted_permissions()

    def _get_permissions_file(self, scope: str = "local") -> Path:
        if scope == "local" and self.workspace.local_root:
            return self.workspace.local_root / "config" / "permissions.yaml"
        return self.workspace.global_root / "config" / "permissions.yaml"

    def _load_persisted_permissions(self) -> None:
        # Load global then local permissions.yaml if present
        for scope in ("global", "local"):
            try:
                p = self._get_permissions_file(scope=scope)
                if p.exists():
                    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                    if "mode" in data:
                        self.config.mode = data["mode"]
                    if "allowed_tools" in data:
                        self.config.allowed_tools = list(set(self.config.allowed_tools + data["allowed_tools"]))
                    if "blocked_tools" in data:
                        self.config.blocked_tools = list(set(self.config.blocked_tools + data["blocked_tools"]))
                    if "rules" in data and isinstance(data["rules"], dict):
                        self.config.rules.update(data["rules"])
                    if "remembered_decisions" in data and isinstance(data["remembered_decisions"], dict):
                        self.config.remembered_decisions.update(data["remembered_decisions"])
            except Exception as exc:
                logger.warning("Failed to load permissions: %s", exc)

    def save_permissions(self, scope: str = "local") -> None:
        p = self._get_permissions_file(scope=scope)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "mode": self.config.mode,
                "allowed_tools": self.config.allowed_tools,
                "blocked_tools": self.config.blocked_tools,
                "rules": self.config.rules,
                "remembered_decisions": self.config.remembered_decisions,
            }
            p.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
        except OSError as exc:
            logger.warning("Failed to save permissions to %s: %s", p, exc)

    def remember_decision(self, tool_name: str, decision: str, scope: str = "local") -> None:
        """Persist an 'always allow' or 'always block' decision for a tool."""
        self.config.remembered_decisions[tool_name] = decision
        if decision == "allow" and tool_name not in self.config.allowed_tools:
            self.config.allowed_tools.append(tool_name)
        elif decision == "deny" and tool_name not in self.config.blocked_tools:
            self.config.blocked_tools.append(tool_name)
        self.save_permissions(scope=scope)

    def check(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        user_intent: str = "",
    ) -> PermissionDecision:
        """Evaluate tool call against security rules and permission mode."""
        # 1. Global Blocklist
        if tool_name in self.config.blocked_tools:
            return PermissionDecision("deny", f"Tool '{tool_name}' is blocked by security policy", "blocklist")

        # 2. Remembered Decisions
        if tool_name in self.config.remembered_decisions:
            dec = self.config.remembered_decisions[tool_name]
            if dec == "allow":
                return PermissionDecision("allow", f"Tool '{tool_name}' was previously allowed by user", "remembered")
            elif dec == "deny":
                return PermissionDecision("deny", f"Tool '{tool_name}' was previously blocked by user", "remembered")

        # 3. Per-Tool-Per-Argument Pattern Rules
        if tool_name in self.config.rules:
            rule_def = self.config.rules[tool_name]
            patterns = rule_def.get("argument_patterns", [])
            for p in patterns:
                match_spec = p.get("match", {})
                action = p.get("action", "confirm")
                matched = True
                for arg_key, pattern in match_spec.items():
                    val = str(arguments.get(arg_key, ""))
                    if not fnmatch.fnmatch(val, pattern):
                        matched = False
                        break
                if matched:
                    return PermissionDecision(action, f"Matches rule pattern for {tool_name}", "pattern")

            if "default_action" in rule_def:
                return PermissionDecision(rule_def["default_action"], f"Default rule action for {tool_name}", "pattern")

        # 4. Global Allowlist
        if tool_name in self.config.allowed_tools:
            return PermissionDecision("allow", f"Tool '{tool_name}' is in allowed_tools list", "allowlist")

        # 5. Safety Classifier (Autonomous Mode)
        if self.config.mode == "autonomous" and self.classifier is not None:
            try:
                pred = self.classifier.predict(tool_name, arguments, user_intent)
                if pred is not None:
                    return pred
            except Exception as exc:
                logger.warning("Classifier prediction failed: %s", exc)

        # 6. Mode-based default
        if self.config.mode == "autonomous":
            return PermissionDecision("allow", "Autonomous mode allowed execution", "mode")
        elif self.config.mode == "allowlist":
            return PermissionDecision("confirm", f"Tool '{tool_name}' is not on pre-approved allowlist", "mode")
        else:  # interactive mode
            return PermissionDecision("confirm", f"Interactive confirmation required for '{tool_name}'", "mode")
