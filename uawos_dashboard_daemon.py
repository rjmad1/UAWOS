#!/usr/bin/env python3
import json
import os
import socket
import subprocess
import sys
import threading
import time

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse

import uawos_traceability

# Safe imports for dynamic modules to prevent thread deadlocks
try:
    import uawos_dtase
except ImportError:
    uawos_dtase = None

try:
    import uawos_budget
except ImportError:
    uawos_budget = None

try:
    import uawos_requirement_studio
except ImportError:
    uawos_requirement_studio = None

try:
    import uawos_objective
except ImportError:
    uawos_objective = None

try:
    import uawos_outcome
except ImportError:
    uawos_outcome = None

try:
    import uawos_planning
except ImportError:
    uawos_planning = None

try:
    import uawos_workflow
except ImportError:
    uawos_workflow = None

try:
    import uawos_action
except ImportError:
    uawos_action = None

try:
    import uawos_workforce
except ImportError:
    uawos_workforce = None

try:
    import uawos_agent_workforce
except ImportError:
    uawos_agent_workforce = None

try:
    import uawos_governance
except ImportError:
    uawos_governance = None

try:
    import uawos_knowledge
except ImportError:
    uawos_knowledge = None

try:
    import uawos_memory
except ImportError:
    uawos_memory = None

try:
    import uawos_learning
except ImportError:
    uawos_learning = None

try:
    import uawos_resource
except ImportError:
    uawos_resource = None

try:
    import uawos_decision
except ImportError:
    uawos_decision = None

try:
    import uawos_simulation
except ImportError:
    uawos_simulation = None

try:
    import uawos_value
except ImportError:
    uawos_value = None

try:
    import uawos_observability
except ImportError:
    uawos_observability = None

try:
    import uawos_integrations
except ImportError:
    uawos_integrations = None

try:
    import uawos_pmcms
except ImportError:
    uawos_pmcms = None

PORT = 8099
STATUS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_status.json")

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5435))
QDRANT_HOST = os.environ.get("QDRANT_HOST", "127.0.0.1")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))
MARQUEZ_HOST = os.environ.get("MARQUEZ_HOST", "127.0.0.1")
MARQUEZ_PORT = int(os.environ.get("MARQUEZ_PORT", 5000))
SUPERSET_HOST = os.environ.get("SUPERSET_HOST", "127.0.0.1")
SUPERSET_PORT = int(os.environ.get("SUPERSET_PORT", 8088))
DTRACK_HOST = os.environ.get("DTRACK_HOST", "127.0.0.1")
DTRACK_PORT = int(os.environ.get("DTRACK_PORT", 8081))
DTRACK_UI_HOST = os.environ.get("DTRACK_UI_HOST", "127.0.0.1")
DTRACK_UI_PORT = int(os.environ.get("DTRACK_UI_PORT", 8085))

OPA_HOST = os.environ.get("OPA_HOST", "127.0.0.1")
OPA_PORT = int(os.environ.get("OPA_PORT", 8181))
OPENFGA_HOST = os.environ.get("OPENFGA_HOST", "127.0.0.1")
OPENFGA_PORT = int(os.environ.get("OPENFGA_PORT", 8083))
OPENMETADATA_HOST = os.environ.get("OPENMETADATA_HOST", "127.0.0.1")
OPENMETADATA_PORT = int(os.environ.get("OPENMETADATA_PORT", 8585))

CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "127.0.0.1")
CLICKHOUSE_PORT = int(os.environ.get("CLICKHOUSE_PORT", 8123))
TELEMETRY_HOST = os.environ.get("TELEMETRY_HOST", "127.0.0.1")
TELEMETRY_PORT = int(os.environ.get("TELEMETRY_PORT", 3000))
ALARM_HOST = os.environ.get("ALARM_HOST", "127.0.0.1")
ALARM_PORT = int(os.environ.get("ALARM_PORT", 9093))
SANDBOX_HOST = os.environ.get("SANDBOX_HOST", "127.0.0.1")
SANDBOX_PORT = int(os.environ.get("SANDBOX_PORT", 5001))

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "127.0.0.1")
OLLAMA_PORT = int(os.environ.get("OLLAMA_PORT", 11434))
NEO4J_HOST = os.environ.get("NEO4J_HOST", "127.0.0.1")
NEO4J_PORT_1 = int(os.environ.get("NEO4J_PORT_1", 7687))
NEO4J_PORT_2 = int(os.environ.get("NEO4J_PORT_2", 7474))
HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_dashboard.html")
DELIVERY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_delivery.html")
ROADMAP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_roadmap.html")
REQUIREMENT_STUDIO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_requirement_studio.html")
ARCHITECTURE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_architecture.html")

# Global status cache
status_cache = {}

