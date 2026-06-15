# domains/objective/scoring.py
from typing import List
from .objective import Objective


def calculate_health(
    objective: Objective,
    in_cycle: bool,
    dependency_statuses: List[str],
    budget_verdict: str = "APPROVED",
    has_outcomes: bool = True,
) -> float:
    """Calculate the health score of an objective based on domain rules."""
    health = 100.0

    # 1. Circular dependency penalty
    if in_cycle:
        health -= 30.0

    # 2. Dependency status penalty
    for status in dependency_statuses:
        if status == "cancelled":
            health -= 25.0
        elif status == "paused":
            health -= 10.0

    # 3. Budget warning penalty
    if budget_verdict == "BREACHED":
        health -= 40.0
    elif budget_verdict == "WARNING":
        health -= 15.0

    # 4. Measurable outcomes penalty (Constitutional Law 1)
    if not has_outcomes:
        health -= 20.0

    return max(0.0, min(100.0, health))


def calculate_confidence(
    objective: Objective,
    has_conflict: bool,
) -> float:
    """Calculate the confidence score of an objective based on domain rules."""
    # Start with parser confidence (defaulting to 100.0 if not defined or reset)
    confidence = objective.confidence_score

    # 1. Missing owner/sponsor penalties
    if not objective.owner or objective.owner == "System Agent":
        confidence -= 10.0
    if not objective.sponsor or objective.sponsor == "CPO":
        confidence -= 10.0

    # 2. Active conflicts penalty
    if has_conflict:
        confidence -= 20.0

    return max(10.0, min(100.0, confidence))
