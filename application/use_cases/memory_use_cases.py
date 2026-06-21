# application/use_cases/memory_use_cases.py
import json
import os
import time
import uuid

from domains.memory.memory import MemoryEntry
from infrastructure.storage.json_fallback_store import load_state, save_state

STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uawos_memory_state.json"
)


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


def append_memory(
    content: str,
    scope: str = "workspace",
    owner: str = "system",
    governance_check: bool = True,
) -> dict:
    """Append a new memory entry to the memory log."""
    if governance_check and "secret" in content.lower():
        raise ValueError("Governance rule violation: Memory cannot store plain secret/credential data.")

    state = load_state()
    index = len(state["memory_logs"])

    entry = MemoryEntry(
        index=index,
        timestamp=int(time.time()),
        content=content,
        scope=scope,
        owner=owner,
        status="active",
    )

    state["memory_logs"].append(entry.to_dict())
    save_state(state)

    try:
        from infrastructure.database.db import index_memory

        index_memory(index, content, scope, owner)
    except Exception:
        pass

    return entry.to_dict()


def apply_overlay(overlay_key: str, data: dict) -> dict:
    """Apply a user or contextual memory overlay."""
    state = load_state()
    if overlay_key not in state["overlays"]:
        state["overlays"][overlay_key] = {}
    state["overlays"][overlay_key].update(data)
    save_state(state)
    return state["overlays"][overlay_key]


def curate_memory(index: int, updated_content: str) -> dict:
    """Curate or correct a memory entry, preserving history via append or trace."""
    state = load_state()
    if index < 0 or index >= len(state["memory_logs"]):
        raise ValueError("Invalid memory index.")

    entry_dict = state["memory_logs"][index]
    entry = MemoryEntry.from_dict(entry_dict)

    entry.original_content = entry.content
    entry.content = updated_content
    entry.curated_timestamp = int(time.time())

    state["memory_logs"][index] = entry.to_dict()
    save_state(state)

    try:
        from infrastructure.database.db import index_memory

        index_memory(index, updated_content, entry.scope, entry.owner)
    except Exception:
        pass

    return entry.to_dict()


def export_memory(scope: str) -> list:
    state = load_state()
    return [entry for entry in state["memory_logs"] if entry["scope"] == scope]


def apply_retention_policy(retention_seconds: int):
    """Mark old records as 'archived' but do not delete, ensuring append-only preservation."""
    state = load_state()
    cutoff = int(time.time()) - retention_seconds
    for entry_dict in state["memory_logs"]:
        entry = MemoryEntry.from_dict(entry_dict)
        if entry.timestamp < cutoff and entry.status == "active":
            entry.status = "archived"
            entry_dict.update(entry.to_dict())
    save_state(state)


# ----------------- STM & Episodic Memory Upgrade (Level 5.0) -----------------