SECURE_TOKEN = os.environ.get("UAWOS_SECURE_TOKEN", "uawos-secure-token-change-me")
_DEFAULT_TOKENS = {"uawos-secure-token-2026", "uawos-secure-token-change-me"}
if SECURE_TOKEN in _DEFAULT_TOKENS:
    print(
        "WARNING: Using default development SECURE_TOKEN. "
        "Set UAWOS_SECURE_TOKEN environment variable for production deployments.",
        file=sys.stderr,
    )


def decode_token_payload(token: str) -> dict:
    """Safely decode JWT claims without verifying signature for development context."""
    import base64
    import json

    try:
        parts = token.split(".")
        if len(parts) == 3:
            payload_b64 = parts[1]
            payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
            payload_json = base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8")
            return json.loads(payload_json)
    except Exception:
        pass
    return {}


def verify_secure_token(x_uawos_token: str = None, authorization: str = None):
    token = x_uawos_token
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing authentication credentials.")

    if token != SECURE_TOKEN:
        claims = decode_token_payload(token)
        if not claims:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid security token.")


# Constants for duplicate literals
QDRANT_VECTOR_DB = "Qdrant Vector DB"
MARQUEZ_LINEAGE = "Marquez Lineage"
APACHE_SUPERSET = "Apache Superset"
DEP_TRACK_API = "Dependency-Track API"
APPLICATION_JSON = "application/json"
TEXT_HTML_UTF8 = "text/html; charset=utf-8"


def check_port(host, port):
    """Check if a TCP port is open."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            s.connect((host, port))
            return True
    except OSError:
        return False


def get_docker_status():
    """Check if Docker daemon is running and retrieve running containers."""
    is_docker_running = False
    containers = {}
    try:
        # Check if Docker is running
        res = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=2.0)
        if res.returncode == 0:
            is_docker_running = True
            # Get running containers and their status
            res_ps = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}|{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=2.0,
            )
            if res_ps.returncode == 0:
                lines = res_ps.stdout.strip().split("\n")
                for line in lines:
                    if "|" in line:
                        name, status = line.split("|", 1)
                        containers[name] = status
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return is_docker_running, containers


def check_semgrep_availability():
    """Check if Semgrep is installed in the local environment."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        semgrep_path = os.path.join(base_dir, ".venv", "Scripts", "semgrep.bat")
        if os.path.exists(semgrep_path):
            res = subprocess.run(
                [semgrep_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10.0,
            )
        else:
            res = subprocess.run(["semgrep", "--version"], capture_output=True, text=True, timeout=10.0)
        return res.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def evaluate_infra(is_docker_running, running_containers, local_dev_healthy, ollama_running):
    infra_components = {
        "Postgres DB": {
            "container": "uawos-postgres",
            "host": POSTGRES_HOST,
            "port": POSTGRES_PORT,
        },
        QDRANT_VECTOR_DB: {
            "container": "uawos-qdrant",
            "host": QDRANT_HOST,
            "port": QDRANT_PORT,
        },
        MARQUEZ_LINEAGE: {
            "container": "uawos-marquez",
            "host": MARQUEZ_HOST,
            "port": MARQUEZ_PORT,
        },
        APACHE_SUPERSET: {
            "container": "uawos-superset",
            "host": SUPERSET_HOST,
            "port": SUPERSET_PORT,
        },
        DEP_TRACK_API: {
            "container": "uawos-dependency-track-api",
            "host": DTRACK_HOST,
            "port": DTRACK_PORT,
        },
        "Dependency-Track UI": {
            "container": "uawos-dependency-track-ui",
            "host": DTRACK_UI_HOST,
            "port": DTRACK_UI_PORT,
        },
    }

    infra_status = {}
    infra_status["Local Dev Environment"] = "GREEN" if local_dev_healthy else "YELLOW"
    infra_status["Outbound Model Gateway"] = "GREEN" if (is_docker_running and ollama_running) else "YELLOW"

    for name, cfg in infra_components.items():
        c_name = cfg["container"]
        c_host = cfg["host"]
        c_port = cfg["port"]

        c_running = c_name in running_containers
        port_open = check_port(c_host, c_port)

        if c_running and port_open:
            infra_status[name] = "GREEN"
        elif c_running or port_open:
            infra_status[name] = "YELLOW"
        else:
            infra_status[name] = "GRAY" if not is_docker_running else "RED"

    return infra_status


def evaluate_integrations(infra_status, venv_ok, is_semgrep_available, running_containers):
    marker_running = "uawos-marker-service" in running_containers or "marker-service" in running_containers

    mesa_ok = False
    try:
        import mesa

        mesa_ok = True
    except ImportError:
        pass

    return {
        "INT-A-01: Qdrant Vector Integration": (
            "GREEN" if (infra_status.get(QDRANT_VECTOR_DB) == "GREEN") else "YELLOW"
        ),
        "INT-A-02: Pydantic AI Core Integration": "GREEN" if venv_ok else "GRAY",
        "INT-A-03: Graphiti Temporal Memory": "GREEN" if venv_ok else "GRAY",
        "INT-A-04: LlamaIndex & Haystack Pipeline": "GREEN" if venv_ok else "GRAY",
        "INT-A-05: Apache Superset BI": ("GREEN" if (infra_status.get(APACHE_SUPERSET) == "GREEN") else "YELLOW"),
        "INT-A-06: Security Scanning Suite": (
            "GREEN" if (infra_status.get(DEP_TRACK_API) == "GREEN" and is_semgrep_available) else "YELLOW"
        ),
        "INT-B-01: GitLab/Bitbucket MCP": "GRAY",
        "INT-B-02: Figma & Style Dictionary Sync": "GRAY",
        "INT-B-03: Slack & Teams MCP": "GRAY",
        "INT-B-04: AWS/Azure cloud discovery": "GRAY",
        "INT-C-01: OpenMetadata Integration": "GRAY",
        "INT-C-02: Airbyte / Meltano Pipeline Setup": "GRAY",
        "INT-C-03: Mesa Simulation Models": "GREEN" if mesa_ok else "RED",
        "INT-C-04: GPLv3 Marker Wrapper": "GREEN" if marker_running else "RED",
    }


def evaluate_security(is_semgrep_available, is_docker_running, infra_status):
    sandboxing_healthy = "GREEN" if check_port(SANDBOX_HOST, SANDBOX_PORT) else "GRAY"
    return {
        "Semgrep SAST": "YELLOW" if not is_semgrep_available else "GREEN",
        "Trivy Container Scanner": "GREEN" if is_docker_running else "YELLOW",
        "Gitleaks Secret Detection": (
            "GREEN" if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".git")) else "YELLOW"
        ),
        "Dependency-Track SBOM Auditor": ("GREEN" if (infra_status.get(DEP_TRACK_API) == "GREEN") else "RED"),
        "Falco Sandbox / OpenHands Sandboxing": sandboxing_healthy,
    }


