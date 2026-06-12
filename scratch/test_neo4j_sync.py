import json
import urllib.request

NEO4J_HOST = "127.0.0.1"
NEO4J_HTTP_PORT = 7474
NEO4J_URL = f"http://{NEO4J_HOST}:{NEO4J_HTTP_PORT}"


def execute_cypher(statement: str, parameters: dict = None) -> dict:
    url = f"{NEO4J_URL}/db/neo4j/tx/commit"
    payload = {"statements": [{"statement": statement, "parameters": parameters or {}}]}
    try:
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=req_data, headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print("Cypher execute error:", e)
        return None


def _get_neo4j_label(entity_id: str) -> str:
    if entity_id.startswith("KNW-"):
        return "KnowledgeAsset"
    elif entity_id.startswith("OBJ-"):
        return "Objective"
    elif entity_id.startswith("PLN-"):
        return "Plan"
    elif entity_id.startswith("OUT-"):
        return "Outcome"
    elif entity_id.startswith("WRK-"):
        return "Workflow"
    elif entity_id.startswith("ACT-"):
        return "Action"
    return "Entity"


def sync_asset_to_neo4j(asset: dict) -> bool:
    label = _get_neo4j_label(asset["id"])
    query = f"""
    MERGE (a:{label} {{id: $id}})
    SET a.title = $title,
        a.content = $content,
        a.source_type = $source_type,
        a.source_uri = $source_uri,
        a.provenance = $provenance,
        a.confidence_score = $confidence_score,
        a.timestamp = $timestamp
    """
    res = execute_cypher(query, asset)
    return res is not None and not res.get("errors")


def sync_relationship_to_neo4j(rel: dict) -> bool:
    src_label = _get_neo4j_label(rel["source"])
    tgt_label = _get_neo4j_label(rel["target"])
    rel_type = rel["relationship"]
    if not rel_type.replace("_", "").isalnum():
        return False

    query = f"""
    MERGE (s:{src_label} {{id: $source_id}})
    MERGE (t:{tgt_label} {{id: $target_id}})
    WITH s, t
    MERGE (s)-[r:{rel_type}]->(t)
    SET r.id = $rel_id,
        r.confidence = $confidence,
        r.provenance = $provenance
    """
    params = {
        "source_id": rel["source"],
        "target_id": rel["target"],
        "rel_id": rel["id"],
        "confidence": rel["confidence"],
        "provenance": rel.get("provenance", "Sync link"),
    }
    res = execute_cypher(query, params)
    return res is not None and not res.get("errors")


if __name__ == "__main__":
    # Test sync asset
    asset = {
        "id": "KNW-101",
        "title": "OAuth Spec",
        "content": "OAuth credentials specification details",
        "source_type": "document",
        "source_uri": "s3://oauth",
        "provenance": "Security team",
        "confidence_score": 98.0,
        "timestamp": 123456789,
    }
    print("Sync asset success:", sync_asset_to_neo4j(asset))

    # Test sync relationship
    rel = {
        "id": "REL-01",
        "source": "KNW-101",
        "relationship": "DEFINES_AUTH_FOR",
        "target": "OBJ-101",
        "confidence": 95.0,
        "provenance": "Manual link",
    }
    print("Sync relationship success:", sync_relationship_to_neo4j(rel))

    # Check if they exist in Neo4j
    check_query = """
    MATCH (a:KnowledgeAsset {id: 'KNW-101'})-[r:DEFINES_AUTH_FOR]->(o:Objective {id: 'OBJ-101'})
    RETURN a.title as title, r.confidence as conf, o.id as obj_id
    """
    res = execute_cypher(check_query)
    print("Verification query results:", res)
