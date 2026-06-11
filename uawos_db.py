# uawos_db.py
import hashlib
import json
import os
import time
import urllib.request

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

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5435))
POSTGRES_DB = os.environ.get("POSTGRES_DB", "marquez")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "marquez")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "marquez")
POSTGRES_CONN_STR = os.environ.get(
    "POSTGRES_CONN_STR",
    f"host={POSTGRES_HOST} port={POSTGRES_PORT} dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD}",
)
QDRANT_HOST = os.environ.get("QDRANT_HOST", "127.0.0.1")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")


def get_db_connection():
    if not DB_AVAILABLE:
        raise RuntimeError("psycopg2 is not installed.")
    return psycopg2.connect(POSTGRES_CONN_STR)


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
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(50) DEFAULT 'default_tenant';")
        cursor.execute("ALTER TABLE uawos_state ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(50) DEFAULT 'default_tenant';")
        try:
            cursor.execute("ALTER TABLE uawos_state DROP CONSTRAINT IF EXISTS uawos_state_pkey;")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE uawos_state ADD CONSTRAINT uawos_state_pkey PRIMARY KEY (key, tenant_id);")
        except Exception:
            pass
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
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
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
            f"{OLLAMA_BASE_URL}/api/embeddings",
            data=req_data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=2.0) as response:
            resp = json.loads(response.read().decode("utf-8"))
            emb = resp.get("embedding")
            if emb and len(emb) == 384:
                return emb
            elif emb:
                # Truncate or pad to 384
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


# PostgreSQL State Helpers
def db_get_state(key: str, default_fn, tenant_id: str = "default_tenant") -> dict:
    if not DB_AVAILABLE:
        return default_fn() if default_fn else None
    try:
        if tenant_id == "default_tenant":
            from uawos_context import get_tenant_id
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
    return default_fn() if default_fn else None


def db_save_state(key: str, state: dict, tenant_id: str = "default_tenant"):
    if not DB_AVAILABLE:
        return
    try:
        if tenant_id == "default_tenant":
            from uawos_context import get_tenant_id
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


# Qdrant Indexing Helpers
def index_memory(memory_id: int, content: str, scope: str, owner: str):
    if not QDRANT_AVAILABLE:
        return
    try:
        from uawos_context import get_tenant_id
        tenant_id = get_tenant_id()
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
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


def index_knowledge(
    asset_id: str, title: str, content: str, source_type: str, provenance: str
):
    if not QDRANT_AVAILABLE:
        return
    try:
        from uawos_context import get_tenant_id
        tenant_id = get_tenant_id()
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        embedding = get_embedding(content)
        import uuid

        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, asset_id))
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
        from uawos_context import get_tenant_id
        tenant_id = get_tenant_id()
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        embedding = get_embedding(query)
        results = client.query_points(
            collection_name="uawos_memory",
            query=embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="tenant_id",
                        match=MatchValue(value=tenant_id)
                    )
                ]
            ),
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
        from uawos_context import get_tenant_id
        tenant_id = get_tenant_id()
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        embedding = get_embedding(query)
        results = client.query_points(
            collection_name="uawos_knowledge",
            query=embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="tenant_id",
                        match=MatchValue(value=tenant_id)
                    )
                ]
            ),
            limit=limit,
        )
        return [r.payload for r in results.points]
    except Exception as e:
        print(f"search_knowledge exception: {e}")
        return []


# ----------------- UAWOS Relational SQL Helpers -----------------


# Objectives
def db_save_objective(obj: dict):
    if not DB_AVAILABLE:
        return
    try:
        tenant_id = obj.get("tenant_id")
        if not tenant_id or tenant_id == "default_tenant":
            from uawos_context import get_tenant_id
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
        from uawos_context import get_tenant_id
        tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, description, source_type, source_uri, owner, sponsor, priority, status, version, health_score, confidence_score, dependencies, history, tenant_id FROM uawos_objectives WHERE tenant_id = %s;",
            (tenant_id,)
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
                    r[12]
                    if isinstance(r[12], list)
                    else json.loads(r[12] if isinstance(r[12], str) else "[]")
                ),
                "history": (
                    r[13]
                    if isinstance(r[13], list)
                    else json.loads(r[13] if isinstance(r[13], str) else "[]")
                ),
                "tenant_id": r[14],
            }
        return {"objectives": objs}
    except Exception as e:
        print(f"Database error loading objectives: {e}")
        return {"objectives": {}}