def evaluate_governance(infra_status):
    sbom_auditor_green = infra_status.get(DEP_TRACK_API) == "GREEN"
    opa_healthy = "GREEN" if check_port(OPA_HOST, OPA_PORT) else "YELLOW"
    openfga_healthy = "GREEN" if check_port(OPENFGA_HOST, OPENFGA_PORT) else "YELLOW"
    openmetadata_healthy = "GREEN" if check_port(OPENMETADATA_HOST, OPENMETADATA_PORT) else "GRAY"
    return {
        "License Governance Filters": "GREEN" if sbom_auditor_green else "YELLOW",
        "OpenLineage Execution Ingestion": ("GREEN" if (infra_status.get(MARQUEZ_LINEAGE) == "GREEN") else "YELLOW"),
        "Marquez Metadata & Lineage": ("GREEN" if (infra_status.get(MARQUEZ_LINEAGE) == "GREEN") else "RED"),
        "OpenMetadata Catalog": openmetadata_healthy,
        "OPA/Rego Policy Engine": opa_healthy,
        "OpenFGA Authorization": openfga_healthy,
    }


def evaluate_data(infra_status):
    return {
        "Vector Storage (Qdrant)": ("GREEN" if (infra_status.get(QDRANT_VECTOR_DB) == "GREEN") else "RED"),
        "Relational Databases (Postgres)": ("GREEN" if (infra_status.get("Postgres DB") == "GREEN") else "RED"),
        "Long-term Log Storage (ClickHouse)": ("GREEN" if check_port(CLICKHOUSE_HOST, CLICKHOUSE_PORT) else "YELLOW"),
    }


def evaluate_operations(infra_status):
    telemetry_healthy = "GREEN" if check_port(TELEMETRY_HOST, TELEMETRY_PORT) else "YELLOW"
    alarm_healthy = "GREEN" if check_port(ALARM_HOST, ALARM_PORT) else "GRAY"
    return {
        "Telemetry Collection": telemetry_healthy,
        "BI Reporting (Apache Superset)": ("GREEN" if (infra_status.get(APACHE_SUPERSET) == "GREEN") else "RED"),
        "Operational Alarm Framework": alarm_healthy,
    }


def _evaluate_dynamic_services(dtase_healthy, budget_healthy, objective_healthy):
    """Evaluate current service statuses dynamically."""
    return {
        "Objective Engine": "GREEN" if uawos_objective is not None else "GRAY",
        "Discovery Engine": "GREEN" if uawos_dtase is not None else "GRAY",
        "Planning Engine": "GREEN" if uawos_planning is not None else "GRAY",
        "Governance Engine": "GREEN" if uawos_governance is not None else "GRAY",
        "Knowledge Engine": "GREEN" if uawos_knowledge is not None else "GRAY",
        "Value Engine": ("GREEN" if (uawos_value is not None or uawos_budget is not None) else "GRAY"),
        "Simulation Engine": "GREEN" if uawos_simulation is not None else "GRAY",
        "DTASE": "GREEN" if uawos_dtase is not None else "GRAY",
        "Maturity Engine": "GREEN" if uawos_pmcms is not None else "GRAY",
    }


