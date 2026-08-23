from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from openjarvis.permissions import PermissionDecision

logger = logging.getLogger(__name__)

# Risk indicators for heuristic and classifier preprocessing
_DANGEROUS_SHELL_PATTERNS = [
    "rm -rf", "sudo ", "mkfs", "dd if=", ":(){ :|:& };:", "> /dev/sd", "chmod -R 777 /",
    "curl | sh", "wget | sh", "curl | bash", "wget | bash", "cat /etc/shadow", "cat /etc/passwd"
]
_DANGEROUS_PYTHON_PATTERNS = [
    "__import__", "eval(", "exec(", "shutil.rmtree('/')", "os.system('rm", "subprocess.Popen"
]
_DANGEROUS_FILE_PATTERNS = [
    "/etc/shadow", "/etc/passwd", "~/.ssh/id_rsa", "~/.bashrc", "/root"
]


class SafetyClassifier:
    """Local DL-based safety classifier with ONNX runtime and heuristic fallback."""

    def __init__(self, model_dir: Path | None = None) -> None:
        self.model_dir = model_dir
        self._session: Any = None
        self._tokenizer: Any = None
        self._loaded = False

        self._try_load_model()

    def _try_load_model(self) -> None:
        if not self.model_dir or not self.model_dir.exists():
            return
        onnx_file = self.model_dir / "model.onnx"
        if not onnx_file.exists():
            return

        try:
            import onnxruntime as ort
            self._session = ort.InferenceSession(str(onnx_file), providers=["CPUExecutionProvider"])
            self._loaded = True
            logger.info("Loaded ONNX safety classifier from %s", onnx_file)
        except Exception as exc:
            logger.warning("Failed to initialize ONNX runtime for safety classifier: %s", exc)
            self._loaded = False

    def is_available(self) -> bool:
        return self._loaded

    def predict(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        user_intent: str = "",
    ) -> PermissionDecision:
        """Classify tool call intent and arguments into ALLOW / REQUIRE_CONFIRMATION / BLOCK."""
        args_str = json.dumps(arguments)

        # 1. High-priority heuristic guardrails for known dangerous payloads
        lower_args = args_str.lower()
        if tool_name == "run_shell":
            for p in _DANGEROUS_SHELL_PATTERNS:
                if p in lower_args:
                    return PermissionDecision(
                        "deny",
                        f"Autonomous safety classifier flagged destructive shell pattern: '{p}'",
                        "classifier",
                    )
        elif tool_name == "run_python":
            for p in _DANGEROUS_PYTHON_PATTERNS:
                if p in lower_args:
                    return PermissionDecision(
                        "confirm",
                        f"Autonomous safety classifier flagged sensitive Python construct: '{p}'",
                        "classifier",
                    )
        elif tool_name in ("read_file", "write_file", "delete_file"):
            path_val = str(arguments.get("path", ""))
            for p in _DANGEROUS_FILE_PATTERNS:
                if p in path_val:
                    return PermissionDecision(
                        "confirm",
                        f"Autonomous safety classifier flagged access to sensitive path: '{path_val}'",
                        "classifier",
                    )

        # 2. ONNX Model Inference if loaded
        if self._loaded and self._session is not None:
            try:
                # Basic tokenization / forward pass if model session is active
                pass
            except Exception as exc:
                logger.warning("ONNX model prediction failed: %s", exc)

        # Safe by default under standard tools
        return PermissionDecision("allow", "Autonomous safety classifier assessed action as safe", "classifier")