def create_stm_session(tenant_id: str, actor_owner: str) -> str:
    """Create a new short-term memory session in the database."""
    from infrastructure.database.db import DB_AVAILABLE, get_db_connection

    if not DB_AVAILABLE:
        return str(uuid.uuid4())
    try:
        session_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_stm_sessions (session_id, tenant_id, actor_owner, status)
            VALUES (%s, %s, %s, 'active');
            """,
            (session_id, tenant_id, actor_owner),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return session_id
    except Exception as e:
        print(f"create_stm_session error: {e}")
        return str(uuid.uuid4())


def add_stm_message(session_id: str, sender: str, content: str, parent_message_id: int = None) -> int:
    """Add a new sliding-context message to the active session."""
    from infrastructure.database.db import DB_AVAILABLE, get_db_connection

    if not DB_AVAILABLE:
        return None
    try:
        token_count = len(content.split())  # Simple heuristic
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_stm_sliding_context (session_id, sender, message_content, token_count, parent_message_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (session_id, sender, content, token_count, parent_message_id),
        )
        row = cursor.fetchone()
        inserted_id = row[0] if row else None
        conn.commit()
        cursor.close()
        conn.close()
        return inserted_id
    except Exception as e:
        print(f"add_stm_message error: {e}")
        return None


def get_stm_sliding_context(session_id: str, max_tokens: int = 1500) -> list:
    """Retrieve sliding-context messages for the session up to token capacity."""
    from infrastructure.database.db import DB_AVAILABLE, get_db_connection

    if not DB_AVAILABLE:
        return []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT sender, message_content, token_count, created_at, id, parent_message_id
            FROM uawos_stm_sliding_context
            WHERE session_id = %s
            ORDER BY created_at ASC;
            """,
            (session_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        messages = []
        accumulated_tokens = 0
        for r in reversed(rows):
            t_count = r[2]
            if accumulated_tokens + t_count > max_tokens:
                break
            accumulated_tokens += t_count
            messages.append(
                {
                    "sender": r[0],
                    "content": r[1],
                    "token_count": t_count,
                    "created_at": str(r[3]),
                    "id": r[4],
                    "parent_message_id": r[5],
                }
            )
        return list(reversed(messages))
    except Exception as e:
        print(f"get_stm_sliding_context error: {e}")
        return []


def update_agent_scratchpad(agent_id: str, session_id: str, thought_process: str, active_plan_step: str):
    """Upsert agent scratchpad thinking process and step details."""
    from infrastructure.database.db import DB_AVAILABLE, get_db_connection

    if not DB_AVAILABLE:
        return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_stm_agent_scratchpad (agent_id, session_id, thought_process, active_plan_step, updated_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (agent_id) DO UPDATE
            SET session_id = EXCLUDED.session_id,
                thought_process = EXCLUDED.thought_process,
                active_plan_step = EXCLUDED.active_plan_step,
                updated_at = CURRENT_TIMESTAMP;
            """,
            (agent_id, session_id, thought_process, active_plan_step),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"update_agent_scratchpad error: {e}")


def get_agent_scratchpad(agent_id: str) -> dict:
    """Retrieve active scratchpad details for an agent."""
    from infrastructure.database.db import DB_AVAILABLE, get_db_connection

    if not DB_AVAILABLE:
        return {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT session_id, thought_process, active_plan_step, updated_at
            FROM uawos_stm_agent_scratchpad
            WHERE agent_id = %s;
            """,
            (agent_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return {
                "agent_id": agent_id,
                "session_id": row[0],
                "thought_process": row[1],
                "active_plan_step": row[2],
                "updated_at": str(row[3]),
            }
        return {}
    except Exception as e:
        print(f"get_agent_scratchpad error: {e}")
        return {}


def create_episode(session_id: str, objective_id: str, summary: str) -> str:
    """Create a new episodic execution block."""
    from infrastructure.database.db import DB_AVAILABLE, get_db_connection

    if not DB_AVAILABLE:
        return str(uuid.uuid4())
    try:
        episode_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_episodic_episodes (episode_id, session_id, objective_id, summary, status)
            VALUES (%s, %s, %s, %s, 'in_progress');
            """,
            (episode_id, session_id, objective_id, summary),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return episode_id
    except Exception as e:
        print(f"create_episode error: {e}")
        return str(uuid.uuid4())


def add_episode_event(episode_id: str, actor_id: str, event_type: str, content: str, telemetry: dict = None):
    """Log an execution event under the episode timeline."""
    from infrastructure.database.db import DB_AVAILABLE, get_db_connection

    if not DB_AVAILABLE:
        return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_episodic_events (episode_id, actor_id, event_type, content, telemetry)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (episode_id, actor_id, event_type, content, json.dumps(telemetry or {})),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"add_episode_event error: {e}")


def add_episode_decision(
    episode_id: str, recommendation_id: str, chosen_alternative: str, justification: str, causal_impact: dict = None
):
    """Log a decision linked to the current execution episode."""
    from infrastructure.database.db import DB_AVAILABLE, get_db_connection

    if not DB_AVAILABLE:
        return
    try:
        decision_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_episodic_decisions (decision_id, episode_id, recommendation_id, chosen_alternative, justification, causal_impact)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (
                decision_id,
                episode_id,
                recommendation_id,
                chosen_alternative,
                justification,
                json.dumps(causal_impact or {}),
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"add_episode_decision error: {e}")


def get_episode_timeline(episode_id: str) -> list:
    """Retrieve the chronological timeline of events for an episode."""
    from infrastructure.database.db import DB_AVAILABLE, get_db_connection

    if not DB_AVAILABLE:
        return []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT event_id, actor_id, event_type, content, telemetry, created_at
            FROM uawos_episodic_events
            WHERE episode_id = %s
            ORDER BY created_at ASC;
            """,
            (episode_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [
            {
                "event_id": r[0],
                "actor_id": r[1],
                "event_type": r[2],
                "content": r[3],
                "telemetry": r[4],
                "created_at": str(r[5]),
            }
            for r in rows
        ]
    except Exception as e:
        print(f"get_episode_timeline error: {e}")
        return []


def reflect_on_episode(episode_id: str) -> dict:
    """Reflect on completed episode events, summarize, and publish as best practice."""
    timeline = get_episode_timeline(episode_id)
    if not timeline:
        return {}

    events_summary = " ".join([f"{e['actor_id']} - {e['content']}" for e in timeline])
    reflection_text = f"Continuous learning summary of events: {events_summary[:200]}"
    try:
        import uawos_weaverouter

        prompt = f"Summarize these workflow events into a technical best practice rule: {events_summary[:300]}"
        reflection_text = uawos_weaverouter.uawos_generate_response(
            prompt=prompt, model="tinyllama", agent_name="Memory Consolidation Agent"
        )
    except Exception:
        pass

    import uawos_knowledge

    asset = uawos_knowledge.create_knowledge_asset(
        title=f"Reflected Best Practice - Episode {episode_id[:8]}",
        content=reflection_text,
        source_type="best_practice",
        source_uri=f"internal://reflection/{episode_id}",
        provenance="Autonomous Reflection Service",
    )

    from infrastructure.database.db import DB_AVAILABLE, get_db_connection

    if DB_AVAILABLE:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE uawos_episodic_episodes SET status = 'completed', end_time = CURRENT_TIMESTAMP WHERE episode_id = %s;",
                (episode_id,),
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Failed to update episode status: {e}")

    return asset


def auto_consolidate_memories(similarity_threshold: float = 0.92) -> list:
    """Scan knowledge assets in PostgreSQL, detect near-duplicate contents, and consolidate them."""
    consolidated = []
    from infrastructure.database.db import DB_AVAILABLE, get_db_connection

    if not DB_AVAILABLE:
        return []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT asset_id, content, title FROM uawos_semantic_knowledge WHERE source_type != 'reconciled';"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        def jaccard(s1, s2):
            w1 = set(s1.lower().split())
            w2 = set(s2.lower().split())
            if not w1 or not w2:
                return 0.0
            return len(w1.intersection(w2)) / len(w1.union(w2))

        visited = set()
        import uawos_knowledge

        for i in range(len(rows)):
            id_i, content_i, title_i = rows[i]
            if id_i in visited:
                continue
            for j in range(i + 1, len(rows)):
                id_j, content_j, title_j = rows[j]
                if id_j in visited:
                    continue
                score = jaccard(content_i, content_j)
                if score >= similarity_threshold:
                    visited.add(id_j)
                    reconciled = uawos_knowledge.reconcile_contradictions(id_i, id_j, "latest_timestamp")
                    consolidated.append({"merged_from": [id_i, id_j], "reconciled_asset_id": reconciled["id"]})
        return consolidated
    except Exception as e:
        print(f"auto_consolidate_memories error: {e}")
        return []