def _evaluate_dynamic_agents(budget_healthy, objective_healthy):
    """Evaluate current agent statuses dynamically."""
    return {
        "Planner Agent": ("GREEN" if (uawos_agent_workforce is not None and uawos_planning is not None) else "GRAY"),
        "Orchestrator Agent": (
            "GREEN" if (uawos_agent_workforce is not None and uawos_workflow is not None) else "GRAY"
        ),
        "Executor Agent": ("GREEN" if (uawos_agent_workforce is not None and uawos_action is not None) else "GRAY"),
        "Reviewer Agent": ("GREEN" if (uawos_agent_workforce is not None and uawos_outcome is not None) else "GRAY"),
        "Governor Agent": ("GREEN" if (uawos_agent_workforce is not None and uawos_governance is not None) else "GRAY"),
        "Learner Agent": ("GREEN" if (uawos_agent_workforce is not None and uawos_learning is not None) else "GRAY"),
        "Knowledge Manager Agent": (
            "GREEN" if (uawos_agent_workforce is not None and uawos_knowledge is not None) else "GRAY"
        ),
        "Portfolio Governor Agent": (
            "GREEN" if (uawos_agent_workforce is not None and uawos_budget is not None) else "GRAY"
        ),
        "Value Analyst Agent": ("GREEN" if (uawos_agent_workforce is not None and uawos_value is not None) else "GRAY"),
        "Resource Manager Agent": (
            "GREEN" if (uawos_agent_workforce is not None and uawos_resource is not None) else "GRAY"
        ),
        "Simulation Agent": (
            "GREEN" if (uawos_agent_workforce is not None and uawos_simulation is not None) else "GRAY"
        ),
        "Challenger Agent": ("GREEN" if (uawos_agent_workforce is not None and uawos_decision is not None) else "GRAY"),
    }


def _count_statuses(dicts_to_count):
    """Aggregate green, yellow, red, and gray component status counts."""
    green_count = 0
    yellow_count = 0
    red_count = 0
    gray_count = 0

    for d in dicts_to_count:
        for val in d.values():
            if val == "GREEN":
                green_count += 1
            elif val == "YELLOW":
                yellow_count += 1
            elif val == "RED":
                red_count += 1
            else:
                gray_count += 1
    return green_count, yellow_count, red_count, gray_count


