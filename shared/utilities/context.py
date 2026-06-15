# shared/utilities/context.py
from contextvars import ContextVar

# Define thread-safe ContextVar primitives
_tenant_id = ContextVar("tenant_id", default="default_tenant")
_actor_role = ContextVar("actor_role", default="Developer")
_actor_owner = ContextVar("actor_owner", default="system")


def get_tenant_id() -> str:
    """Retrieve the active tenant ID from request context."""
    return _tenant_id.get()


def get_actor_role() -> str:
    """Retrieve the active user/agent role from request context."""
    return _actor_role.get()


def get_actor_owner() -> str:
    """Retrieve the active user/agent owner identifier from request context."""
    return _actor_owner.get()


def set_context(tenant_id: str, role: str, owner: str):
    """Set the active context variables for the current thread/task context.
    Returns a tuple of tokens that can be used to reset the context later.
    """
    token_tenant = _tenant_id.set(tenant_id)
    token_role = _actor_role.set(role)
    token_owner = _actor_owner.set(owner)
    return token_tenant, token_role, token_owner


def reset_context(tokens):
    """Reset the context variables to their previous values using tokens."""
    token_tenant, token_role, token_owner = tokens
    _tenant_id.reset(token_tenant)
    _actor_role.reset(token_role)
    _actor_owner.reset(token_owner)
