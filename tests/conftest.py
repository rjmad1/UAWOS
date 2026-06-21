# tests/conftest.py
import os
import pytest
from shared.utilities.context import set_context, reset_context


@pytest.fixture(autouse=True)
def setup_test_context():
    """Automatically set and clean up default tenant context for tests."""
    tokens = set_context("default_tenant", "Developer", "system")
    yield
    reset_context(tokens)


@pytest.fixture(autouse=True, scope="session")
def configure_test_state_directory(tmp_path_factory):
    """Automatically isolate state files in a temporary directory for test duration."""
    test_state_dir = tmp_path_factory.mktemp("uawos_test_state")
    os.environ["UAWOS_STATE_DIR"] = str(test_state_dir)
    yield
    if "UAWOS_STATE_DIR" in os.environ:
        del os.environ["UAWOS_STATE_DIR"]
