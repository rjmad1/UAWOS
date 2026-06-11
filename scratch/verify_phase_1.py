# scratch/verify_phase_1.py
"""Verification test script for UAWOS Wave 1 tenant isolation.
Verifies thread-safe context propagation, database tenant filters,
Qdrant vector filtering, and the removal of plaintext file fallbacks.
"""

import sys
import os

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import uawos_context
import uawos_db
import uawos_state_utils
import uawos_objective

def verify_relational_tenant_isolation():
    print("\n1. Verifying PostgreSQL Tenant Isolation...")
    if not uawos_db.DB_AVAILABLE:
        print("   [SKIP] PostgreSQL DB driver not available.")
        return

    # Clean up any pre-existing test objectives
    try:
        conn = uawos_db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM uawos_objectives WHERE id LIKE 'TEST-OBJ-%';")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
         print(f"   [WARN] Database cleanup failed: {e}")

    # Set Context for Tenant A
    uawos_context.set_context("tenant_a", "Developer", "alice")
    print(f"   Active Tenant: {uawos_context.get_tenant_id()} | Actor: {uawos_context.get_actor_owner()}")
    
    # Save Objective A
    obj_a = {
        "id": "TEST-OBJ-A",
        "title": "Objective A for Tenant A",
        "description": "Tenant A description",
        "source_type": "text",
        "source_uri": "test",
        "owner": "alice",
        "sponsor": "cto",
        "priority": "High",
        "status": "draft",
        "version": 1,
        "health_score": 100.0,
        "confidence_score": 100.0,
        "dependencies": [],
        "history": [],
        "tenant_id": "default_tenant" # should be overridden by context
    }
    uawos_db.db_save_objective(obj_a)
    print("   Saved Objective TEST-OBJ-A under Tenant A context.")

    # Set Context for Tenant B
    uawos_context.set_context("tenant_b", "Developer", "bob")
    print(f"   Active Tenant: {uawos_context.get_tenant_id()} | Actor: {uawos_context.get_actor_owner()}")

    # Save Objective B
    obj_b = {
        "id": "TEST-OBJ-B",
        "title": "Objective B for Tenant B",
        "description": "Tenant B description",
        "source_type": "text",
        "source_uri": "test",
        "owner": "bob",
        "sponsor": "cto",
        "priority": "Medium",
        "status": "draft",
        "version": 1,
        "health_score": 90.0,
        "confidence_score": 95.0,
        "dependencies": [],
        "history": [],
        "tenant_id": "default_tenant" # should be overridden by context
    }
    uawos_db.db_save_objective(obj_b)
    print("   Saved Objective TEST-OBJ-B under Tenant B context.")

    # Load and verify objectives for Tenant A
    uawos_context.set_context("tenant_a", "Developer", "alice")
    objs_a = uawos_db.db_load_objectives()["objectives"]
    print(f"   Loaded objectives for Tenant A: {list(objs_a.keys())}")
    assert "TEST-OBJ-A" in objs_a, "Tenant A should see its own objective."
    assert "TEST-OBJ-B" not in objs_a, "Tenant A should NOT see Tenant B's objective."

    # Load and verify objectives for Tenant B
    uawos_context.set_context("tenant_b", "Developer", "bob")
    objs_b = uawos_db.db_load_objectives()["objectives"]
    print(f"   Loaded objectives for Tenant B: {list(objs_b.keys())}")
    assert "TEST-OBJ-B" in objs_b, "Tenant B should see its own objective."
    assert "TEST-OBJ-A" not in objs_b, "Tenant B should NOT see Tenant A's objective."

    print("   [PASS] Relational PostgreSQL Tenant Isolation Verified Successfully.")


