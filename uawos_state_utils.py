# uawos_state_utils.py
"""Utility functions for loading and saving persistent JSON state files.
These helpers replace duplicated code across many uawos_*.py modules.
"""

import json
import os
from typing import Callable, Any


def load_state(state_file: str = None, default_state_func: Callable[[], Any] = None):
    """Load JSON state with flexible parameters.
    If *state_file* is omitted, the function attempts to locate a ``STATE_FILE``
    variable in the caller's global namespace. Likewise, if *default_state_func*
    is omitted, it looks for a ``get_default_state`` callable. This preserves the
    original simple ``load_state()`` usage throughout the codebase while still
    supporting explicit arguments where needed.
    """
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
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Fallback to default state
    state = default_state_func()
    save_state(state_file, state)
    return state


def save_state(state_file: str = None, state: Any = None):
    """Persist *state* as JSON to *state_file*.
    If *state_file* is omitted, the function looks for a ``STATE_FILE`` constant
    in the caller's globals. The *state* argument may be passed as the sole
    positional parameter for backward compatibility.
    """
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
    try:
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving state to {state_file}: {e}")
