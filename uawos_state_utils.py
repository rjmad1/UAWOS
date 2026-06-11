# uawos_state_utils.py
"""Utility functions for loading and saving persistent JSON state files.
These helpers replace duplicated code across many uawos_*.py modules.
"""

import json
import os
from typing import Callable, Any


def _get_db_key(state_file: str) -> str:
    return os.path.splitext(os.path.basename(state_file))[0]


def load_state(state_file: str = None, default_state_func: Callable[[], Any] = None, tenant_id: str = "default_tenant"):
    """Load state from PostgreSQL database, throwing error if offline."""
    import inspect
    from uawos_context import get_tenant_id

    # Resolve state_file if not provided
    if state_file is None:
        caller_globals = inspect.stack()[1].frame.f_globals
        state_file = caller_globals.get("STATE_FILE")
    # Resolve default_state_func if not provided
    if default_state_func is None:
        caller_globals = inspect.stack()[1].frame.f_globals
        default_state_func = caller_globals.get("get_default_state")
    if state_file is None or default_state_func is None:
        raise ValueError(
            "STATE_FILE and get_default_state must be defined in the caller module or passed explicitly."
        )

    if tenant_id == "default_tenant":
        tenant_id = get_tenant_id()

    # Try database
    try:
        import uawos_db
        if uawos_db.DB_AVAILABLE:
            key = _get_db_key(state_file)
            state = uawos_db.db_get_state(key, None, tenant_id)
            if state is not None:
                return state
        else:
            raise RuntimeError("PostgreSQL database is offline.")
    except Exception as e:
        raise RuntimeError(f"Database error loading state: {e}")

    # Plaintext file fallbacks are decommissioned in Wave 1.
    # Seed default state if not found in database, then save it to database.
    state = default_state_func()
    save_state(state_file, state, tenant_id)
    return state


def save_state(state_file: str = None, state: Any = None, tenant_id: str = "default_tenant"):
    """Save state to PostgreSQL database."""
    import inspect
    from uawos_context import get_tenant_id

    # Handle backward‑compatible signature where only state is provided
    if state is None and isinstance(state_file, dict):
        state = state_file
        # Resolve STATE_FILE from caller globals
        caller_globals = inspect.stack()[1].frame.f_globals
        state_file = caller_globals.get("STATE_FILE")
    if state_file is None:
        caller_globals = inspect.stack()[1].frame.f_globals
        state_file = caller_globals.get("STATE_FILE")
    if state_file is None or state is None:
        raise ValueError("STATE_FILE and state must be provided to save_state.")

    if tenant_id == "default_tenant":
        tenant_id = get_tenant_id()

    # Try saving to DB
    try:
        import uawos_db
        if uawos_db.DB_AVAILABLE:
            uawos_db.db_save_state(_get_db_key(state_file), state, tenant_id)
            return
        else:
            raise RuntimeError("PostgreSQL database is offline.")
    except Exception as e:
        raise RuntimeError(f"Database error saving state: {e}")