def run_health_checks():
    """Run all system checks and build the status dictionary."""
    is_docker_running, running_containers = get_docker_status()
    is_semgrep_available = check_semgrep_availability()

    local_dev_healthy = os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv"))
    ollama_running = check_port(OLLAMA_HOST, OLLAMA_PORT)

    infra_status = evaluate_infra(is_docker_running, running_containers, local_dev_healthy, ollama_running)
    integrations = evaluate_integrations(infra_status, local_dev_healthy, is_semgrep_available, running_containers)
    security_status = evaluate_security(is_semgrep_available, is_docker_running, infra_status)
    governance_status = evaluate_governance(infra_status)
    data_status = evaluate_data(infra_status)
    operations_status = evaluate_operations(infra_status)

    services_status = _evaluate_dynamic_services(
        uawos_dtase is not None, uawos_budget is not None, uawos_objective is not None
    )
    agents_status = _evaluate_dynamic_agents(uawos_budget is not None, uawos_objective is not None)

    # Dynamic skill health checks
    dspy_ok = False
    try:
        import dspy

        dspy_ok = True
    except ImportError:
        pass

    instructor_ok = False
    try:
        import instructor

        instructor_ok = True
    except ImportError:
        pass

    fastembed_ok = False
    try:
        import fastembed

        fastembed_ok = True
    except ImportError:
        pass

    dbt_ok = False
    try:
        import dbt

        dbt_ok = True
    except ImportError:
        pass

    mesa_ok = False
    try:
        import mesa

        mesa_ok = True
    except ImportError:
        pass

    networkx_ok = False
    try:
        import networkx

        networkx_ok = True
    except ImportError:
        pass

    openlineage_ok = False
    try:
        import openlineage

        openlineage_ok = True
    except ImportError:
        pass

    marquez_ok = False
    try:
        import marquez_client

        marquez_ok = True
    except ImportError:
        pass

    import shutil

    java_ok = shutil.which("java") is not None
    npm_ok = shutil.which("npm") is not None

    neo4j_running = check_port(NEO4J_HOST, NEO4J_PORT_1) or check_port(NEO4J_HOST, NEO4J_PORT_2)
    clickhouse_running = check_port(CLICKHOUSE_HOST, CLICKHOUSE_PORT)

    # SKL-AI-01: Prompt Tuning
    if dspy_ok and ollama_running:
        skl_ai_01 = "GREEN"
    elif dspy_ok or ollama_running:
        skl_ai_01 = "YELLOW"
    else:
        skl_ai_01 = "RED"

    # SKL-AI-02: Structural Parsing
    skl_ai_02 = "GREEN" if instructor_ok else "RED"

    # SKL-RAG-01: Dense Retrieval
    qdrant_green = infra_status.get(QDRANT_VECTOR_DB) == "GREEN"
    if fastembed_ok and qdrant_green:
        skl_rag_01 = "GREEN"
    elif fastembed_ok or qdrant_green:
        skl_rag_01 = "YELLOW"
    else:
        skl_rag_01 = "RED"

    # SKL-RAG-02: Graph Traversal
    skl_rag_02 = "GREEN" if neo4j_running else "YELLOW"

    # SKL-DOC-01: C4 Architecture
    if java_ok and npm_ok:
        skl_doc_01 = "GREEN"
    elif java_ok or npm_ok:
        skl_doc_01 = "YELLOW"
    else:
        skl_doc_01 = "RED"

    # SKL-SEC-01: Vulnerability Audit
    dtrack_green = infra_status.get(DEP_TRACK_API) == "GREEN"
    if is_docker_running and dtrack_green:
        skl_sec_01 = "GREEN"
    elif is_docker_running or dtrack_green:
        skl_sec_01 = "YELLOW"
    else:
        skl_sec_01 = "RED"

    # SKL-DAT-01: Analytical Transform
    if dbt_ok and clickhouse_running:
        skl_dat_01 = "GREEN"
    elif dbt_ok or clickhouse_running:
        skl_dat_01 = "YELLOW"
    else:
        skl_dat_01 = "RED"

    # SKL-SIM-01: Monte Carlo Run
    skl_sim_01 = "GREEN" if (mesa_ok and networkx_ok) else "RED"

    # SKL-GOV-01: Lineage Audit
    marquez_green = infra_status.get(MARQUEZ_LINEAGE) == "GREEN"
    if openlineage_ok and marquez_ok and marquez_green:
        skl_gov_01 = "GREEN"
    elif openlineage_ok or marquez_ok or marquez_green:
        skl_gov_01 = "YELLOW"
    else:
        skl_gov_01 = "RED"

    skills_status = {
        "SKL-AI-01: Prompt Tuning": skl_ai_01,
        "SKL-AI-02: Structural Parsing": skl_ai_02,
        "SKL-RAG-01: Dense Retrieval": skl_rag_01,
        "SKL-RAG-02: Graph Traversal": skl_rag_02,
        "SKL-DOC-01: C4 Architecture": skl_doc_01,
        "SKL-SEC-01: Vulnerability Audit": skl_sec_01,
        "SKL-DAT-01: Analytical Transform": skl_dat_01,
        "SKL-SIM-01: Monte Carlo Run": skl_sim_01,
        "SKL-GOV-01: Lineage Audit": skl_gov_01,
    }

    mcps_status = dict.fromkeys(
        [
            "GitLab MCP",
            "Bitbucket MCP",
            "SonarQube MCP",
            "Jenkins MCP",
            "Confluence MCP",
            "Notion MCP",
            "Docusaurus MCP",
            "Mermaid MCP",
            "PlantUML MCP",
            "AWS MCP",
            "Azure MCP",
            "Terraform MCP",
            "Redis MCP",
            "Kafka MCP",
            "ClickHouse MCP",
            "OpenSearch MCP",
            "Neo4j MCP",
            "Slack MCP",
            "Teams MCP",
            "Discord MCP",
        ],
        "GRAY",
    )

    # Evaluate Custom Engine APIs
    engines = [
        uawos_objective,
        uawos_dtase,
        uawos_planning,
        uawos_governance,
        uawos_knowledge,
        uawos_value,
        uawos_budget,
        uawos_simulation,
    ]
    not_none_count = sum(1 for e in engines if e is not None)
    if not_none_count == len(engines):
        custom_apis_status = "GREEN"
    elif not_none_count > 0:
        custom_apis_status = "YELLOW"
    else:
        custom_apis_status = "RED"

    apis_status = {
        "Outbound APIs (LiteLLM/Weave)": "GREEN" if ollama_running else "YELLOW",
        "Custom Engine APIs": custom_apis_status,
    }

    # Sum up all statuses
    dicts_to_count = [
        infra_status,
        integrations,
        security_status,
        governance_status,
        data_status,
        operations_status,
        services_status,
        agents_status,
        skills_status,
        mcps_status,
        apis_status,
    ]

    green_count, yellow_count, red_count, gray_count = _count_statuses(dicts_to_count)

    total_components = green_count + yellow_count + red_count + gray_count
    strict_health = round((green_count / total_components) * 100, 1) if total_components > 0 else 0.0
    weighted_health = (
        round(((green_count + 0.5 * yellow_count) / total_components) * 100, 1) if total_components > 0 else 0.0
    )

    alt_components = {
        "Ollama Local LLM": {"container": "core-ollama", "port": 11434},
        "Langfuse ClickHouse": {"container": "langfuse-clickhouse-1", "port": 8123},
        "Langfuse MinIO": {"container": "langfuse-minio-1", "port": 9090},
        "Langfuse Postgres": {"container": "langfuse-postgres-1", "port": 5432},
        "Core Redis": {"container": "core-redis", "port": 6380},
    }

    status_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "docker_running": is_docker_running,
        "running_containers": running_containers,
        "health_summary": {
            "total": total_components,
            "green": green_count,
            "yellow": yellow_count,
            "red": red_count,
            "gray": gray_count,
            "strict_percentage": strict_health,
            "weighted_percentage": weighted_health,
        },
        "domains": {
            "Services": services_status,
            "Agents": agents_status,
            "MCPs": mcps_status,
            "Skills": skills_status,
            "APIs": apis_status,
            "Integrations": integrations,
            "Data": data_status,
            "Infrastructure": infra_status,
            "Security": security_status,
            "Governance": governance_status,
            "Operations": operations_status,
        },
        "alternate_daemons": {
            name: (
                "GREEN"
                if (name == "Ollama Local LLM" and ollama_running) or (cfg["container"] in running_containers)
                else "GRAY"
            )
            for name, cfg in alt_components.items()
        },
    }

    return status_data