# Outcomes
def db_save_outcome(out: dict):
    if not DB_AVAILABLE:
        return
    try:
        tenant_id = out.get("tenant_id")
        if not tenant_id or tenant_id == "default_tenant":
            from uawos_context import get_tenant_id
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
        from uawos_context import get_tenant_id
        tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, objective_id, title, metric, unit, weight, dependencies, confidence_score, owner, baseline_state, target_state, current_state, forecasted_state, tenant_id FROM uawos_outcomes WHERE tenant_id = %s;",
            (tenant_id,)
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
                    r[6]
                    if isinstance(r[6], list)
                    else json.loads(r[6] if isinstance(r[6], str) else "[]")
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


# Plans
def db_save_plan(plan: dict):
    if not DB_AVAILABLE:
        return
    try:
        tenant_id = plan.get("tenant_id")
        if not tenant_id or tenant_id == "default_tenant":
            from uawos_context import get_tenant_id
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
        from uawos_context import get_tenant_id
        tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, objective_id, title, steps, cost_estimate, duration_estimate, resource_requirements, success_probability, status, version, risks, assumptions, is_alternative, history, tenant_id FROM uawos_plans WHERE tenant_id = %s;",
            (tenant_id,)
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
                "steps": (
                    r[3]
                    if isinstance(r[3], list)
                    else json.loads(r[3] if isinstance(r[3], str) else "[]")
                ),
                "cost_estimate": float(r[4]),
                "duration_estimate": int(r[5]),
                "resource_requirements": (
                    r[6]
                    if isinstance(r[6], list)
                    else json.loads(r[6] if isinstance(r[6], str) else "[]")
                ),
                "success_probability": float(r[7]),
                "status": r[8],
                "version": int(r[9]),
                "risks": (
                    r[10]
                    if isinstance(r[10], list)
                    else json.loads(r[10] if isinstance(r[10], str) else "[]")
                ),
                "assumptions": (
                    r[11]
                    if isinstance(r[11], list)
                    else json.loads(r[11] if isinstance(r[11], str) else "[]")
                ),
                "is_alternative": bool(r[12]),
                "history": (
                    r[13]
                    if isinstance(r[13], list)
                    else json.loads(r[13] if isinstance(r[13], str) else "[]")
                ),
                "tenant_id": r[14],
            }
        return {"plans": plans}
    except Exception as e:
        print(f"Database error loading plans: {e}")
        return {"plans": {}}


# Workflows
def db_save_workflow(wf: dict):
    if not DB_AVAILABLE:
        return
    try:
        tenant_id = wf.get("tenant_id")
        if not tenant_id or tenant_id == "default_tenant":
            from uawos_context import get_tenant_id
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
        from uawos_context import get_tenant_id
        tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, plan_id, title, tasks, dependencies, state, version, governed, history, tenant_id FROM uawos_workflows WHERE tenant_id = %s;",
            (tenant_id,)
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
                "tasks": (
                    r[3]
                    if isinstance(r[3], list)
                    else json.loads(r[3] if isinstance(r[3], str) else "[]")
                ),
                "dependencies": (
                    r[4]
                    if isinstance(r[4], list)
                    else json.loads(r[4] if isinstance(r[4], str) else "[]")
                ),
                "state": r[5],
                "version": int(r[6]),
                "governed": bool(r[7]),
                "history": (
                    r[8]
                    if isinstance(r[8], list)
                    else json.loads(r[8] if isinstance(r[8], str) else "[]")
                ),
                "tenant_id": r[9],
            }
        return {"workflows": wfs}
    except Exception as e:
        print(f"Database error loading workflows: {e}")
        return {"workflows": {}}


# Actions
def db_save_action(act: dict):
    if not DB_AVAILABLE:
        return
    try:
        tenant_id = act.get("tenant_id")
        if not tenant_id or tenant_id == "default_tenant":
            from uawos_context import get_tenant_id
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
                act["workflow_id"],
                act["name"],
                act["owner"],
                json.dumps(act["dependencies"]),
                act["priority"],
                act["budget"],
                act["deadline"],
                act["status"],
                act["approval_required"],
                tenant_id,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error saving action {act.get('id')}: {e}")


def db_save_all_actions(actions: dict):
    for act in actions.values():
        db_save_action(act)


def db_load_actions() -> dict:
    if not DB_AVAILABLE:
        return {"actions": {}}
    try:
        from uawos_context import get_tenant_id
        tenant_id = get_tenant_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, workflow_id, name, owner, dependencies, priority, budget, deadline, status, approval_required, tenant_id FROM uawos_actions WHERE tenant_id = %s;",
            (tenant_id,)
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
                    r[4]
                    if isinstance(r[4], list)
                    else json.loads(r[4] if isinstance(r[4], str) else "[]")
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


# Initialize immediately when imported
init_db()
init_qdrant()
