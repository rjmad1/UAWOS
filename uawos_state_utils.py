# uawos_state_utils.py
"""Utility functions for loading and saving persistent JSON state files.
These helpers replace duplicated code across many uawos_*.py modules.
"""

import os
from collections.abc import Callable
from typing import Any


def _get_db_key(state_file: str) -> str:
    return os.path.splitext(os.path.basename(state_file))[0]


def load_state(state_file: str = None, default_state_func: Callable[[], Any] = None, tenant_id: str = "default_tenant"):
    """Load state from PostgreSQL database, falling back to local JSON file if offline."""
    import inspect
    import json
    import sys

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
        raise ValueError("STATE_FILE and get_default_state must be defined in the caller module or passed explicitly.")

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
        # DB is offline or errored - fall back to local JSON file
        sys.stderr.write(f"WARNING: PostgreSQL database offline ({e}). Falling back to local JSON file state: {state_file}\n")
        
        if os.path.exists(state_file):
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as file_err:
                sys.stderr.write(f"ERROR: Failed to read local JSON state file: {file_err}\n")

        # Seed default state if local JSON doesn't exist
        state = default_state_func()
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
        except Exception as file_err:
            sys.stderr.write(f"ERROR: Failed to write default state to local JSON file: {file_err}\n")
        return state

    # Seed default state if not found in database, then save it to database.
    state = default_state_func()
    save_state(state_file, state, tenant_id)
    return state


def save_state(state_file: str = None, state: Any = None, tenant_id: str = "default_tenant"):
    """Save state to PostgreSQL database, falling back to local JSON file if offline."""
    import inspect
    import json
    import sys

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
        sys.stderr.write(f"WARNING: PostgreSQL database offline ({e}). Falling back to local JSON file save: {state_file}\n")
        
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
        except Exception as file_err:
            raise RuntimeError(f"Failed to write state to local JSON file: {file_err}") from file_err


import contextlib
import hashlib

@contextlib.contextmanager
def state_transaction(state_file: str = None, tenant_id: str = "default_tenant"):
    """Context manager to perform state read-modify-write operations under a PostgreSQL advisory lock."""
    import inspect
    from uawos_context import get_tenant_id

    # Resolve state_file if not provided
    if state_file is None:
        # Go up 2 stack frames: contextmanager generator block is frame 1, caller is frame 2
        try:
            caller_globals = inspect.stack()[2].frame.f_globals
            state_file = caller_globals.get("STATE_FILE")
        except Exception:
            pass
    if state_file is None:
        raise ValueError("STATE_FILE must be defined in the caller or passed explicitly.")

    if tenant_id == "default_tenant":
        tenant_id = get_tenant_id()

    key = _get_db_key(state_file)
    lock_id = int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**31 - 1)

    acquired = False
    try:
        import uawos_memory
        uawos_memory.acquire_advisory_lock(lock_id)
        acquired = True
    except Exception as e:
        import sys
        sys.stderr.write(f"WARNING: PostgreSQL offline, executing state transaction without advisory lock ({e})\n")

    try:
        yield
    finally:
        if acquired:
            try:
                import uawos_memory
                uawos_memory.release_advisory_lock(lock_id)
            except Exception as e:
                import sys
                sys.stderr.write(f"ERROR: Failed to release state advisory lock ({e})\n")
