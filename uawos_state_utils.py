# uawos_state_utils.py
"""Backward compatibility wrapper. Proxies state load/save operations to the target infrastructure package."""
from infrastructure.storage.json_fallback_store import load_state, save_state, state_transaction

__all__ = ["load_state", "save_state", "state_transaction"]
