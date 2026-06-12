# uawos_sdk.py
import json
import urllib.request

import uawos_context
import uawos_db
import uawos_memory
import uawos_objective


class UAWOSClientSDK:
    def __init__(self, base_url: str = "http://127.0.0.1:8099", tenant_id: str = "default_tenant"):
        self.base_url = base_url
        self.tenant_id = tenant_id

    def create_objective(self, title: str, description: str, priority: str = "Medium", owner: str = "") -> dict:
        """Programmatically create a new strategic objective."""
        tokens = uawos_context.set_context(self.tenant_id, "Developer", "system")
        try:
            obj = uawos_objective.create_objective(title=title, description=description, priority=priority, owner=owner)
            # Sync to the relational database to ensure consistency with DB-backed APIs
            uawos_db.db_save_objective(obj)
            return obj
        finally:
            uawos_context.reset_context(tokens)

    def get_objective_status(self, objective_id: str) -> str:
        """Query status of a specific objective."""
        tokens = uawos_context.set_context(self.tenant_id, "Developer", "system")
        try:
            data = uawos_db.db_load_objectives()
            objs = data.get("objectives", {})
            obj = objs.get(objective_id)
            return obj.get("status") if obj else "Not Found"
        finally:
            uawos_context.reset_context(tokens)

    def add_memory(self, content: str, scope: str = "workspace", owner: str = "system") -> dict:
        """Append a memory log to short-term memory."""
        tokens = uawos_context.set_context(self.tenant_id, "Developer", "system")
        try:
            return uawos_memory.append_memory(content=content, scope=scope, owner=owner)
        finally:
            uawos_context.reset_context(tokens)

    def search_knowledge(self, query: str, limit: int = 5) -> list:
        """Perform RRF hybrid search on semantic knowledge base."""
        return uawos_db.hybrid_search_knowledge(query=query, tenant_id=self.tenant_id, limit=limit)

    def get_status(self) -> dict:
        """Fetch general daemon status."""
        try:
            req = urllib.request.urlopen(f"{self.base_url}/api/status", timeout=1.0)
            if req.status == 200:
                return json.loads(req.read().decode("utf-8"))
        except Exception:
            pass
        return {"status": "offline", "note": "Local daemon offline. Running in SDK fallback mode."}
