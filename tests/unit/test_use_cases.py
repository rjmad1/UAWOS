# tests/unit/test_use_cases.py
import pytest
from application.use_cases import (
    objective_use_cases,
    billing_use_cases,
    governance_use_cases,
    planning_use_cases,
    workflow_use_cases,
    action_use_cases,
    outcome_use_cases,
    memory_use_cases,
)


def test_objective_use_cases():
    """Verify clean architecture use cases for objectives."""
    # Reset/Clean state
    state = objective_use_cases.get_default_state()
    objective_use_cases.save_state(objective_use_cases.STATE_FILE, state)

    obj = objective_use_cases.create_objective_from_input(
        "Voice transcript: setup postgres DB immediately", "voice", "Lead Engineer", "CPO"
    )
    assert obj["source_type"] == "voice"
    assert obj["owner"] == "Lead Engineer"
    assert obj["sponsor"] == "CPO"

    conflicts = objective_use_cases.detect_objective_conflicts()
    assert isinstance(conflicts, list)


def test_billing_use_cases():
    """Verify clean architecture use cases for billing and budgets."""
    # Reset/Clean state
    state = billing_use_cases.get_default_state()
    billing_use_cases.save_state(billing_use_cases.STATE_FILE, state)

    summary = billing_use_cases.get_summary()
    assert "metrics" in summary
    assert "objective_budgets" in summary

    # Allocate budget
    obj_budget = billing_use_cases.allocate_objective_budget("OBJ-101", "Launch Product X", 2000.0)
    assert obj_budget["budget"] == 2000.0


def test_governance_use_cases():
    """Verify clean architecture use cases for governance."""
    # Reset/Clean state
    state = governance_use_cases.get_default_state()
    governance_use_cases.save_state(governance_use_cases.STATE_FILE, state)

    # Evaluate action
    res = governance_use_cases.evaluate_action_governance("ACT-TEST", {"estimated_tokens": 1000})
    assert res["verdict"] == "APPROVED"


def test_planning_use_cases():
    """Verify clean architecture use cases for planning."""
    # Reset/Clean state
    state = planning_use_cases.get_default_state()
    planning_use_cases.save_state(planning_use_cases.STATE_FILE, state)

    plans = planning_use_cases.generate_plans("OBJ-101")
    assert len(plans) > 0


def test_workflow_use_cases():
    """Verify clean architecture use cases for workflows."""
    # Reset/Clean state
    state = workflow_use_cases.get_default_state()
    workflow_use_cases.save_state(workflow_use_cases.STATE_FILE, state)

    wf = workflow_use_cases.create_workflow("PLN-101", "Test Title", ["task 1"])
    assert wf["title"] == "Test Title"
    assert "task 1" in wf["tasks"]


def test_action_use_cases():
    """Verify clean architecture use cases for actions."""
    # Reset/Clean state
    state = action_use_cases.get_default_state()
    action_use_cases.save_state(action_use_cases.STATE_FILE, state)

    action = action_use_cases.create_action("WRK-101", "Test Action")
    assert action["name"] == "Test Action"
    assert action["workflow_id"] == "WRK-101"


def test_outcome_use_cases():
    """Verify clean architecture use cases for outcomes."""
    # Reset/Clean state
    state = outcome_use_cases.get_default_state()
    outcome_use_cases.save_state(outcome_use_cases.STATE_FILE, state)

    outcome = outcome_use_cases.create_outcome("OBJ-101", "Test Outcome", "Metric", "units")
    assert outcome["title"] == "Test Outcome"
    assert outcome["metric"] == "Metric"


def test_memory_use_cases():
    """Verify clean architecture use cases for memory."""
    # Reset/Clean state
    state = memory_use_cases.get_default_state()
    memory_use_cases.save_state(memory_use_cases.STATE_FILE, state)

    memory = memory_use_cases.append_memory("Test Content")
    assert memory["content"] == "Test Content"
    assert memory["scope"] == "workspace"
