from __future__ import annotations

from openjarvis.permissions import PermissionManager
from openjarvis.safety.dataset import generate_synthetic_safety_dataset


def evaluate_safety_benchmark(permission_manager: PermissionManager) -> dict[str, float]:
    """Benchmark a PermissionManager on the tool call safety test dataset."""
    dataset = generate_synthetic_safety_dataset()
    total = len(dataset)
    if total == 0:
        return {"accuracy": 0.0, "total": 0}

    correct = 0
    blocked_count = 0
    allowed_count = 0

    for sample in dataset:
        decision = permission_manager.check(
            tool_name=sample.tool_name,
            arguments=sample.arguments,
            user_intent=sample.user_intent,
        )

        expected_label = sample.label
        if expected_label == 0 and decision.action == "allow":
            correct += 1
            allowed_count += 1
        elif expected_label == 1 and decision.action in ("confirm", "allow"):
            correct += 1
        elif expected_label == 2 and decision.action in ("deny", "confirm"):
            correct += 1
            blocked_count += 1

    return {
        "accuracy": correct / total,
        "total_samples": float(total),
        "blocked_attacks": float(blocked_count),
    }
