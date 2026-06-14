# UAWOS Site Reliability Engineering (SRE) Runbook

This runbook contains Standard Operating Procedures (SOPs) for managing and troubleshooting operational issues in the Universal AI Workforce Operating System (UAWOS) platform.

---

## 1. PostgreSQL Lock Contention & Concurrency Control

### 1.1 Risk Profile
Multiple autonomous agent workforce threads performing high-frequency read-modify-write loops on `uawos_state` and task tables can trigger database transaction lock contentions and deadlocks.

### 1.2 Detection & Alerts
* **Log Signature:** `psycopg2.errors.DeadlockDetected` or `LockNotAvailable`.
* **Telemetry Metric:** High query latency (>1.5s) on `db_save_state` or `db_save_objective`.
* **Diagnostic Query:** Run the following query in the Postgres container to inspect active locks:
  ```sql
  SELECT pid, age(clock_timestamp(), query_start), usename, query, state 
  FROM pg_stat_activity 
  WHERE state != 'idle' AND query ILIKE '%uawos_%';
  ```

### 1.3 Resolution Procedure (SOP-PG-01)
1. **Identify Blocked PIDs:** Determine the blocked and blocking process IDs (PIDs) using the diagnostic query.
2. **Graceful Terminate:** Try to terminate the blocking query gracefully:
   ```sql
   SELECT pg_cancel_backend(blocking_pid);
   ```
3. **Hard Kill:** If the lock persists, forcefully terminate the backend connection:
   ```sql
   SELECT pg_terminate_backend(blocking_pid);
   ```
4. **Enforce Lock Helpers:** Verify that all python code modifying state files utilizes the `state_transaction` context manager from `uawos_state_utils.py`, which leverages PostgreSQL advisory locks to guarantee atomic read-modify-write transitions.

---

## 2. Outbound Model Gateway & Ollama Context Saturation

### 2.1 Risk Profile
High token loads or concurrency spikes in agent prompt processing can saturate the local Ollama daemon context memory (TinyLlama / DeepSeek), causing HTTP 503 errors, 404 Model Not Found, or slow prompt completions (>30s).

### 2.2 Detection & Alerts
* **Log Signature:** `urllib.error.HTTPError: HTTP Error 503` or `urllib.error.HTTPError: HTTP Error 404`.
* **Telemetry Metric:** LLM response times exceeding the 1.5s latency threshold.

### 2.3 Resolution Procedure (SOP-LLM-02)
1. **BFF Fallback Validation:** Confirm that the BFF server's `Weaverouter` successfully falls back to the local Ollama node if the remote provider is unresponsive.
2. **Context Clearance:** Restart the Ollama daemon container to flush active memory contexts:
   ```powershell
   docker compose restart core-ollama
   ```
3. **Config Check:** Inspect the system environment variables and ensure that `OLLAMA_BASE_URL` is set correctly:
   ```powershell
   $env:OLLAMA_BASE_URL = "http://127.0.0.1:11434"
   ```
4. **Reduce Concurrency limits:** Adjust the `max_concurrency` setting in `uawos_agent_runtime.py` to throttle agent prompts during peak periods.

---

## 3. Qdrant Vector DB Storage & Memory Thresholds

### 3.1 Risk Profile
Memory-intensive semantic chunk indexing and hybrid lexical-vector searches can saturate the Qdrant RAM limit, leading to write rejections or cluster out-of-memory crashes.

### 3.2 Detection & Alerts
* **Log Signature:** `qdrant_client.http.exceptions.UnexpectedResponse` with status `500` or Out of Memory.
* **Port Probing Check:** Port `6333` fails to accept socket connections.

### 3.3 Resolution Procedure (SOP-VDB-03)
1. **Check Memory Footprint:** View container resource allocations:
   ```powershell
   docker stats uawos-qdrant
   ```
2. **Flush Memory Collections:** If memory usage exceeds 90%, optimize the collections to release indexes:
   ```powershell
   Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:6333/collections/uawos_memory/optimize"
   ```
3. **Scale Resource Allocations:** Increase memory thresholds inside the `docker-compose.yml` configuration (change memory limit to `1gb` or `2gb` if necessary).
4. **Clean Ephemeral Session Vectors:** Run the purge script in `scratch/recreate_and_consume.py` to prune expired tenant sliding context indices from vector storage.

---

## 4. Standalone Marker Service Isolation (GPLv3 Compliance)

### 4.1 Risk Profile
Marker PDF parsing libraries use copyleft GPLv3 licenses. Direct imports inside the core UAWOS python virtual environment violate legal licensing controls (POL-03).

### 4.2 Resolution & Enforcement (SOP-SEC-04)
1. **Never Import Marker:** Check python source files to ensure `import marker` is never called.
2. **Sandboxed Container:** Ensure that `uawos-marker-service` runs in an isolated container on port `5001`.
3. **REST Communication:** The DTASE engine (`uawos_dtase.py`) must communicate with the Marker service exclusively over REST APIs (port 5001), preventing any static or dynamic library linking.