def daemon_loop():
    """Periodic health checks background loop."""
    global status_cache
    while True:
        try:
            status_cache = run_health_checks()
            # Write to status.json
            with open(STATUS_FILE, "w") as f:
                json.dump(status_cache, f, indent=2)
        except Exception as e:
            print(f"Error in daemon checks: {e}", file=sys.stderr)
        time.sleep(5.0)


def get_documents():
    """Scan and categorize all markdown files in the Requirements Master directory."""
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Requirements Master")
    categories = {
        "Architectural Standards": [],
        "Ecosystem Catalogs": [],
        "Product & Requirements (PRD)": [],
        "Delivery & Roadmaps": [],
        "Other Specifications": [],
    }

    if not os.path.exists(docs_dir):
        return categories

    try:
        for f_name in sorted(os.listdir(docs_dir)):
            if f_name.endswith(".md"):
                name_lower = f_name.lower()
                if "catalog" in name_lower:
                    categories["Ecosystem Catalogs"].append(f_name)
                elif "prd" in name_lower or "blueprint" in name_lower or "solutiondesign" in name_lower:
                    categories["Product & Requirements (PRD)"].append(f_name)
                elif "roadmap" in name_lower or "backlog" in name_lower:
                    categories["Delivery & Roadmaps"].append(f_name)
                elif (
                    "standard" in name_lower
                    or "architecture" in name_lower
                    or "ontology" in name_lower
                    or "directive" in name_lower
                    or "adr" in name_lower
                    or "record" in name_lower
                    or "graph" in name_lower
                    or "dtase" in name_lower
                ):
                    categories["Architectural Standards"].append(f_name)
                else:
                    categories["Other Specifications"].append(f_name)
    except Exception as e:
        print(f"Error scanning documents: {e}", file=sys.stderr)

    return categories


# Initialize FastAPI App
app = FastAPI(title="UAWOS Operational Control Plane Daemon", version="1.0.0")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def tenant_context_middleware(request: Request, call_next):
    import uawos_context

    token = request.headers.get("x-uawos-token")
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]

    # Defaults
    tenant_id = "default_tenant"
    role = "Developer"
    owner = "system"

    # Decode if present
    if token:
        if token == SECURE_TOKEN:
            tenant_id = "default_tenant"
            role = "Admin"
            owner = "admin_user"
        else:
            claims = decode_token_payload(token)
            if claims:
                tenant_id = claims.get("tenant_id", "default_tenant")
                role = claims.get("role", "Developer")
                owner = claims.get("owner") or claims.get("username") or claims.get("sub", "system")

    tokens = uawos_context.set_context(tenant_id, role, owner)
    try:
        response = await call_next(request)
        return response
    finally:
        uawos_context.reset_context(tokens)


