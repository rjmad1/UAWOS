import json
import urllib.request

NEO4J_HOST = "127.0.0.1"
NEO4J_HTTP_PORT = 7474


def test_neo4j():
    url = f"http://{NEO4J_HOST}:{NEO4J_HTTP_PORT}/db/neo4j/tx/commit"

    # Query to check Neo4j status and version
    payload = {"statements": [{"statement": "RETURN 1 as val"}]}

    try:
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=req_data, headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("Neo4j Response:", data)
    except Exception as e:
        print("Failed to query Neo4j:", e)


if __name__ == "__main__":
    test_neo4j()
