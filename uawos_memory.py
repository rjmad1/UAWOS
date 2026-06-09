# uawos_memory.py
import os
import json
import time

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_memory_state.json")

def get_default_state() -> dict:
    return {
        "memory_logs": [
            {
                "index": 0,
                "timestamp": 1780963292,
                "content": "Initial workspace memory initialized.",
                "scope": "workspace",  # workspace, organizational
                "owner": "system",
                "status": "active"
            }
        ],
        "overlays": {
            "user-01": {
                "theme_preference": "dark_mode",
                "workspace_focus": "objective_lifecycle"
            }
        }
    }

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    state = get_default_state()
    save_state(state)
    return state

def save_state(state: dict):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving memory state: {e}")

# Core API
def append_memory(content: str, scope: str = "workspace", owner: str = "system", governance_check: bool = True) -> dict:
    """Maintain append-only memory (FR-121, FR-126, FR-128, FR-129)."""
    state = load_state()
    
    # Enforce Governance (FR-126)
    if governance_check and "secret" in content.lower():
        raise ValueError("Governance rule violation: Memory cannot store plain secret/credential data.")
        
    index = len(state["memory_logs"])
    entry = {
        "index": index,
        "timestamp": int(time.time()),
        "content": content,
        "scope": scope,
        "owner": owner,
        "status": "active"
    }
    state["memory_logs"].append(entry)
    save_state(state)
    return entry

# FR-122 & FR-130: Overlays
def apply_overlay(overlay_key: str, data: dict) -> dict:
    """Apply a user or contextual memory overlay."""
    state = load_state()
    if overlay_key not in state["overlays"]:
        state["overlays"][overlay_key] = {}
    state["overlays"][overlay_key].update(data)
    save_state(state)
    return state["overlays"][overlay_key]

# FR-124: Curation
def curate_memory(index: int, updated_content: str) -> dict:
    """Curate or correct a memory entry, preserving history via append or trace (FR-127)."""
    state = load_state()
    if index < 0 or index >= len(state["memory_logs"]):
        raise ValueError("Invalid memory index.")
    
    entry = state["memory_logs"][index]
    # Keep historical trace, tag entry as curated
    entry["original_content"] = entry["content"]
    entry["content"] = updated_content
    entry["curated_timestamp"] = int(time.time())
    
    state["memory_logs"][index] = entry
    save_state(state)
    return entry

# FR-125: Memory Export
def export_memory(scope: str) -> list:
    state = load_state()
    return [entry for entry in state["memory_logs"] if entry["scope"] == scope]

# FR-123 & FR-127: Retention and Preservation
def apply_retention_policy(retention_seconds: int):
    """Mark old records as 'archived' but do not delete, ensuring append-only preservation."""
    state = load_state()
    cutoff = int(time.time()) - retention_seconds
    for entry in state["memory_logs"]:
        if entry["timestamp"] < cutoff and entry["status"] == "active":
            entry["status"] = "archived"  # Historical preservation (no physical deletion)
    save_state(state)

# ----------------- VERIFICATION TESTS (FR-121 to FR-130) -----------------

def verify_fr_121():
    m = append_memory("Append test entry")
    assert m["index"] > 0, "Append-only memory insertion failed."
    return True

def verify_fr_122():
    o = apply_overlay("theme_overlay", {"font": "Outfit"})
    assert o["font"] == "Outfit", "Overlay applying failed."
    return True

def verify_fr_123():
    apply_retention_policy(-10) # Everything older than -10s is old
    state = load_state()
    assert state["memory_logs"][0]["status"] == "archived", "Retention policy failed."
    return True

def verify_fr_124():
    cur = curate_memory(0, "Curated Content")
    assert cur["content"] == "Curated Content", "Memory curation failed."
    return True

def verify_fr_125():
    exp = export_memory("workspace")
    assert len(exp) > 0, "Memory export failed."
    return True

def verify_fr_126():
    try:
        append_memory("secret password", governance_check=True)
        assert False, "Should have blocked secret memory."
    except ValueError:
        pass
    return True

def verify_fr_127():
    state = load_state()
    # verify entry 0 has original_content preserved
    assert "original_content" in state["memory_logs"][0], "Historical preservation failed."
    return True

def verify_fr_128():
    m = append_memory("Global Org Standard", scope="organizational")
    assert m["scope"] == "organizational", "Organizational memory failed."
    return True

def verify_fr_129():
    m = append_memory("Project A Standard", scope="workspace")
    assert m["scope"] == "workspace", "Workspace memory failed."
    return True

def verify_fr_130():
    o = apply_overlay("user-01", {"workspace_focus": "sso_testing"})
    assert o["workspace_focus"] == "sso_testing", "User memory overlay failed."
    return True

def run_self_tests():
    print("Running Memory Management self tests...")
    state = get_default_state()
    save_state(state)
    
    tests = [
        ("FR-121", verify_fr_121),
        ("FR-122", verify_fr_122),
        ("FR-123", verify_fr_123),
        ("FR-124", verify_fr_124),
        ("FR-125", verify_fr_125),
        ("FR-126", verify_fr_126),
        ("FR-127", verify_fr_127),
        ("FR-128", verify_fr_128),
        ("FR-129", verify_fr_129),
        ("FR-130", verify_fr_130),
    ]
    
    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae
            
    print("All Memory Engine self tests completed successfully!")

if __name__ == "__main__":
    run_self_tests()
