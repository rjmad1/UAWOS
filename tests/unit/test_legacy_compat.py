# tests/unit/test_legacy_compat.py
import uawos_objective
import uawos_budget
import uawos_governance
import uawos_planning
import uawos_workflow
import uawos_action
import uawos_outcome
import uawos_memory


def test_legacy_objective():
    """Verify legacy objective wrapper self tests pass."""
    uawos_objective.run_self_tests()


def test_legacy_budget():
    """Verify legacy budget wrapper self tests pass."""
    uawos_budget.run_self_tests()


def test_legacy_governance():
    """Verify legacy governance wrapper self tests pass."""
    uawos_governance.run_self_tests()


def test_legacy_planning():
    """Verify legacy planning wrapper self tests pass."""
    uawos_planning.run_self_tests()


def test_legacy_workflow():
    """Verify legacy workflow wrapper self tests pass."""
    uawos_workflow.run_self_tests()


def test_legacy_action():
    """Verify legacy action wrapper self tests pass."""
    uawos_action.run_self_tests()


def test_legacy_outcome():
    """Verify legacy outcome wrapper self tests pass."""
    uawos_outcome.run_self_tests()


def test_legacy_memory():
    """Verify legacy memory wrapper self tests pass."""
    uawos_memory.run_self_tests()
