# uawos_context.py
"""Backward compatibility wrapper. Proxies context propagation to the target shared package."""
from shared.utilities.context import get_tenant_id, get_actor_role, get_actor_owner, set_context, reset_context

__all__ = ["get_tenant_id", "get_actor_role", "get_actor_owner", "set_context", "reset_context"]
