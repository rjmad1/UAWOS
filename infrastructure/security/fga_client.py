# infrastructure/security/fga_client.py
import json
import os
import urllib.request
import urllib.error

# OpenFGA Connection Settings
OPENFGA_HOST = os.environ.get("OPENFGA_HOST", "127.0.0.1")
OPENFGA_PORT = int(os.environ.get("OPENFGA_PORT", 8083))
OPENFGA_URL = f"http://{OPENFGA_HOST}:{OPENFGA_PORT}"

# Track OpenFGA store, model, and bootstrap status in-memory
_fga_store_id = None
_fga_model_id = None
_fga_bootstrapped = False


def sanitize_id(s: str) -> str:
    """Sanitize identifiers for OpenFGA as spaces are not permitted in type/object IDs."""
    return s.replace(" ", "_")


def bootstrap_openfga() -> bool:
    """Bootstrap OpenFGA store, model, and seed relationship rules dynamically if not already bootstrapped."""
    global _fga_store_id, _fga_model_id, _fga_bootstrapped
    if _fga_bootstrapped:
        return True

    try:
        # 1. Get or create store "uawos"
        url = f"{OPENFGA_URL}/stores"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            stores = data.get("stores", [])

        for s in stores:
            if s.get("name") == "uawos":
                _fga_store_id = s.get("id")
                break

        if not _fga_store_id:
            req = urllib.request.Request(
                url,
                data=json.dumps({"name": "uawos"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                _fga_store_id = res.get("id")

        # 2. Get or create authorization model
        model_url = f"{OPENFGA_URL}/stores/{_fga_store_id}/authorization-models"
        req = urllib.request.Request(model_url, method="GET")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = data.get("authorization_models", [])

        if models:
            _fga_model_id = models[0].get("id")
        else:
            auth_model = {
                "schema_version": "1.1",
                "type_definitions": [
                    {"type": "user"},
                    {
                        "type": "role",
                        "relations": {"member": {"this": {}}},
                        "metadata": {"relations": {"member": {"directly_related_user_types": [{"type": "user"}]}}},
                    },
                    {
                        "type": "action_category",
                        "relations": {"permitted": {"this": {}}},
                        "metadata": {
                            "relations": {
                                "permitted": {
                                    "directly_related_user_types": [
                                        {"type": "user"},
                                        {"type": "role", "relation": "member"},
                                    ]
                                }
                            }
                        },
                    },
                ],
            }
            req_model = urllib.request.Request(
                model_url,
                data=json.dumps(auth_model).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req_model, timeout=1.0) as resp:
                res_model = json.loads(resp.read().decode("utf-8"))
                _fga_model_id = res_model.get("authorization_model_id")

        # 3. Seed static permission tuples individually
        write_url = f"{OPENFGA_URL}/stores/{_fga_store_id}/write"

        static_tuples = []
        # Budget roles
        for r in ["CEO", "Lead Engineer", "Database Expert", "Admin"]:
            static_tuples.append(
                {"user": f"role:{sanitize_id(r)}#member", "relation": "permitted", "object": "action_category:budget"}
            )
        # General roles (all valid roles)
        for r in ["CEO", "Lead Engineer", "Database Expert", "Developer", "Executor Agent", "Senior Engineer", "Admin"]:
            static_tuples.append(
                {"user": f"role:{sanitize_id(r)}#member", "relation": "permitted", "object": "action_category:general"}
            )

        for t in static_tuples:
            payload = {"writes": {"tuple_keys": [t]}, "authorization_model_id": _fga_model_id}
            try:
                req_write = urllib.request.Request(
                    write_url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req_write, timeout=1.0) as resp:
                    pass
            except urllib.error.HTTPError as he:
                # Ignore duplicate writes
                err_data = he.read().decode("utf-8")
                if "already exists" not in err_data:
                    pass
            except Exception:
                pass

        _fga_bootstrapped = True
        return True
    except Exception:
        return False


def check_fga_authorization(actor: str, actor_role: str, category: str) -> bool:
    """Perform fine-grained ReBAC check on OpenFGA. Returns None if OpenFGA is offline/unreachable."""
    if not bootstrap_openfga():
        return None

    mapped_cat = "budget" if category == "budget" else "general"

    # 1. Write user-role mapping
    write_url = f"{OPENFGA_URL}/stores/{_fga_store_id}/write"
    user_tuple = {
        "user": f"user:{sanitize_id(actor)}",
        "relation": "member",
        "object": f"role:{sanitize_id(actor_role)}",
    }
    payload = {"writes": {"tuple_keys": [user_tuple]}, "authorization_model_id": _fga_model_id}

    try:
        req_write = urllib.request.Request(
            write_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_write, timeout=1.0) as resp:
            pass
    except urllib.error.HTTPError as he:
        err_data = he.read().decode("utf-8")
        if "already exists" not in err_data:
            return None
    except Exception:
        return None

    # 2. Call Check endpoint
    check_url = f"{OPENFGA_URL}/stores/{_fga_store_id}/check"
    check_payload = {
        "tuple_key": {
            "user": f"user:{sanitize_id(actor)}",
            "relation": "permitted",
            "object": f"action_category:{mapped_cat}",
        },
        "authorization_model_id": _fga_model_id,
    }
    try:
        req_check = urllib.request.Request(
            check_url,
            data=json.dumps(check_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_check, timeout=1.0) as resp:
            check_res = json.loads(resp.read().decode("utf-8"))
            return check_res.get("allowed", False)
    except Exception:
        return None
