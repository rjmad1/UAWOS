# Operational Runbook: [Incident Type/System Outage]
# Location: /runbooks/

## 1. Metadata
*   **Incident ID**: [e.g., RUN-001]
*   **Target Component**: [e.g., SQLite Database Connection Outage]
*   **SRE Owner**: [SRE Agent / Human On-Call]
*   **Severity Rating**: [Low / Medium / High / Critical]

## 2. Symptom Identification
*Describe the metrics, alerts, or user symptoms that identify this incident condition.*
*   **Trigger Alert**: `DB_Connection_Failure_Rate_High`
*   **SLI Mismatch**: API Success Rate drops below 99.0% over 5 minutes.
*   **Log Signature**: `OperationalError: database is locked` or `sqlite3.OperationalError`

## 3. Immediate Diagnostics Steps
*Sequential steps for human or agent operators to diagnose root cause.*
1.  **Check Process Locks**: Identify if another agent or system process is holding a write lock on the SQLite file.
    ```bash
    fuser -v headroom_memory.db
    ```
2.  **Verify Disk Usage**: Check if the host volume is out of storage capacity.
    ```bash
    df -h
    ```
3.  **Inspect Active Connections**: Query database metrics to see current active sessions.

## 4. Remediation Steps
*Steps to execute to restore the system to stable state.*
1.  **Release Stuck Locks**: If a hung agent process has locked the DB, safely terminate the process:
    ```bash
    kill -15 [process_id]
    ```
2.  **Restore DB from Backup**: If SQLite database file is corrupted, restore from the latest automated snapshot:
    ```bash
    cp backups/headroom_memory_latest.db headroom_memory.db
    ```
3.  **Restart Service Daemon**: Restart the dashboard daemon script to reconnect:
    ```bash
    powershell .\start-dashboard.ps1
    ```

## 5. Post-Remediation Verification
*How to verify system is operating normally again.*
*   Verify HTTP status returns 200 on health check endpoint.
*   Validate Prometheus metrics show error budget usage has stabilized.
*   Confirm new agent runs can write to the memory file without locking errors.

## 6. Escalation Matrix
*If remediation fails to solve the issue within 10 minutes:*
1.  Escalate to Human On-Call Engineer.
2.  Route alert context to Slack/Teams channel: `#sre-incidents`.