# Static Dashboard View Routers
@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def serve_dashboard():
    try:
        with open(HTML_FILE, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard UI file not found.")


@app.get("/delivery", response_class=HTMLResponse)
@app.get("/delivery.html", response_class=HTMLResponse)
def serve_delivery():
    try:
        with open(DELIVERY_FILE, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Delivery UI file not found.")


@app.get("/roadmap", response_class=HTMLResponse)
@app.get("/roadmap.html", response_class=HTMLResponse)
def serve_roadmap():
    try:
        with open(ROADMAP_FILE, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Roadmap UI file not found.")


@app.get("/requirement_studio", response_class=HTMLResponse)
@app.get("/requirement_studio.html", response_class=HTMLResponse)
def serve_requirement_studio():
    try:
        with open(REQUIREMENT_STUDIO_FILE, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Requirement Studio UI file not found.")


@app.get("/architecture", response_class=HTMLResponse)
@app.get("/architecture.html", response_class=HTMLResponse)
def serve_architecture():
    try:
        with open(ARCHITECTURE_FILE, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Architecture UI file not found.")


# REST API Endpoint Routers
@app.get("/api/requirement/list")
def get_requirement_list():
    if uawos_requirement_studio is None:
        raise HTTPException(status_code=500, detail="Requirement Studio module unavailable.")
    try:
        return uawos_requirement_studio.load_state()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/objective/list")
def get_objective_list():
    if uawos_objective is None:
        raise HTTPException(status_code=500, detail="Objective module unavailable.")
    try:
        return uawos_objective.load_state()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/objective/conflicts")
def get_objective_conflicts():
    if uawos_objective is None:
        raise HTTPException(status_code=500, detail="Objective module unavailable.")
    try:
        return {"conflicts": uawos_objective.detect_conflicts()}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/status")
def get_status():
    global status_cache
    return status_cache


@app.get("/api/pmcms")
def get_pmcms():
    if uawos_pmcms is None:
        raise HTTPException(status_code=500, detail="PMCMS Maturity module unavailable.")
    global status_cache
    try:
        return uawos_pmcms.get_maturity_assessment(status_cache)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/traceability")
def get_traceability():
    global status_cache
    try:
        matrix = uawos_traceability.get_traceability_matrix(status_cache)
        health = uawos_traceability.get_delivery_health(matrix)
        return {"matrix": matrix, "health": health}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/roadmap")
def get_roadmap():
    global status_cache
    try:
        matrix = uawos_traceability.get_traceability_matrix(status_cache)
        return uawos_traceability.get_roadmap_data(matrix)
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/changes")
def get_changes():
    try:
        return uawos_traceability.get_change_detection()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/generate_prompt")
def get_generate_prompt(roadmap_id: str = None):
    global status_cache
    try:
        matrix = uawos_traceability.get_traceability_matrix(status_cache)
        prompt = uawos_traceability.generate_antigravity_prompt(matrix, roadmap_id)
        return {"prompt": prompt}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/docs")
def get_docs():
    return get_documents()


@app.get("/api/docs/content", response_class=PlainTextResponse)
def get_docs_content(file: str = ""):
    file_name = os.path.basename(file)
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Requirements Master")
    file_path = os.path.join(docs_dir, file_name)
    if file_name and os.path.exists(file_path) and file_name.endswith(".md"):
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading file: {e}")
    raise HTTPException(status_code=404, detail="Document not found or access denied.")


@app.get("/api/budget/status")
def get_budget_status():
    if uawos_budget is None:
        raise HTTPException(status_code=500, detail="Budget module unavailable.")
    try:
        return uawos_budget.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/dtase/analyze")
async def analyze_dtase(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    if uawos_dtase is None:
        raise HTTPException(status_code=500, detail="DTASE module unavailable.")
    try:
        payload = await request.json()
        text = payload.get("text", "")
        return uawos_dtase.analyze_unstructured_input(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/budget/action")
async def budget_action(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    if uawos_budget is None:
        raise HTTPException(status_code=500, detail="Budget module unavailable.")
    try:
        payload = await request.json()
        action = payload.get("action", "")
        result = {"status": "success"}

        if action == "record_tokens":
            agent = payload.get("agent", "Executor Agent")
            model = payload.get("model", "tinyllama")
            tokens_in = int(payload.get("tokens_in", 10000))
            tokens_out = int(payload.get("tokens_out", 5000))
            tokens_reasoning = int(payload.get("tokens_reasoning", 0))
            uawos_budget.record_agent_cost(agent, model, tokens_in, tokens_out, tokens_reasoning)
            result["message"] = f"Recorded token usage for {agent}."
        elif action == "adjust_budget":
            obj_id = payload.get("objective_id", "")
            name = payload.get("name", "")
            amount = float(payload.get("amount", 0.0))
            uawos_budget.allocate_objective_budget(obj_id, name, amount)
            result["message"] = f"Adjusted budget for {obj_id} to ${amount:.2f}."
        elif action == "approve_request":
            app_id = payload.get("approval_id", "")
            decision = payload.get("decision", "Approved")
            uawos_budget.process_approval_request(app_id, decision)
            result["message"] = f"Processed approval {app_id} as {decision}."
        elif action == "check_governance":
            obj_id = payload.get("objective_id", "")
            gov = uawos_budget.evaluate_cost_governance(obj_id)
            result["gov"] = gov
            result["message"] = f"Evaluated governance for {obj_id}."
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/requirement/submit")
async def requirement_submit(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    if uawos_requirement_studio is None:
        raise HTTPException(status_code=500, detail="Requirement Studio module unavailable.")
    try:
        payload = await request.json()
        title = payload.get("title", "New Requirement")
        text = payload.get("text", "")
        return uawos_requirement_studio.submit_new_requirement(title, text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/requirement/clarify")
async def requirement_clarify(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    if uawos_requirement_studio is None:
        raise HTTPException(status_code=500, detail="Requirement Studio module unavailable.")
    try:
        payload = await request.json()
        req_id = payload.get("requirement_id", "")
        answers = payload.get("answers", {})
        waive = payload.get("waive", False)
        return uawos_requirement_studio.update_clarifications(req_id, answers, waive)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/requirement/author")
async def requirement_author(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    if uawos_requirement_studio is None:
        raise HTTPException(status_code=500, detail="Requirement Studio module unavailable.")
    try:
        payload = await request.json()
        req_id = payload.get("requirement_id", "")
        return uawos_requirement_studio.author_proposition(req_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/requirement/absorb")
async def requirement_absorb(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    if uawos_requirement_studio is None:
        raise HTTPException(status_code=500, detail="Requirement Studio module unavailable.")
    try:
        payload = await request.json()
        req_id = payload.get("requirement_id", "")
        return uawos_requirement_studio.absorb_requirement(req_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/requirement/publish")
async def requirement_publish(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    if uawos_requirement_studio is None:
        raise HTTPException(status_code=500, detail="Requirement Studio module unavailable.")
    try:
        payload = await request.json()
        cand_id = payload.get("roadmap_id", "")
        return uawos_requirement_studio.publish_roadmap_item(cand_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/requirement/direct_ingest")
async def requirement_direct_ingest(
    request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)
):
    verify_secure_token(x_uawos_token, authorization)
    if uawos_requirement_studio is None:
        raise HTTPException(status_code=500, detail="Requirement Studio module unavailable.")
    try:
        payload = await request.json()
        req_id = payload.get("requirement_id", "")
        answers = payload.get("answers", {})
        waive = payload.get("waive", False)
        return uawos_requirement_studio.direct_ingest_to_backlog(req_id, answers, waive)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/requirement/reset")
def requirement_reset(x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    if uawos_requirement_studio is None:
        raise HTTPException(status_code=500, detail="Requirement Studio module unavailable.")
    try:
        state = uawos_requirement_studio.get_default_state()
        uawos_requirement_studio.save_state(state)
        if os.path.exists(uawos_requirement_studio.STATE_FILE):
            os.remove(uawos_requirement_studio.STATE_FILE)
        return {"status": "SUCCESS"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/objective/submit")
async def objective_submit(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    if uawos_objective is None:
        raise HTTPException(status_code=500, detail="Objective module unavailable.")
    try:
        payload = await request.json()
        text = payload.get("text", "")
        input_type = payload.get("input_type", "text")
        owner = payload.get("owner", "")
        sponsor = payload.get("sponsor", "")
        source_uri = payload.get("source_uri", "")
        return uawos_objective.create_objective_from_input(text, input_type, owner, sponsor, source_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/objective/action")
async def objective_action(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    if uawos_objective is None:
        raise HTTPException(status_code=500, detail="Objective module unavailable.")
    try:
        payload = await request.json()
        action = payload.get("action", "")
        obj_id = payload.get("objective_id", "")
        result = {"status": "success"}

        if action == "pause":
            result["data"] = uawos_objective.pause_objective(obj_id)
        elif action == "cancel":
            result["data"] = uawos_objective.cancel_objective(obj_id)
        elif action == "archive":
            result["data"] = uawos_objective.archive_objective(obj_id)
        elif action == "restore":
            result["data"] = uawos_objective.restore_objective(obj_id)
        elif action == "resume":
            result["data"] = uawos_objective.resume_objective(obj_id)
        elif action == "update":
            updates = payload.get("updates", {})
            result["data"] = uawos_objective.update_objective(obj_id, updates)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def start_server():
    print(f"Starting server on http://0.0.0.0:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
    return 0


if __name__ == "__main__":
    print("Initializing UAWOS health monitors...")
    status_cache = run_health_checks()
    with open(STATUS_FILE, "w") as f:
        json.dump(status_cache, f, indent=2)

    # Start the daemon monitoring thread
    t = threading.Thread(target=daemon_loop, daemon=True)
    t.start()

    # Start the web server
    start_server()
