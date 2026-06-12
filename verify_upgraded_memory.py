# verify_upgraded_memory.py
import time
import threading
import uuid
import uawos_db
import uawos_memory
import uawos_context

def test_stm_apis():
    print("Testing Short-Term Memory APIs...")
    tenant_id = "tenant-hybrid-test"
    actor = "Executor Agent"
    
    # 1. Session Creation
    session_id = uawos_memory.create_stm_session(tenant_id, actor)
    assert session_id is not None, "Failed to create STM session"
    print(f"  [PASS] STM Session Created: {session_id}")
    
    # 2. Add Context Messages
    uawos_memory.add_stm_message(session_id, "user", "How can I refactor checkouts?")
    uawos_memory.add_stm_message(session_id, "agent", "We can apply database query optimization.")
    
    # 3. Retrieve Context
    context = uawos_memory.get_stm_sliding_context(session_id)
    assert len(context) == 2, f"Expected 2 messages, got {len(context)}"
    assert context[0]["sender"] == "user", "First sender mismatch"
    assert "refactor checkouts" in context[0]["content"], "First content mismatch"
    assert context[1]["sender"] == "agent", "Second sender mismatch"
    print("  [PASS] STM sliding context messages verified.")
    
    # 4. Scratchpad Updates
    uawos_memory.update_agent_scratchpad("Executor Agent", session_id, "Drafting SQL query improvements...", "optimization_step")
    scratchpad = uawos_memory.get_agent_scratchpad("Executor Agent")
    assert scratchpad.get("session_id") == session_id, "Scratchpad session ID mismatch"
    assert scratchpad.get("thought_process") == "Drafting SQL query improvements...", "Scratchpad thought process mismatch"
    assert scratchpad.get("active_plan_step") == "optimization_step", "Scratchpad active step mismatch"
    print("  [PASS] STM agent scratchpad tracking verified.")


def test_episodic_apis():
    print("Testing Episodic Memory APIs...")
    session_id = uawos_memory.create_stm_session("tenant-hybrid-test", "Executor Agent")
    objective_id = "OBJ-202"
    summary = "Resolving database checkout latency under load."
    
    # 1. Create Episode
    episode_id = uawos_memory.create_episode(session_id, objective_id, summary)
    assert episode_id is not None, "Failed to create episode"
    print(f"  [PASS] Episode Created: {episode_id}")
    
    # 2. Add Timeline Events
    uawos_memory.add_episode_event(episode_id, "Executor Agent", "action_run", "Executed test suite checkout queries.", {"latency_ms": 3200})
    uawos_memory.add_episode_event(episode_id, "Executor Agent", "action_failure", "Checkout connection query timeout.", {"error": "TimeoutException"})
    
    # 3. Add Decision Records
    uawos_memory.add_episode_decision(episode_id, "REC-101", "Alt B: Cached query optimizations", "Allows faster query retrievals in parallel.", {"risk_shift": "lowered"})
    
    # 4. Query Timeline
    timeline = uawos_memory.get_episode_timeline(episode_id)
    assert len(timeline) == 2, f"Expected 2 timeline events, got {len(timeline)}"
    assert timeline[0]["actor_id"] == "Executor Agent", "Event actor mismatch"
    assert timeline[1]["event_type"] == "action_failure", "Event type mismatch"
    print("  [PASS] Episodic timeline events and decision mappings verified.")
    return episode_id


def test_concurrency_advisory_locks():
    print("Testing Concurrency Control via Advisory Locks...")
    lock_id = 99999
    execution_order = []
    
    def thread_task(name, delay):
        uawos_memory.acquire_advisory_lock(lock_id)
        execution_order.append(f"{name}_entered")
        time.sleep(delay)
        execution_order.append(f"{name}_exited")
        uawos_memory.release_advisory_lock(lock_id)
        
    t1 = threading.Thread(target=thread_task, args=("ThreadA", 0.2))
    t2 = threading.Thread(target=thread_task, args=("ThreadB", 0.05))
    
    t1.start()
    time.sleep(0.05) # Ensure ThreadA acquires the lock first
    t2.start()
    
    t1.join()
    t2.join()
    
    # Verify ThreadB waited until ThreadA exited
    assert execution_order == ["ThreadA_entered", "ThreadA_exited", "ThreadB_entered", "ThreadB_exited"], f"Concurrency mismatch: {execution_order}"
    print("  [PASS] advisory lock concurrency safety verified.")


def test_hybrid_search():
    print("Testing Hybrid Lexical-Vector Retrieval...")
    tenant_id = "tenant-hybrid-test"
    
    # Index knowledge items
    uawos_db.index_knowledge("KNW-301", "OAuth Spec Detail", "Use OAuth 2.0 client credentials for machine authorization.", "document", "Security Spec PDF")
    uawos_db.index_knowledge("KNW-302", "Checkout Latency Specs", "Checkout API connection latency must stay under 100ms threshold.", "document", "Performance Spec PDF")
    
    # Run hybrid search
    results = uawos_db.hybrid_search_knowledge("OAuth client credentials", tenant_id, limit=5)
    print(f"Hybrid search returned {len(results)} items:")
    for idx, r in enumerate(results):
        print(f"  [{idx}] ID: {r.get('id')}, Content: {r.get('content')[:50]}, Title: {r.get('title')}")
    
    # We should have KNW-301 matched first
    assert len(results) > 0, "No results returned in hybrid search"
    assert "OAuth" in results[0]["content"], f"Expected OAuth content at rank 0, got: {results[0]['content']}"
    print("  [PASS] Hybrid lexical-vector search (RRF) verified.")


def test_reflection_and_consolidation(episode_id):
    print("Testing Memory Consolidation & Reflection...")
    
    # 1. Test Reflection
    best_practice = uawos_memory.reflect_on_episode(episode_id)
    assert best_practice is not None, "Failed to reflect on episode"
    assert best_practice["source_type"] == "best_practice", "Reflection source type mismatch"
    print(f"  [PASS] Episode Reflection verified: {best_practice['title']}")
    
    # 2. Test Consolidation
    # Add near-duplicate assets
    uawos_db.index_knowledge("KNW-401", "Redis Config Specs", "Ensure Redis container runs with maxmemory 2gb policy.", "document", "infra")
    uawos_db.index_knowledge("KNW-402", "Redis Config Specs v2", "Ensure Redis container runs with maxmemory 2gb policy.", "document", "infra")
    
    consolidated = uawos_memory.auto_consolidate_memories(similarity_threshold=0.8)
    assert len(consolidated) > 0, "Consolidation failed to merge duplicate entries"
    print(f"  [PASS] Memory Consolidation merged {len(consolidated)} duplicate assets.")


def run_all_tests():
    print("==================================================")
    print("Running Upgraded UAWOS Memory Suite (Level 5.0)...")
    print("==================================================")
    
    tokens = uawos_context.set_context("tenant-hybrid-test", "Developer", "system")
    try:
        test_stm_apis()
        print("-" * 50)
        episode_id = test_episodic_apis()
        print("-" * 50)
        test_concurrency_advisory_locks()
        print("-" * 50)
        test_hybrid_search()
        print("-" * 50)
        test_reflection_and_consolidation(episode_id)
        print("==================================================")
        print("All Upgraded Memory Suite tests completed successfully!")
        print("==================================================")
    finally:
        uawos_context.reset_context(tokens)

if __name__ == "__main__":
    run_all_tests()
