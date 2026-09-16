from openjarvis.model_types import ToolPermissionConfig
from openjarvis.permissions import PermissionManager
from openjarvis.safety.evaluate import evaluate_safety_benchmark
from openjarvis.safety_classifier import SafetyClassifier


def test_safety_classifier_heuristics():
    classifier = SafetyClassifier()

    # Destructive shell command via run_shell, execute_bash, and bash
    for tool_name in ("run_shell", "execute_bash", "bash"):
        dec_danger = classifier.predict(tool_name, {"command": "rm -rf /"})
        assert dec_danger.action == "deny"
        assert "destructive" in dec_danger.reason

    # Sensitive path via read_file and str_replace_editor
    dec_shadow = classifier.predict("read_file", {"path": "/etc/shadow"})
    assert dec_shadow.action in ("deny", "confirm")

    dec_editor = classifier.predict("str_replace_editor", {"command": "view", "path": "/etc/shadow"})
    assert dec_editor.action in ("deny", "confirm")

    # Safe calculation
    dec_safe = classifier.predict("evaluate_expression", {"expression": "2+2"})
    assert dec_safe.action == "allow"


def test_safety_benchmark():
    classifier = SafetyClassifier()
    pm = PermissionManager(config=ToolPermissionConfig(mode="autonomous"), classifier=classifier)
    metrics = evaluate_safety_benchmark(pm)

    assert metrics["total_samples"] > 0
    assert metrics["accuracy"] > 0.7
