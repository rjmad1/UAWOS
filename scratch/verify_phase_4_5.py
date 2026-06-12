import json
import os
import sys
import urllib.request

# Ensure project root is in path
project_root = r"C:/Users/rajaj/Projects/UAWOS"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import contextlib

import uawos_db
import uawos_knowledge
import uawos_state_utils


def verify_neo4j_sync():
    print("--- Verifying Neo4j Sync ---")

    # 1. Create a dummy asset
    asset_title = "Manual Ingress Verif"
    asset_content = "OAuth credentials verification payload"
    asset = uawos_knowledge.create_knowledge_asset(
        title=asset_title, content=asset_content, source_type="verification", provenance="Verification Runner"
    )
    asset_id = asset["id"]
    print(f"Created knowledge asset: {asset_id}")

    # 2. Create relationship
    rel = uawos_knowledge.create_graph_relationship(
        source_id=asset_id, relationship="VERIFIES_FLOW", target_id="OBJ-101"
    )
    print(f"Created relationship: {rel['id']}")

    # 3. Query Neo4j via HTTP REST to verify nodes & relationship exist
    url = f"{uawos_knowledge.NEO4J_URL}/db/neo4j/tx/commit"
    query = """
    MATCH (a:KnowledgeAsset {id: $id})-[r:VERIFIES_FLOW]->(o:Objective {id: 'OBJ-101'})
    RETURN a.title as title, r.id as rel_id
    """
    payload = {"statements": [{"statement": query, "parameters": {"id": asset_id}}]}

    try:
        import base64

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        auth_str = os.environ.get("NEO4J_AUTH", "neo4j/uawos-change-me")
        if auth_str and auth_str.lower() != "none" and "/" in auth_str:
            user, pw = auth_str.split("/", 1)
            base64string = base64.b64encode(f"{user}:{pw}".encode()).decode("utf-8")
            headers["Authorization"] = f"Basic {base64string}"

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers=headers)
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            results = res.get("results", [])
            if results and results[0].get("data"):
                row = results[0]["data"][0]["row"]
                print(f"[PASS] Found matched nodes in Neo4j! Asset title: '{row[0]}', Rel ID: '{row[1]}'")
                return True
            else:
                print("[FAIL] Could not retrieve the matched nodes from Neo4j.")
                print("Neo4j returned:", res)
    except Exception as e:
        print("[FAIL] HTTP query to Neo4j failed:", e)
    return False


def verify_tenant_isolation():
    print("--- Verifying Multi-Tenant State Isolation ---")

    state_file = os.path.join(project_root, "uawos_test_tenant_state.json")

    # Define caller STATE_FILE and get_default_state
    global STATE_FILE
    STATE_FILE = state_file

    # Mock get_default_state
    def mock_default():
        return {"value": "initial"}

    try:
        # Save state under tenant_a
        state_a = {"value": "data_for_tenant_a"}
        uawos_state_utils.save_state(state_file, state_a, tenant_id="tenant_a")
        print("Saved state under 'tenant_a'")

        # Save state under tenant_b
        state_b = {"value": "data_for_tenant_b"}
        uawos_state_utils.save_state(state_file, state_b, tenant_id="tenant_b")
        print("Saved state under 'tenant_b'")

        # Load state under tenant_a (should load state_a)
        loaded_a = uawos_state_utils.load_state(state_file, mock_default, tenant_id="tenant_a")
        print(f"Loaded tenant_a state: {loaded_a}")

        # Load state under tenant_b (should load state_b)
        loaded_b = uawos_state_utils.load_state(state_file, mock_default, tenant_id="tenant_b")
        print(f"Loaded tenant_b state: {loaded_b}")

        assert loaded_a["value"] == "data_for_tenant_a", "Tenant A state mismatch"
        assert loaded_b["value"] == "data_for_tenant_b", "Tenant B state mismatch"
        print("[PASS] Tenant states are isolated successfully!")
        return True
    except Exception as e:
        print("[FAIL] Tenant isolation failed:", e)
    finally:
        # Cleanup file if exists
        if os.path.exists(state_file):
            with contextlib.suppress(Exception):
                os.remove(state_file)
    return False


if __name__ == "__main__":
    uawos_db.init_db()
    n_ok = verify_neo4j_sync()
    t_ok = verify_tenant_isolation()

    if n_ok and t_ok:
        print("\nALL PHASE 4 & 5 VERIFICATIONS PASSED!")
        sys.exit(0)
    else:
        print("\nSOME VERIFICATIONS FAILED!")
        sys.exit(1)
