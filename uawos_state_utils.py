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
    """Load state from PostgreSQL database if online, falling back to local JSON file."""
    import inspect

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

    # Try database first
    db_ok = False
    try:
        import uawos_db
        if uawos_db.DB_AVAILABLE:
            key = _get_db_key(state_file)
            conn = uawos_db.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT state FROM uawos_state WHERE key = %s AND tenant_id = %s;", (key, tenant_id))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            db_ok = True
            if row:
                state = row[0]
                if isinstance(state, str):
                    return json.loads(state)
                return state
    except Exception:
        pass

    # Fallback to local JSON file
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                # If DB is online but has no state record, seed it
                if db_ok:
                    try:
                        import uawos_db
                        uawos_db.db_save_state(_get_db_key(state_file), state, tenant_id)
                    except Exception:
                        pass
                return state
        except Exception:
            pass

    # Fallback to default state
    state = default_state_func()
    save_state(state_file, state, tenant_id)
    return state


def save_state(state_file: str = None, state: Any = None, tenant_id: str = "default_tenant"):
    """Save state to PostgreSQL database and local JSON file."""
    import inspect

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

    # Try saving to DB
    db_saved = False
    try:
        import uawos_db
        if uawos_db.DB_AVAILABLE:
            conn = uawos_db.get_db_connection()
            conn.close()
            uawos_db.db_save_state(_get_db_key(state_file), state, tenant_id)
            db_saved = True
    except Exception:
        pass

    # Dual-write/fallback to JSON file
    try:
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        if not db_saved:
            print(f"Error saving state to file (and DB was unavailable): {e}")
