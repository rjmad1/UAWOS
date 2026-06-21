# infrastructure/storage/json_fallback_store.py
import contextlib
import hashlib
import inspect
import json
import os
import sys
import threading
from collections.abc import Callable
from typing import Any

from config.settings import settings
from shared.utilities.context import get_tenant_id

# Global lock repository to handle concurrent writes on file fallbacks
_file_locks = {}
_file_locks_lock = threading.Lock()


def _get_file_lock(filepath: str) -> threading.Lock:
    with _file_locks_lock:
        if filepath not in _file_locks:
            _file_locks[filepath] = threading.Lock()
        return _file_locks[filepath]


def _get_db_key(state_file: str) -> str:
    return os.path.splitext(os.path.basename(state_file))[0]


def _resolve_state_file(state_file: str) -> str:
    import tempfile

    if state_file and os.path.isabs(state_file):
        try:
            norm_state_file = os.path.normpath(state_file)
            temp_dir = os.path.normpath(tempfile.gettempdir())
            if os.name == "nt":
                import ctypes

                buf = ctypes.create_unicode_buffer(1024)
                if ctypes.windll.kernel32.GetLongPathNameW(norm_state_file, buf, 1024) > 0:
                    norm_state_file = buf.value
                buf = ctypes.create_unicode_buffer(1024)
                if ctypes.windll.kernel32.GetLongPathNameW(temp_dir, buf, 1024) > 0:
                    temp_dir = buf.value
            if norm_state_file.lower().startswith(temp_dir.lower()):
                return state_file
        except Exception:
            pass
    return os.path.join(settings.STATE_DIR, os.path.basename(state_file))


def load_state(state_file: str = None, default_state_func: Callable[[], Any] = None, tenant_id: str = "default_tenant"):
    """Load state from PostgreSQL database, falling back to local JSON file if offline."""
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

    state_file = _resolve_state_file(state_file)

    if tenant_id == "default_tenant":
        tenant_id = get_tenant_id()

    # Try database
    try:
        from infrastructure.database.db import DB_AVAILABLE, db_get_state

        if DB_AVAILABLE:
            key = _get_db_key(state_file)
            state = db_get_state(key, None, tenant_id)
            if state is not None:
                return state
        else:
            raise RuntimeError("PostgreSQL database is offline.")
    except Exception as e:
        # DB is offline or errored - fall back to local JSON file
        sys.stderr.write(
            f"WARNING: PostgreSQL database offline ({e}). Falling back to local JSON file state: {state_file}\n"
        )

        lock = _get_file_lock(state_file)
        with lock:
            if os.path.exists(state_file):
                try:
                    with open(state_file, encoding="utf-8") as f:
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

    state_file = _resolve_state_file(state_file)

    if tenant_id == "default_tenant":
        tenant_id = get_tenant_id()

    # Try saving to DB
    try:
        from infrastructure.database.db import DB_AVAILABLE, db_save_state

        if DB_AVAILABLE:
            db_save_state(_get_db_key(state_file), state, tenant_id)
            return
        else:
            raise RuntimeError("PostgreSQL database is offline.")
    except Exception as e:
        sys.stderr.write(
            f"WARNING: PostgreSQL database offline ({e}). Falling back to local JSON file save: {state_file}\n"
        )

        lock = _get_file_lock(state_file)
        with lock:
            try:
                with open(state_file, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=4)
            except Exception as file_err:
                raise RuntimeError(f"Failed to write state to local JSON file: {file_err}") from file_err


@contextlib.contextmanager
def state_transaction(state_file: str = None, tenant_id: str = "default_tenant"):
    """Context manager to perform state read-modify-write operations under a PostgreSQL advisory lock."""
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

    state_file = _resolve_state_file(state_file)

    if tenant_id == "default_tenant":
        tenant_id = get_tenant_id()

    key = _get_db_key(state_file)
    lock_id = int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**31 - 1)

    acquired = False
    try:
        from infrastructure.database.db import acquire_advisory_lock

        acquire_advisory_lock(lock_id)
        acquired = True
    except Exception as e:
        sys.stderr.write(f"WARNING: PostgreSQL offline, executing state transaction without advisory lock ({e})\n")

    try:
        yield
    finally:
        if acquired:
            try:
                from infrastructure.database.db import release_advisory_lock

                release_advisory_lock(lock_id)
            except Exception as e:
                sys.stderr.write(f"ERROR: Failed to release state advisory lock ({e})\n")