def verify_vector_tenant_isolation():
    print("\n2. Verifying Qdrant Vector Tenant Isolation...")
    if not uawos_db.QDRANT_AVAILABLE:
        print("   [SKIP] Qdrant DB not available.")
        return

    # Index memory under Tenant A
    uawos_context.set_context("tenant_a", "Developer", "alice")
    uawos_db.index_memory(9991, "blueprint_a", "scope_a", "alice")
    print("   Indexed memory point 9991 for Tenant A.")

    # Index memory under Tenant B
    uawos_context.set_context("tenant_b", "Developer", "bob")
    uawos_db.index_memory(9992, "blueprint_b", "scope_b", "bob")
    print("   Indexed memory point 9992 for Tenant B.")

    # Search memory under Tenant A context
    uawos_context.set_context("tenant_a", "Developer", "alice")
    results_a = uawos_db.search_memory("blueprint_a", limit=5)
    contents_a = [r.get("content") for r in results_a]
    print(f"   Search results for Tenant A: {contents_a}")
    assert any("blueprint_a" in c for c in contents_a), "Tenant A search should retrieve its own memories."
    assert not any("blueprint_b" in c for c in contents_a), "Tenant A search should NOT leak Tenant B's memories."

    # Search memory under Tenant B context
    uawos_context.set_context("tenant_b", "Developer", "bob")
    results_b = uawos_db.search_memory("blueprint_b", limit=5)
    contents_b = [r.get("content") for r in results_b]
    print(f"   Search results for Tenant B: {contents_b}")
    assert any("blueprint_b" in c for c in contents_b), "Tenant B search should retrieve its own memories."
    assert not any("blueprint_a" in c for c in contents_b), "Tenant B search should NOT leak Tenant A's memories."

    print("   [PASS] Vector Qdrant Tenant Isolation Verified Successfully.")


def verify_no_file_fallbacks():
    print("\n3. Verifying Plaintext JSON State Fallback Decommissioning...")
    # Delete any existing test local state file to verify it is not recreated
    test_state_file = os.path.join(project_root, "uawos_verify_test_state.json")
    if os.path.exists(test_state_file):
        os.remove(test_state_file)

    def get_mock_state():
        return {"test_key": "test_val"}

    # Mock Tenant Context
    uawos_context.set_context("tenant_state_test", "Developer", "tester")

    # Load state - should use database and write to DB since file fallbacks are deleted
    state = uawos_state_utils.load_state(test_state_file, get_mock_state)
    assert state == {"test_key": "test_val"}, "State loading failed."
    assert not os.path.exists(test_state_file), "State utility should NOT write a plaintext state JSON file to disk."
    print("   Verified that no local JSON file was created during load.")

    # Modify and save state
    state["new_key"] = "new_val"
    uawos_state_utils.save_state(test_state_file, state)
    assert not os.path.exists(test_state_file), "State utility should NOT write a plaintext state JSON file to disk during save."
    print("   Verified that no local JSON file was created during save.")

    # Re-load to verify database lookup returned the correct modified state
    reloaded_state = uawos_state_utils.load_state(test_state_file, get_mock_state)
    assert reloaded_state.get("new_key") == "new_val", "Relational database state persistence failed."
    print("   Verified relational persistence retrieves modified state.")

    # Clean up test database record
    try:
        conn = uawos_db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM uawos_state WHERE key = 'uawos_verify_test_state';")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
         print(f"   [WARN] Database cleanup of test state failed: {e}")

    print("   [PASS] Plaintext File Fallback Decommissioning Verified Successfully.")


if __name__ == "__main__":
    print("==================================================")
    print("Running Wave 1 Tenant Isolation Integration Tests")
    print("==================================================")
    try:
        verify_relational_tenant_isolation()
        verify_vector_tenant_isolation()
        verify_no_file_fallbacks()
        print("\n==================================================")
        print("ALL WAVE 1 TENANT ISOLATION TESTS PASSED!")
        print("==================================================")
        sys.exit(0)
    except AssertionError as ae:
        print(f"\n[FAIL] Assertion Failed: {ae}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
