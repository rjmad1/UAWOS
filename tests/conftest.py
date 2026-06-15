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
