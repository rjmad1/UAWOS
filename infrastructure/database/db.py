# infrastructure/database/db.py
import contextlib
import hashlib
import json
import time
import urllib.request

from config import settings
from shared.utilities.context import get_tenant_id

try:
    import psycopg2

    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


def get_db_connection():
    if not DB_AVAILABLE:
        raise RuntimeError("psycopg2 is not installed.")
    return psycopg2.connect(settings.POSTGRES_CONN_STR)


def init_db():
    if not DB_AVAILABLE:
        print("PostgreSQL driver unavailable. Bypassing DB init.")
        return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_state (
                key VARCHAR(255),
                tenant_id VARCHAR(50) DEFAULT 'default_tenant',
                state JSONB NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (key, tenant_id)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_objectives (
                id VARCHAR(255) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                source_type VARCHAR(50),
                source_uri VARCHAR(255),
                owner VARCHAR(255),
                sponsor VARCHAR(255),
                priority VARCHAR(50),
                status VARCHAR(50),
                version INT DEFAULT 1,
                health_score DOUBLE PRECISION DEFAULT 100.0,
                confidence_score DOUBLE PRECISION DEFAULT 100.0,
                dependencies JSONB DEFAULT '[]',
                history JSONB DEFAULT '[]',
                tenant_id VARCHAR(50) DEFAULT 'default_tenant',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_outcomes (
                id VARCHAR(255) PRIMARY KEY,
                objective_id VARCHAR(255) REFERENCES uawos_objectives(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                metric VARCHAR(255) NOT NULL,
                unit VARCHAR(255) NOT NULL,
                weight DOUBLE PRECISION DEFAULT 1.0,
                dependencies JSONB DEFAULT '[]',
                confidence_score DOUBLE PRECISION DEFAULT 100.0,
                owner VARCHAR(255),
                baseline_state DOUBLE PRECISION DEFAULT 0.0,
                target_state DOUBLE PRECISION DEFAULT 100.0,
                current_state DOUBLE PRECISION,
                forecasted_state DOUBLE PRECISION,
                tenant_id VARCHAR(50) DEFAULT 'default_tenant',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_plans (
                id VARCHAR(255) PRIMARY KEY,
                objective_id VARCHAR(255) REFERENCES uawos_objectives(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                steps JSONB DEFAULT '[]',
                cost_estimate DOUBLE PRECISION DEFAULT 0.0,
                duration_estimate INT DEFAULT 0,
                resource_requirements JSONB DEFAULT '[]',
                success_probability DOUBLE PRECISION DEFAULT 1.0,
                status VARCHAR(50),
                version INT DEFAULT 1,
                risks JSONB DEFAULT '[]',
                assumptions JSONB DEFAULT '[]',
                is_alternative BOOLEAN DEFAULT FALSE,
                history JSONB DEFAULT '[]',
                tenant_id VARCHAR(50) DEFAULT 'default_tenant',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_workflows (
                id VARCHAR(255) PRIMARY KEY,
                plan_id VARCHAR(255) REFERENCES uawos_plans(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                tasks JSONB DEFAULT '[]',
                dependencies JSONB DEFAULT '[]',
                state VARCHAR(50),
                version INT DEFAULT 1,
                governed BOOLEAN DEFAULT TRUE,
                history JSONB DEFAULT '[]',
                tenant_id VARCHAR(50) DEFAULT 'default_tenant',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_actions (
                id VARCHAR(255) PRIMARY KEY,
                workflow_id VARCHAR(255) REFERENCES uawos_workflows(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                owner VARCHAR(255) NOT NULL,
                dependencies JSONB DEFAULT '[]',
                priority VARCHAR(50) DEFAULT 'Medium',
                budget DOUBLE PRECISION DEFAULT 0.0,
                deadline INT DEFAULT 0,
                status VARCHAR(50) DEFAULT 'pending',
                approval_required BOOLEAN DEFAULT FALSE,
                tenant_id VARCHAR(50) DEFAULT 'default_tenant',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Dynamic schema updates to guarantee tenant_id column existence in pre-existing DBs
        for table in ["uawos_objectives", "uawos_outcomes", "uawos_plans", "uawos_workflows", "uawos_actions"]:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(50) DEFAULT 'default_tenant';"
            )
        cursor.execute(
            "ALTER TABLE uawos_state ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(50) DEFAULT 'default_tenant';"
        )
        with contextlib.suppress(Exception):
            cursor.execute("ALTER TABLE uawos_state DROP CONSTRAINT IF EXISTS uawos_state_pkey;")
        with contextlib.suppress(Exception):
            cursor.execute("ALTER TABLE uawos_state ADD CONSTRAINT uawos_state_pkey PRIMARY KEY (key, tenant_id);")

        # STM, Episodic, Semantic tables for Level 5.0 Memory Upgrade
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_stm_sessions (
                session_id VARCHAR(255) PRIMARY KEY,
                tenant_id VARCHAR(50) NOT NULL,
                actor_owner VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_stm_sliding_context (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) REFERENCES uawos_stm_sessions(session_id) ON DELETE CASCADE,
                sender VARCHAR(255) NOT NULL,
                message_content TEXT NOT NULL,
                token_count INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_stm_agent_scratchpad (
                agent_id VARCHAR(255) PRIMARY KEY,
                session_id VARCHAR(255) REFERENCES uawos_stm_sessions(session_id) ON DELETE CASCADE,
                thought_process TEXT,
                active_plan_step VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_episodic_episodes (
                episode_id VARCHAR(255) PRIMARY KEY,
                session_id VARCHAR(255) REFERENCES uawos_stm_sessions(session_id) ON DELETE SET NULL,
                objective_id VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'in_progress',
                summary TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_episodic_events (
                event_id SERIAL PRIMARY KEY,
                episode_id VARCHAR(255) REFERENCES uawos_episodic_episodes(episode_id) ON DELETE CASCADE,
                actor_id VARCHAR(255) NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                telemetry JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_episodic_decisions (
                decision_id VARCHAR(255) PRIMARY KEY,
                episode_id VARCHAR(255) REFERENCES uawos_episodic_episodes(episode_id) ON DELETE CASCADE,
                recommendation_id VARCHAR(255) NOT NULL,
                chosen_alternative TEXT NOT NULL,
                justification TEXT NOT NULL,
                causal_impact JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_semantic_knowledge (
                asset_id VARCHAR(255) PRIMARY KEY,
                tenant_id VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                content_hash VARCHAR(64) NOT NULL,
                content TEXT NOT NULL,
                source_type VARCHAR(100) DEFAULT 'document',
                provenance TEXT,
                confidence_score DOUBLE PRECISION DEFAULT 100.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        with contextlib.suppress(Exception):
            cursor.execute(
                "ALTER TABLE uawos_semantic_knowledge DROP CONSTRAINT IF EXISTS uawos_semantic_knowledge_content_hash_key;"
            )
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_semantic_chunks (
                chunk_id VARCHAR(255) PRIMARY KEY,
                asset_id VARCHAR(255) REFERENCES uawos_semantic_knowledge(asset_id) ON DELETE CASCADE,
                chunk_index INT NOT NULL,
                content TEXT NOT NULL,
                vector_id VARCHAR(255) UNIQUE NOT NULL
            );
        """)

        # Add parent_message_id to STM sliding context
        cursor.execute("""
            ALTER TABLE uawos_stm_sliding_context
            ADD COLUMN IF NOT EXISTS parent_message_id INTEGER REFERENCES uawos_stm_sliding_context(id) ON DELETE SET NULL;
        """)

        # Create Shared Channels and membership tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_channels (
                channel_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                tenant_id VARCHAR(50) DEFAULT 'default_tenant',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_channel_members (
                channel_id VARCHAR(255) REFERENCES uawos_channels(channel_id) ON DELETE CASCADE,
                user_id VARCHAR(255) NOT NULL,
                tenant_id VARCHAR(50) DEFAULT 'default_tenant',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (channel_id, user_id)
            );
        """)

        # Create Linked Files and Artifacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_artifacts (
                artifact_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                file_path VARCHAR(555) NOT NULL,
                file_hash VARCHAR(64) NOT NULL,
                objective_id VARCHAR(255),
                action_id VARCHAR(255),
                tenant_id VARCHAR(50) DEFAULT 'default_tenant',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Create Billing & Subscription table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_subscriptions (
                tenant_id VARCHAR(50) PRIMARY KEY,
                plan_type VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                expires_at TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uawos_events (
                event_id VARCHAR(255) PRIMARY KEY,
                event_type VARCHAR(255) NOT NULL,
                event_version VARCHAR(50) NOT NULL,
                timestamp DOUBLE PRECISION NOT NULL,
                actor VARCHAR(255) NOT NULL,
                source VARCHAR(255) NOT NULL,
                correlation_id VARCHAR(255) NOT NULL,
                causation_id VARCHAR(255) NOT NULL,
                entity_ref VARCHAR(255) NOT NULL,
                payload JSONB DEFAULT '{}',
                tenant_id VARCHAR(50) DEFAULT 'default_tenant',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("PostgreSQL UAWOS state and relational tables initialized successfully.")
    except Exception as e:
        print(f"PostgreSQL connection/init failed: {e}")


def init_qdrant():
    if not QDRANT_AVAILABLE:
        print("Qdrant client unavailable. Bypassing Qdrant init.")
        return
    try:
        client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        collections = [c.name for c in client.get_collections().collections]

        if "uawos_memory" not in collections:
            client.create_collection(
                collection_name="uawos_memory",
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
        if "uawos_knowledge" not in collections:
            client.create_collection(
                collection_name="uawos_knowledge",
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
        print("Qdrant vector collections initialized successfully.")
    except Exception as e:
        print(f"Qdrant connection/init failed: {e}")


def get_embedding(text: str) -> list:
    """Get text embeddings from local Ollama TinyLlama, with deterministic fallback."""
    try:
        req_data = json.dumps({"model": "tinyllama", "prompt": text}).encode("utf-8")
        req = urllib.request.Request(
            f"{settings.OLLAMA_BASE_URL}/api/embeddings",
            data=req_data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=2.0) as response:
            resp = json.loads(response.read().decode("utf-8"))
            emb = resp.get("embedding")
            if emb and len(emb) == 384:
                return emb
            elif emb:
                if len(emb) > 384:
                    return emb[:384]
                else:
                    return emb + [0.0] * (384 - len(emb))
    except Exception:
        pass

    # Deterministic fallback vector
    h = hashlib.sha256(text.encode("utf-8")).digest()
    vector = []
    for i in range(384):
        val = (h[i % 32] + i) % 256
        vector.append(float(val) / 256.0 - 0.5)
    return vector


def db_get_state(key: str, default_fn, tenant_id: str = "default_tenant") -> dict:
    if not DB_AVAILABLE:
        return default_fn() if default_fn else None
    try:
        if tenant_id == "default_tenant":
            tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT state FROM uawos_state WHERE key = %s AND tenant_id = %s;", (key, tenant_id))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            state = row[0]
            if isinstance(state, str):
                return json.loads(state)
            return state
    except Exception as e:
        print(f"Database error loading state for {key} under tenant {tenant_id}: {e}")
        raise e
    return default_fn() if default_fn else None


def db_save_state(key: str, state: dict, tenant_id: str = "default_tenant"):
    if not DB_AVAILABLE:
        return
    try:
        if tenant_id == "default_tenant":
            tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_state (key, tenant_id, state, updated_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (key, tenant_id) DO UPDATE
            SET state = EXCLUDED.state, updated_at = CURRENT_TIMESTAMP;
        """,
            (key, tenant_id, json.dumps(state)),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error saving state for {key} under tenant {tenant_id}: {e}")
        raise e


def db_save_event(event: dict) -> None:
    if not DB_AVAILABLE:
        return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_events (
                event_id, event_type, event_version, timestamp, actor, source,
                correlation_id, causation_id, entity_ref, payload, tenant_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (event_id) DO NOTHING;
        """,
            (
                event.get("event_id"),
                event.get("event_type"),
                event.get("event_version"),
                event.get("timestamp"),
                event.get("actor"),
                event.get("source"),
                event.get("correlation_id"),
                event.get("causation_id"),
                event.get("entity_ref"),
                json.dumps(event.get("payload", {})),
                event.get("tenant_id", "default_tenant"),
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"db_save_event failed: {e}")


def db_get_events(correlation_id: str | None = None, event_type: str | None = None, limit: int = 100) -> list[dict]:
    if not DB_AVAILABLE:
        return []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT event_id, event_type, event_version, timestamp, actor, source, correlation_id, causation_id, entity_ref, payload, tenant_id FROM uawos_events"
        conditions = []
        params = []
        if correlation_id:
            conditions.append("correlation_id = %s")
            params.append(correlation_id)
        if event_type:
            conditions.append("event_type = %s")
            params.append(event_type)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY timestamp ASC LIMIT %s"
        params.append(limit)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        events = []
        for r in rows:
            events.append(
                {
                    "event_id": r[0],
                    "event_type": r[1],
                    "event_version": r[2],
                    "timestamp": r[3],
                    "actor": r[4],
                    "source": r[5],
                    "correlation_id": r[6],
                    "causation_id": r[7],
                    "entity_ref": r[8],
                    "payload": r[9] if isinstance(r[9], dict) else json.loads(r[9] or "{}"),
                    "tenant_id": r[10],
                }
            )
        return events
    except Exception as e:
        print(f"db_get_events failed: {e}")
        return []


def index_memory(memory_id: int, content: str, scope: str, owner: str):
    if not QDRANT_AVAILABLE:
        return
    try:
        tenant_id = get_tenant_id()
        client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        embedding = get_embedding(content)
        client.upsert(
            collection_name="uawos_memory",
            points=[
                PointStruct(
                    id=memory_id,
                    vector=embedding,
                    payload={
                        "content": content,
                        "scope": scope,
                        "owner": owner,
                        "timestamp": int(time.time()),
                        "tenant_id": tenant_id,
                    },
                )
            ],
        )
    except Exception as e:
        print(f"Error indexing memory in Qdrant: {e}")


def db_save_semantic_knowledge(
    asset_id: str,
    tenant_id: str,
    title: str,
    content: str,
    source_type: str,
    provenance: str,
    confidence_score: float = 100.0,
):
    if not DB_AVAILABLE:
        return
    try:
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_semantic_knowledge (asset_id, tenant_id, title, content_hash, content, source_type, provenance, confidence_score, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (asset_id) DO UPDATE
            SET tenant_id = EXCLUDED.tenant_id, title = EXCLUDED.title, content_hash = EXCLUDED.content_hash, content = EXCLUDED.content,
                source_type = EXCLUDED.source_type, provenance = EXCLUDED.provenance, confidence_score = EXCLUDED.confidence_score, updated_at = CURRENT_TIMESTAMP;
            """,
            (asset_id, tenant_id, title, content_hash, content, source_type, provenance, confidence_score),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"db_save_semantic_knowledge error: {e}")


def db_save_semantic_chunk(asset_id: str, chunk_index: int, content: str, vector_id: str):
    if not DB_AVAILABLE:
        return
    try:
        chunk_id = f"{asset_id}-chunk-{chunk_index}"
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_semantic_chunks (chunk_id, asset_id, chunk_index, content, vector_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (chunk_id) DO UPDATE
            SET content = EXCLUDED.content, chunk_index = EXCLUDED.chunk_index, vector_id = EXCLUDED.vector_id;
            """,
            (chunk_id, asset_id, chunk_index, content, vector_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"db_save_semantic_chunk error: {e}")


def index_knowledge(asset_id: str, title: str, content: str, source_type: str, provenance: str):
    tenant_id = get_tenant_id()

    # Save to SQL database
    db_save_semantic_knowledge(
        asset_id=asset_id,
        tenant_id=tenant_id,
        title=title,
        content=content,
        source_type=source_type,
        provenance=provenance,
    )

    import uuid

    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, asset_id))
    db_save_semantic_chunk(asset_id=asset_id, chunk_index=0, content=content, vector_id=point_id)

    if not QDRANT_AVAILABLE:
        return
    try:
        client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        embedding = get_embedding(content)
        client.upsert(
            collection_name="uawos_knowledge",
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "id": asset_id,
                        "title": title,
                        "content": content,
                        "source_type": source_type,
                        "provenance": provenance,
                        "timestamp": int(time.time()),
                        "tenant_id": tenant_id,
                    },
                )
            ],
        )
    except Exception as e:
        print(f"Error indexing knowledge in Qdrant: {e}")


def search_memory(query: str, limit: int = 5) -> list:
    if not QDRANT_AVAILABLE:
        return []
    try:
        tenant_id = get_tenant_id()
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        embedding = get_embedding(query)
        results = client.query_points(
            collection_name="uawos_memory",
            query=embedding,
            query_filter=Filter(must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]),
            limit=limit,
        )
        return [r.payload for r in results.points]
    except Exception as e:
        print(f"search_memory exception: {e}")
        return []


def search_knowledge(query: str, limit: int = 5) -> list:
    if not QDRANT_AVAILABLE:
        return []
    try:
        tenant_id = get_tenant_id()
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        embedding = get_embedding(query)
        results = client.query_points(
            collection_name="uawos_knowledge",
            query=embedding,
            query_filter=Filter(must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]),
            limit=limit,
        )
        return [r.payload for r in results.points]
    except Exception as e:
        print(f"search_knowledge exception: {e}")
        return []


def hybrid_search_knowledge(query: str, tenant_id: str = "default_tenant", limit: int = 5) -> list:
    """Hybrid lexical-vector search utilizing BM25-like ILIKE search in PostgreSQL and vector search in Qdrant, merged via Reciprocal Rank Fusion (RRF)."""
    if tenant_id == "default_tenant":
        tenant_id = get_tenant_id()

    lexical_results = []
    if DB_AVAILABLE:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            words = [f"%{w}%" for w in query.split() if len(w) > 2]
            if not words:
                words = [f"%{query}%"]

            like_clauses = " OR ".join(["sc.content ILIKE %s" for _ in words])
            sql = f"""
                SELECT sc.asset_id, sc.content, sk.title, sk.source_type, sk.provenance, sk.confidence_score
                FROM uawos_semantic_chunks sc
                JOIN uawos_semantic_knowledge sk ON sc.asset_id = sk.asset_id
                WHERE sk.tenant_id = %s AND ({like_clauses})
                LIMIT 20;
            """
            cursor.execute(sql, [tenant_id] + words)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            for r in rows:
                lexical_results.append(
                    {
                        "id": r[0],
                        "content": r[1],
                        "title": r[2],
                        "source_type": r[3],
                        "provenance": r[4],
                        "confidence_score": float(r[5]),
                        "tenant_id": tenant_id,
                    }
                )
        except Exception as e:
            print(f"Lexical search failed: {e}")

    vector_results = []
    if QDRANT_AVAILABLE:
        try:
            from qdrant_client.models import FieldCondition, Filter, MatchValue

            client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
            embedding = get_embedding(query)
            results = client.query_points(
                collection_name="uawos_knowledge",
                query=embedding,
                query_filter=Filter(must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]),
                limit=20,
            )
            for r in results.points:
                vector_results.append(r.payload)
        except Exception as e:
            print(f"Vector search in hybrid failed: {e}")

    # RRF merging
    rrf_scores = {}

    def add_to_rrf(results_list):
        seen_in_list = set()
        for rank, item in enumerate(results_list):
            content_key = item.get("content", "")
            if not content_key:
                continue
            if content_key in seen_in_list:
                continue
            seen_in_list.add(content_key)
            if content_key not in rrf_scores:
                rrf_scores[content_key] = {"item": item, "score": 0.0}
            rrf_scores[content_key]["score"] += 1.0 / (60.0 + (rank + 1))

    add_to_rrf(lexical_results)
    add_to_rrf(vector_results)

    sorted_rrf = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)
    merged = [x["item"] for x in sorted_rrf[:limit]]
    return merged


_active_locks = {}


def acquire_advisory_lock(lock_id: int):
    """Acquire a session-level PostgreSQL advisory lock (blocking).

    Raises:
        ConnectionError: If the database is offline or lock acquisition fails.
    """
    if not DB_AVAILABLE:
        raise ConnectionError("PostgreSQL database is offline (db driver unavailable).")
    try:
        conn = get_db_connection()
        conn.set_isolation_level(0)  # autocommit mode
        cursor = conn.cursor()
        cursor.execute("SELECT pg_advisory_lock(%s);", (lock_id,))
        cursor.close()
        _active_locks[lock_id] = conn
    except Exception as e:
        print(f"acquire_advisory_lock error: {e}")
        raise ConnectionError(f"Failed to acquire PostgreSQL advisory lock: {e}") from e


def release_advisory_lock(lock_id: int):
    """Release a session-level PostgreSQL advisory lock."""
    if not DB_AVAILABLE:
        return
    try:
        conn = _active_locks.pop(lock_id, None)
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pg_advisory_unlock(%s);", (lock_id,))
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"release_advisory_lock error: {e}")


# --- Objectives Helpers ---
def db_save_objective(obj: dict):
    if not DB_AVAILABLE:
        return
    try:
        tenant_id = obj.get("tenant_id")
        if not tenant_id or tenant_id == "default_tenant":
            tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_objectives (id, title, description, source_type, source_uri, owner, sponsor, priority, status, version, health_score, confidence_score, dependencies, history, tenant_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET title = EXCLUDED.title, description = EXCLUDED.description, source_type = EXCLUDED.source_type,
                source_uri = EXCLUDED.source_uri, owner = EXCLUDED.owner, sponsor = EXCLUDED.sponsor,
                priority = EXCLUDED.priority, status = EXCLUDED.status, version = EXCLUDED.version,
                health_score = EXCLUDED.health_score, confidence_score = EXCLUDED.confidence_score,
                dependencies = EXCLUDED.dependencies, history = EXCLUDED.history, tenant_id = EXCLUDED.tenant_id,
                updated_at = CURRENT_TIMESTAMP;
        """,
            (
                obj["id"],
                obj["title"],
                obj["description"],
                obj["source_type"],
                obj["source_uri"],
                obj["owner"],
                obj["sponsor"],
                obj["priority"],
                obj["status"],
                obj["version"],
                obj["health_score"],
                obj["confidence_score"],
                json.dumps(obj["dependencies"]),
                json.dumps(obj["history"]),
                tenant_id,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error saving objective {obj.get('id')}: {e}")


def db_save_all_objectives(objectives: dict):
    for obj in objectives.values():
        db_save_objective(obj)


def db_load_objectives() -> dict:
    if not DB_AVAILABLE:
        return {"objectives": {}}
    try:
        tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, description, source_type, source_uri, owner, sponsor, priority, status, version, health_score, confidence_score, dependencies, history, tenant_id FROM uawos_objectives WHERE tenant_id = %s;",
            (tenant_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        objs = {}
        for r in rows:
            objs[r[0]] = {
                "id": r[0],
                "title": r[1],
                "description": r[2],
                "source_type": r[3],
                "source_uri": r[4],
                "owner": r[5],
                "sponsor": r[6],
                "priority": r[7],
                "status": r[8],
                "version": r[9],
                "health_score": float(r[10]),
                "confidence_score": float(r[11]),
                "dependencies": (
                    r[12] if isinstance(r[12], list) else json.loads(r[12] if isinstance(r[12], str) else "[]")
                ),
                "history": (
                    r[13] if isinstance(r[13], list) else json.loads(r[13] if isinstance(r[13], str) else "[]")
                ),
                "tenant_id": r[14],
            }
        return {"objectives": objs}
    except Exception as e:
        print(f"Database error loading objectives: {e}")
        return {"objectives": {}}


# --- Outcomes Helpers ---
def db_save_outcome(out: dict):
    if not DB_AVAILABLE:
        return
    try:
        tenant_id = out.get("tenant_id")
        if not tenant_id or tenant_id == "default_tenant":
            tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_outcomes (id, objective_id, title, metric, unit, weight, dependencies, confidence_score, owner, baseline_state, target_state, current_state, forecasted_state, tenant_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET objective_id = EXCLUDED.objective_id, title = EXCLUDED.title, metric = EXCLUDED.metric,
                unit = EXCLUDED.unit, weight = EXCLUDED.weight, dependencies = EXCLUDED.dependencies,
                confidence_score = EXCLUDED.confidence_score, owner = EXCLUDED.owner, baseline_state = EXCLUDED.baseline_state,
                target_state = EXCLUDED.target_state, current_state = EXCLUDED.current_state, forecasted_state = EXCLUDED.forecasted_state,
                tenant_id = EXCLUDED.tenant_id, updated_at = CURRENT_TIMESTAMP;
        """,
            (
                out["id"],
                out["objective_id"],
                out["title"],
                out["metric"],
                out["unit"],
                out["weight"],
                json.dumps(out["dependencies"]),
                out["confidence_score"],
                out["owner"],
                out["baseline_state"],
                out["target_state"],
                out["current_state"],
                out["forecasted_state"],
                tenant_id,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error saving outcome {out.get('id')}: {e}")


def db_save_all_outcomes(outcomes: dict):
    for out in outcomes.values():
        db_save_outcome(out)


def db_load_outcomes() -> dict:
    if not DB_AVAILABLE:
        return {"outcomes": {}}
    try:
        tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, objective_id, title, metric, unit, weight, dependencies, confidence_score, owner, baseline_state, target_state, current_state, forecasted_state, tenant_id FROM uawos_outcomes WHERE tenant_id = %s;",
            (tenant_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        outs = {}
        for r in rows:
            outs[r[0]] = {
                "id": r[0],
                "objective_id": r[1],
                "title": r[2],
                "metric": r[3],
                "unit": r[4],
                "weight": float(r[5]),
                "dependencies": (
                    r[6] if isinstance(r[6], list) else json.loads(r[6] if isinstance(r[6], str) else "[]")
                ),
                "confidence_score": float(r[7]),
                "owner": r[8],
                "baseline_state": float(r[9]),
                "target_state": float(r[10]),
                "current_state": float(r[11]) if r[11] is not None else None,
                "forecasted_state": float(r[12]) if r[12] is not None else None,
                "tenant_id": r[13],
            }
        return {"outcomes": outs}
    except Exception as e:
        print(f"Database error loading outcomes: {e}")
        return {"outcomes": {}}


# --- Plans Helpers ---
def db_save_plan(plan: dict):
    if not DB_AVAILABLE:
        return
    try:
        tenant_id = plan.get("tenant_id")
        if not tenant_id or tenant_id == "default_tenant":
            tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_plans (id, objective_id, title, steps, cost_estimate, duration_estimate, resource_requirements, success_probability, status, version, risks, assumptions, is_alternative, history, tenant_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET objective_id = EXCLUDED.objective_id, title = EXCLUDED.title, steps = EXCLUDED.steps,
                cost_estimate = EXCLUDED.cost_estimate, duration_estimate = EXCLUDED.duration_estimate,
                resource_requirements = EXCLUDED.resource_requirements, success_probability = EXCLUDED.success_probability,
                status = EXCLUDED.status, version = EXCLUDED.version, risks = EXCLUDED.risks,
                assumptions = EXCLUDED.assumptions, is_alternative = EXCLUDED.is_alternative, history = EXCLUDED.history,
                tenant_id = EXCLUDED.tenant_id, updated_at = CURRENT_TIMESTAMP;
        """,
            (
                plan["id"],
                plan["objective_id"],
                plan["title"],
                json.dumps(plan["steps"]),
                plan["cost_estimate"],
                plan["duration_estimate"],
                json.dumps(plan["resource_requirements"]),
                plan["success_probability"],
                plan["status"],
                plan["version"],
                json.dumps(plan["risks"]),
                json.dumps(plan["assumptions"]),
                plan["is_alternative"],
                json.dumps(plan["history"]),
                tenant_id,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error saving plan {plan.get('id')}: {e}")


def db_save_all_plans(plans: dict):
    for plan in plans.values():
        db_save_plan(plan)


def db_load_plans() -> dict:
    if not DB_AVAILABLE:
        return {"plans": {}}
    try:
        tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, objective_id, title, steps, cost_estimate, duration_estimate, resource_requirements, success_probability, status, version, risks, assumptions, is_alternative, history, tenant_id FROM uawos_plans WHERE tenant_id = %s;",
            (tenant_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        plans = {}
        for r in rows:
            plans[r[0]] = {
                "id": r[0],
                "objective_id": r[1],
                "title": r[2],
                "steps": (r[3] if isinstance(r[3], list) else json.loads(r[3] if isinstance(r[3], str) else "[]")),
                "cost_estimate": float(r[4]),
                "duration_estimate": int(r[5]),
                "resource_requirements": (
                    r[6] if isinstance(r[6], list) else json.loads(r[6] if isinstance(r[6], str) else "[]")
                ),
                "success_probability": float(r[7]),
                "status": r[8],
                "version": int(r[9]),
                "risks": (r[10] if isinstance(r[10], list) else json.loads(r[10] if isinstance(r[10], str) else "[]")),
                "assumptions": (
                    r[11] if isinstance(r[11], list) else json.loads(r[11] if isinstance(r[11], str) else "[]")
                ),
                "is_alternative": bool(r[12]),
                "history": (
                    r[13] if isinstance(r[13], list) else json.loads(r[13] if isinstance(r[13], str) else "[]")
                ),
                "tenant_id": r[14],
            }
        return {"plans": plans}
    except Exception as e:
        print(f"Database error loading plans: {e}")
        return {"plans": {}}


# --- Workflows Helpers ---
def db_save_workflow(wf: dict):
    if not DB_AVAILABLE:
        return
    try:
        tenant_id = wf.get("tenant_id")
        if not tenant_id or tenant_id == "default_tenant":
            tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_workflows (id, plan_id, title, tasks, dependencies, state, version, governed, history, tenant_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET plan_id = EXCLUDED.plan_id, title = EXCLUDED.title, tasks = EXCLUDED.tasks,
                dependencies = EXCLUDED.dependencies, state = EXCLUDED.state, version = EXCLUDED.version,
                governed = EXCLUDED.governed, history = EXCLUDED.history, tenant_id = EXCLUDED.tenant_id,
                updated_at = CURRENT_TIMESTAMP;
        """,
            (
                wf["id"],
                wf["plan_id"],
                wf["title"],
                json.dumps(wf["tasks"]),
                json.dumps(wf["dependencies"]),
                wf["state"],
                wf["version"],
                wf["governed"],
                json.dumps(wf["history"]),
                tenant_id,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error saving workflow {wf.get('id')}: {e}")


def db_save_all_workflows(workflows: dict):
    for wf in workflows.values():
        db_save_workflow(wf)


def db_load_workflows() -> dict:
    if not DB_AVAILABLE:
        return {"workflows": {}}
    try:
        tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, plan_id, title, tasks, dependencies, state, version, governed, history, tenant_id FROM uawos_workflows WHERE tenant_id = %s;",
            (tenant_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        wfs = {}
        for r in rows:
            wfs[r[0]] = {
                "id": r[0],
                "plan_id": r[1],
                "title": r[2],
                "tasks": (r[3] if isinstance(r[3], list) else json.loads(r[3] if isinstance(r[3], str) else "[]")),
                "dependencies": (
                    r[4] if isinstance(r[4], list) else json.loads(r[4] if isinstance(r[4], str) else "[]")
                ),
                "state": r[5],
                "version": int(r[6]),
                "governed": bool(r[7]),
                "history": (r[8] if isinstance(r[8], list) else json.loads(r[8] if isinstance(r[8], str) else "[]")),
                "tenant_id": r[9],
            }
        return {"workflows": wfs}
    except Exception as e:
        print(f"Database error loading workflows: {e}")
        return {"workflows": {}}


# --- Actions Helpers ---
def db_save_action(act: dict):
    if not DB_AVAILABLE:
        return
    try:
        tenant_id = act.get("tenant_id")
        if not tenant_id or tenant_id == "default_tenant":
            tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_actions (id, workflow_id, name, owner, dependencies, priority, budget, deadline, status, approval_required, tenant_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET workflow_id = EXCLUDED.workflow_id, name = EXCLUDED.name, owner = EXCLUDED.owner,
                dependencies = EXCLUDED.dependencies, priority = EXCLUDED.priority, budget = EXCLUDED.budget,
                deadline = EXCLUDED.deadline, status = EXCLUDED.status, approval_required = EXCLUDED.approval_required,
                tenant_id = EXCLUDED.tenant_id;
        """,
            (
                act["id"],
                act.get("workflow_id", ""),
                act["name"],
                act.get("owner", "Unassigned"),
                json.dumps(act.get("dependencies", [])),
                act.get("priority", "Medium"),
                act.get("budget", 0.0),
                act.get("deadline", 0),
                act.get("status", "pending"),
                act.get("approval_required", False),
                tenant_id,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error saving action {act.get('id')}: {e}")
        raise e


def db_save_all_actions(actions: dict):
    for act in actions.values():
        db_save_action(act)


def db_load_actions() -> dict:
    if not DB_AVAILABLE:
        return {"actions": {}}
    try:
        tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, workflow_id, name, owner, dependencies, priority, budget, deadline, status, approval_required, tenant_id FROM uawos_actions WHERE tenant_id = %s;",
            (tenant_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        acts = {}
        for r in rows:
            acts[r[0]] = {
                "id": r[0],
                "workflow_id": r[1],
                "name": r[2],
                "owner": r[3],
                "dependencies": (
                    r[4] if isinstance(r[4], list) else json.loads(r[4] if isinstance(r[4], str) else "[]")
                ),
                "priority": r[5],
                "budget": float(r[6]),
                "deadline": int(r[7]),
                "status": r[8],
                "approval_required": bool(r[9]),
                "tenant_id": r[10],
            }
        return {"actions": acts}
    except Exception as e:
        print(f"Database error loading actions: {e}")
        return {"actions": {}}


# --- Channels Helpers ---
def db_create_channel(channel_id: str, name: str, tenant_id: str = "default_tenant") -> dict:
    if not DB_AVAILABLE:
        return {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_channels (channel_id, name, tenant_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (channel_id) DO UPDATE
            SET name = EXCLUDED.name, tenant_id = EXCLUDED.tenant_id;
            """,
            (channel_id, name, tenant_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"channel_id": channel_id, "name": name, "tenant_id": tenant_id}
    except Exception as e:
        print(f"db_create_channel error: {e}")
        return {}


def db_add_channel_member(channel_id: str, user_id: str, tenant_id: str = "default_tenant") -> bool:
    if not DB_AVAILABLE:
        return False
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_channel_members (channel_id, user_id, tenant_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (channel_id, user_id) DO NOTHING;
            """,
            (channel_id, user_id, tenant_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"db_add_channel_member error: {e}")
        return False


def db_get_channel_members(channel_id: str) -> list:
    if not DB_AVAILABLE:
        return []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM uawos_channel_members WHERE channel_id = %s;", (channel_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        print(f"db_get_channel_members error: {e}")
        return []


def db_get_channels(tenant_id: str = "default_tenant") -> list:
    if not DB_AVAILABLE:
        return []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT channel_id, name FROM uawos_channels WHERE tenant_id = %s;", (tenant_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{"channel_id": r[0], "name": r[1]} for r in rows]
    except Exception as e:
        print(f"db_get_channels error: {e}")
        return []


# --- Artifacts Helpers ---
def db_save_artifact(
    artifact_id: str,
    name: str,
    file_path: str,
    file_hash: str,
    objective_id: str = None,
    action_id: str = None,
    tenant_id: str = "default_tenant",
) -> dict:
    if not DB_AVAILABLE:
        return {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_artifacts (artifact_id, name, file_path, file_hash, objective_id, action_id, tenant_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (artifact_id) DO UPDATE
            SET name = EXCLUDED.name, file_path = EXCLUDED.file_path, file_hash = EXCLUDED.file_hash,
                objective_id = EXCLUDED.objective_id, action_id = EXCLUDED.action_id, tenant_id = EXCLUDED.tenant_id;
            """,
            (artifact_id, name, file_path, file_hash, objective_id, action_id, tenant_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {
            "artifact_id": artifact_id,
            "name": name,
            "file_path": file_path,
            "file_hash": file_hash,
            "objective_id": objective_id,
            "action_id": action_id,
            "tenant_id": tenant_id,
        }
    except Exception as e:
        print(f"db_save_artifact error: {e}")
        return {}


def db_get_action_artifacts(action_id: str) -> list:
    if not DB_AVAILABLE:
        return []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT artifact_id, name, file_path, file_hash, objective_id, action_id, tenant_id FROM uawos_artifacts WHERE action_id = %s;",
            (action_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [
            {
                "artifact_id": r[0],
                "name": r[1],
                "file_path": r[2],
                "file_hash": r[3],
                "objective_id": r[4],
                "action_id": r[5],
                "tenant_id": r[6],
            }
            for r in rows
        ]
    except Exception as e:
        print(f"db_get_action_artifacts error: {e}")
        return []


# --- Subscriptions Helpers ---
def db_save_subscription(tenant_id: str, plan_type: str, status: str, expires_at_timestamp: float = None) -> dict:
    if not DB_AVAILABLE:
        return {}
    try:
        import datetime

        expires_at = datetime.datetime.fromtimestamp(expires_at_timestamp) if expires_at_timestamp else None
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uawos_subscriptions (tenant_id, plan_type, status, expires_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (tenant_id) DO UPDATE
            SET plan_type = EXCLUDED.plan_type, status = EXCLUDED.status, expires_at = EXCLUDED.expires_at;
            """,
            (tenant_id, plan_type, status, expires_at),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {
            "tenant_id": tenant_id,
            "plan_type": plan_type,
            "status": status,
            "expires_at": str(expires_at) if expires_at else None,
        }
    except Exception as e:
        print(f"db_save_subscription error: {e}")
        return {}


def db_get_subscription(tenant_id: str) -> dict:
    if not DB_AVAILABLE:
        return {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tenant_id, plan_type, status, expires_at FROM uawos_subscriptions WHERE tenant_id = %s;",
            (tenant_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return {
                "tenant_id": row[0],
                "plan_type": row[1],
                "status": row[2],
                "expires_at": str(row[3]) if row[3] else None,
            }
        return {}
    except Exception as e:
        print(f"db_get_subscription error: {e}")
        return {}


# Initialize schemas and collections on import
init_db()
init_qdrant()
