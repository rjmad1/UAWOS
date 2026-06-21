# uawos_context.py
"""Backward compatibility wrapper. Proxies context propagation to the target shared package."""

from shared.utilities.context import get_actor_owner, get_actor_role, get_tenant_id, reset_context, set_context

__all__ = ["get_tenant_id", "get_actor_role", "get_actor_owner", "set_context", "reset_context"]
