import traceback

import uawos_agent_runtime
import uawos_semantic_kernel_adapter

ctx = uawos_agent_runtime.UAWOSContext(actor="test")
ctx.tenant_id = "default_tenant"

print("Saving memory...")
try:
    saved = uawos_semantic_kernel_adapter.SemanticKernelVectorBridge.save_memory(
        "knowledge_base",
        "UAWOS is an event-driven AI workforce platform.",
        "kb-001",
        ctx,
    )
    print("Saved status:", saved)
except Exception:
    traceback.print_exc()

print("Searching memory...")
try:
    from qdrant_client import QdrantClient

    import uawos_db

    QDRANT_HOST = "127.0.0.1"
    QDRANT_PORT = 6333
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    print("Collection points:")
    pts = client.scroll(collection_name="knowledge_base", limit=5)
    print(pts)

    embedding = uawos_db.get_embedding("event-driven")
    print("Embedding length:", len(embedding))

    results = client.query_points(collection_name="knowledge_base", query=embedding, limit=5)
    print("Qdrant raw search results:", results)
except Exception:
    print("Direct Qdrant search failed:")
    traceback.print_exc()

try:
    res = uawos_semantic_kernel_adapter.SemanticKernelVectorBridge.search_memory(
        "knowledge_base", "event-driven", 5, ctx
    )
    print("Adapter Search Result:", res)
except Exception:
    print("Adapter Search failed:")
    traceback.print_exc()
