# uawos_memory.py
import os
import time
import json
import uuid

import uawos_db
from uawos_state_utils import load_state, save_state

from application.use_cases.memory_use_cases import (
    append_memory,
    apply_overlay,
    curate_memory,
    export_memory,
    apply_retention_policy,
    create_stm_session,
    add_stm_message,
    get_stm_sliding_context,
    update_agent_scratchpad,
    get_agent_scratchpad,
    create_episode,
    add_episode_event,
    add_episode_decision,
    get_episode_timeline,
    reflect_on_episode,
    auto_consolidate_memories,
)

# Advisory lock wrappers for compatibility
from infrastructure.database.db import acquire_advisory_lock, release_advisory_lock

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
                "status": "active",
            }
        ],
        "overlays": {
            "user-01": {
                "theme_preference": "dark_mode",
                "workspace_focus": "objective_lifecycle",
            }
        },
    }


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
    apply_retention_policy(-10)  # Everything older than -10s is old
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
        raise AssertionError("Should have blocked secret memory.")
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
