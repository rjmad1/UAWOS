#!/usr/bin/env python3
import os
import sys
import json
import time
import socket
import threading
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
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

PORT = 8099
STATUS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_status.json")
HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_dashboard.html")
DELIVERY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_delivery.html")
ROADMAP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_roadmap.html")
REQUIREMENT_STUDIO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_requirement_studio.html")

# Global status cache
status_cache = {}

# Constants for duplicate literals
QDRANT_VECTOR_DB = "Qdrant Vector DB"
MARQUEZ_LINEAGE = "Marquez Lineage"
APACHE_SUPERSET = "Apache Superset"
DEP_TRACK_API = "Dependency-Track API"
APPLICATION_JSON = "application/json"
TEXT_HTML_UTF8 = "text/html; charset=utf-8"

STATIC_ROUTES = {
    "/": (HTML_FILE, "text/html"),
    "/index.html": (HTML_FILE, "text/html"),
    "/delivery": (DELIVERY_FILE, TEXT_HTML_UTF8),
    "/delivery.html": (DELIVERY_FILE, TEXT_HTML_UTF8),
    "/roadmap": (ROADMAP_FILE, TEXT_HTML_UTF8),
    "/roadmap.html": (ROADMAP_FILE, TEXT_HTML_UTF8),
    "/requirement_studio": (REQUIREMENT_STUDIO_FILE, TEXT_HTML_UTF8),
    "/requirement_studio.html": (REQUIREMENT_STUDIO_FILE, TEXT_HTML_UTF8),
}

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
            res_ps = subprocess.run(["docker", "ps", "--format", "{{.Names}}|{{.Status}}"], capture_output=True, text=True, timeout=2.0)
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
            res = subprocess.run([semgrep_path, "--version"], capture_output=True, text=True, timeout=10.0)
        else:
            res = subprocess.run(["semgrep", "--version"], capture_output=True, text=True, timeout=10.0)
        return res.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def evaluate_infra(is_docker_running, running_containers, local_dev_healthy, ollama_running):
    infra_components = {
        "Postgres DB": {"container": "uawos-postgres", "port": 5435},
        QDRANT_VECTOR_DB: {"container": "uawos-qdrant", "port": 6333},
        MARQUEZ_LINEAGE: {"container": "uawos-marquez", "port": 5000},
        APACHE_SUPERSET: {"container": "uawos-superset", "port": 8088},
        DEP_TRACK_API: {"container": "uawos-dependency-track-api", "port": 8081},
        "Dependency-Track UI": {"container": "uawos-dependency-track-ui", "port": 8085},
    }
    
    infra_status = {}
    infra_status["Local Dev Environment"] = "GREEN" if local_dev_healthy else "YELLOW"
    infra_status["Outbound Model Gateway"] = "GREEN" if (is_docker_running and ollama_running) else "YELLOW"
    
    for name, cfg in infra_components.items():
        c_name = cfg["container"]
        c_port = cfg["port"]
        
        c_running = c_name in running_containers
        port_open = check_port("127.0.0.1", c_port)

        if c_running and port_open:
            infra_status[name] = "GREEN"
        elif c_running or port_open:
            infra_status[name] = "YELLOW"
        else:
            infra_status[name] = "GRAY" if not is_docker_running else "RED"
            
    return infra_status

def evaluate_integrations(infra_status, venv_ok, is_semgrep_available, running_containers):
    marker_running = "uawos-marker-service" in running_containers or "marker-service" in running_containers
    return {
        "INT-A-01: Qdrant Vector Integration": "GREEN" if (infra_status.get(QDRANT_VECTOR_DB) == "GREEN") else "YELLOW",
        "INT-A-02: Pydantic AI Core Integration": "GREEN" if venv_ok else "GRAY",
        "INT-A-03: Graphiti Temporal Memory": "GREEN" if venv_ok else "GRAY",
        "INT-A-04: LlamaIndex & Haystack Pipeline": "GREEN" if venv_ok else "GRAY",
        "INT-A-05: Apache Superset BI": "GREEN" if (infra_status.get(APACHE_SUPERSET) == "GREEN") else "YELLOW",
        "INT-A-06: Security Scanning Suite": "GREEN" if (infra_status.get(DEP_TRACK_API) == "GREEN" and is_semgrep_available) else "YELLOW",
        "INT-B-01: GitLab/Bitbucket MCP": "GRAY",
        "INT-B-02: Figma & Style Dictionary Sync": "GRAY",
        "INT-B-03: Slack & Teams MCP": "GRAY",
        "INT-B-04: AWS/Azure cloud discovery": "GRAY",
        "INT-C-01: OpenMetadata Integration": "GRAY",
        "INT-C-02: Airbyte / Meltano Pipeline Setup": "GRAY",
        "INT-C-03: Mesa Simulation Models": "GRAY",
        "INT-C-04: GPLv3 Marker Wrapper": "GREEN" if marker_running else "RED",
    }

def evaluate_security(is_semgrep_available, is_docker_running, infra_status):
    sandboxing_healthy = "GREEN" if check_port("127.0.0.1", 5001) else "GRAY"
    return {
        "Semgrep SAST": "YELLOW" if not is_semgrep_available else "GREEN",
        "Trivy Container Scanner": "GREEN" if is_docker_running else "YELLOW",
        "Gitleaks Secret Detection": "GREEN" if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".git")) else "YELLOW",
        "Dependency-Track SBOM Auditor": "GREEN" if (infra_status.get(DEP_TRACK_API) == "GREEN") else "RED",
        "Falco Sandbox / OpenHands Sandboxing": sandboxing_healthy,
    }

def evaluate_governance(infra_status):
    sbom_auditor_green = (infra_status.get(DEP_TRACK_API) == "GREEN")
    opa_healthy = "GREEN" if check_port("127.0.0.1", 8181) else "YELLOW"
    openfga_healthy = "GREEN" if check_port("127.0.0.1", 8083) else "YELLOW"
    openmetadata_healthy = "GREEN" if check_port("127.0.0.1", 8585) else "GRAY"
    return {
        "License Governance Filters": "GREEN" if sbom_auditor_green else "YELLOW",
        "OpenLineage Execution Ingestion": "GREEN" if (infra_status.get(MARQUEZ_LINEAGE) == "GREEN") else "YELLOW",
        "Marquez Metadata & Lineage": "GREEN" if (infra_status.get(MARQUEZ_LINEAGE) == "GREEN") else "RED",
        "OpenMetadata Catalog": openmetadata_healthy,
        "OPA/Rego Policy Engine": opa_healthy,
        "OpenFGA Authorization": openfga_healthy,
    }

def evaluate_data(infra_status):
    return {
        "Vector Storage (Qdrant)": "GREEN" if (infra_status.get(QDRANT_VECTOR_DB) == "GREEN") else "RED",
        "Relational Databases (Postgres)": "GREEN" if (infra_status.get("Postgres DB") == "GREEN") else "RED",
        "Long-term Log Storage (ClickHouse)": "GREEN" if check_port("127.0.0.1", 8123) else "YELLOW",
    }

def evaluate_operations(infra_status):
    telemetry_healthy = "GREEN" if check_port("127.0.0.1", 3000) else "YELLOW"
    alarm_healthy = "GREEN" if check_port("127.0.0.1", 9093) else "GRAY"
    return {
        "Telemetry Collection": telemetry_healthy,
        "BI Reporting (Apache Superset)": "GREEN" if (infra_status.get(APACHE_SUPERSET) == "GREEN") else "RED",
        "Operational Alarm Framework": alarm_healthy,
    }

def _evaluate_dynamic_services(dtase_healthy, budget_healthy):
    """Evaluate current service statuses dynamically."""
    services_status = dict.fromkeys(["Objective Engine", "Discovery Engine", "Planning Engine", "Governance Engine", "Knowledge Engine", "Value Engine", "Simulation Engine"], "GRAY")
    services_status["DTASE"] = "GREEN" if dtase_healthy else "GRAY"
    if budget_healthy:
        services_status["Value Engine"] = "GREEN"
    return services_status

def _evaluate_dynamic_agents(budget_healthy):
    """Evaluate current agent statuses dynamically."""
    agents_status = dict.fromkeys(["Planner Agent", "Orchestrator Agent", "Executor Agent", "Reviewer Agent", "Governor Agent", "Learner Agent", "Knowledge Manager Agent", "Portfolio Governor Agent", "Value Analyst Agent", "Resource Manager Agent", "Simulation Agent", "Challenger Agent"], "GRAY")
    if budget_healthy:
        agents_status["Portfolio Governor Agent"] = "GREEN"
        agents_status["Value Analyst Agent"] = "GREEN"
        agents_status["Resource Manager Agent"] = "GREEN"
    return agents_status

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
    ollama_running = check_port("127.0.0.1", 11434)

    infra_status = evaluate_infra(is_docker_running, running_containers, local_dev_healthy, ollama_running)
    integrations = evaluate_integrations(infra_status, local_dev_healthy, is_semgrep_available, running_containers)
    security_status = evaluate_security(is_semgrep_available, is_docker_running, infra_status)
    governance_status = evaluate_governance(infra_status)
    data_status = evaluate_data(infra_status)
    operations_status = evaluate_operations(infra_status)

    services_status = _evaluate_dynamic_services(uawos_dtase is not None, uawos_budget is not None)
    agents_status = _evaluate_dynamic_agents(uawos_budget is not None)
    skills_status = dict.fromkeys(["SKL-AI-01: Prompt Tuning", "SKL-AI-02: Structural Parsing", "SKL-RAG-01: Dense Retrieval", "SKL-RAG-02: Graph Traversal", "SKL-DOC-01: C4 Architecture", "SKL-SEC-01: Vulnerability Audit", "SKL-DAT-01: Analytical Transform", "SKL-SIM-01: Monte Carlo Run", "SKL-GOV-01: Lineage Audit"], "GRAY")
    mcps_status = dict.fromkeys(["GitLab MCP", "Bitbucket MCP", "SonarQube MCP", "Jenkins MCP", "Confluence MCP", "Notion MCP", "Docusaurus MCP", "Mermaid MCP", "PlantUML MCP", "AWS MCP", "Azure MCP", "Terraform MCP", "Redis MCP", "Kafka MCP", "ClickHouse MCP", "OpenSearch MCP", "Neo4j MCP", "Slack MCP", "Teams MCP", "Discord MCP"], "GRAY")

    apis_status = {
        "Outbound APIs (LiteLLM/Weave)": "GREEN" if ollama_running else "YELLOW",
        "Custom Engine APIs": "GRAY",
    }

    # Sum up all statuses
    dicts_to_count = [
        infra_status, integrations, security_status, governance_status,
        data_status, operations_status, services_status, agents_status,
        skills_status, mcps_status, apis_status
    ]

    green_count, yellow_count, red_count, gray_count = _count_statuses(dicts_to_count)

    total_components = green_count + yellow_count + red_count + gray_count
    strict_health = round((green_count / total_components) * 100, 1) if total_components > 0 else 0.0
    weighted_health = round(((green_count + 0.5 * yellow_count) / total_components) * 100, 1) if total_components > 0 else 0.0

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
            "weighted_percentage": weighted_health
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
            "Operations": operations_status
        },
        "alternate_daemons": {
            name: ("GREEN" if (name == "Ollama Local LLM" and ollama_running) or (cfg["container"] in running_containers) else "GRAY")
            for name, cfg in alt_components.items()
        }
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

import urllib.parse

def get_documents():
    """Scan and categorize all markdown files in the Requirements Master directory."""
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Requirements Master")
    categories = {
        "Architectural Standards": [],
        "Ecosystem Catalogs": [],
        "Product & Requirements (PRD)": [],
        "Delivery & Roadmaps": [],
        "Other Specifications": []
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
                elif "standard" in name_lower or "architecture" in name_lower or "ontology" in name_lower or "directive" in name_lower or "adr" in name_lower or "record" in name_lower or "graph" in name_lower or "dtase" in name_lower:
                    categories["Architectural Standards"].append(f_name)
                else:
                    categories["Other Specifications"].append(f_name)
    except Exception as e:
        print(f"Error scanning documents: {e}", file=sys.stderr)
        
    return categories

class DashboardRequestHandler(BaseHTTPRequestHandler):
    """Serve Dashboard HTTP requests."""
    
    def log_message(self, format, *args):
        # Silence HTTP requests logging to stdout
        pass

    def handle_static(self, file_path, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.wfile.write(f.read().encode("utf-8"))
        except FileNotFoundError:
            self.wfile.write(f"<h1>File not found: {os.path.basename(file_path)}</h1>".encode("utf-8"))

    def handle_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", APPLICATION_JSON)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def handle_doc_content(self, query):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        file_name = query.get("file", [""])[0]
        file_name = os.path.basename(file_name)  # Sanitization against directory traversal
        
        docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Requirements Master")
        file_path = os.path.join(docs_dir, file_name)
        
        if file_name and os.path.exists(file_path) and file_name.endswith(".md"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            except Exception as e:
                self.wfile.write(f"Error reading file: {e}".encode("utf-8"))
        else:
            self.wfile.write(b"Document not found or access denied.")

    def do_GET(self):
        global status_cache
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)
        
        if path in STATIC_ROUTES:
            file_path, content_type = STATIC_ROUTES[path]
            self.handle_static(file_path, content_type)
        elif path == "/api/requirement/list":
            try:
                import uawos_requirement_studio
                self.handle_json(uawos_requirement_studio.load_state())
            except Exception as e:
                self.handle_json({"error": str(e)})
        elif path == "/api/status":
            self.handle_json(status_cache)
        elif path == "/api/traceability":
            matrix = uawos_traceability.get_traceability_matrix(status_cache)
            health = uawos_traceability.get_delivery_health(matrix)
            self.handle_json({"matrix": matrix, "health": health})
        elif path == "/api/roadmap":
            matrix = uawos_traceability.get_traceability_matrix(status_cache)
            roadmap = uawos_traceability.get_roadmap_data(matrix)
            self.handle_json(roadmap)
        elif path == "/api/changes":
            self.handle_json(uawos_traceability.get_change_detection())
        elif path == "/api/generate_prompt":
            roadmap_id = query.get("roadmap_id", [None])[0]
            matrix = uawos_traceability.get_traceability_matrix(status_cache)
            prompt = uawos_traceability.generate_antigravity_prompt(matrix, roadmap_id)
            self.handle_json({"prompt": prompt})
        elif path == "/api/docs":
            self.handle_json(get_documents())
        elif path == "/api/docs/content":
            self.handle_doc_content(query)
        elif path == "/api/budget/status":
            try:
                import uawos_budget
                self.handle_json(uawos_budget.get_summary())
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.handle_json({"error": str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_dtase_analyze(self, payload):
        """Handle DTASE unstructured input analysis."""
        text = payload.get("text", "")
        import uawos_dtase
        result = uawos_dtase.analyze_unstructured_input(text)
        self.send_response(200)
        self.send_header("Content-Type", APPLICATION_JSON)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _handle_budget_action(self, payload):
        """Handle budget actions and adjustments."""
        action = payload.get("action", "")
        import uawos_budget
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
            result = {"status": "error", "error": f"Unknown action: {action}"}
            
        self.send_response(200)
        self.send_header("Content-Type", APPLICATION_JSON)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _handle_requirement_submit(self, payload):
        """Submit a new requirement to the intelligence studio."""
        title = payload.get("title", "New Requirement")
        text = payload.get("text", "")
        import uawos_requirement_studio
        result = uawos_requirement_studio.submit_new_requirement(title, text)
        self.send_response(200)
        self.send_header("Content-Type", APPLICATION_JSON)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _handle_requirement_clarify(self, payload):
        """Update answers to clarification questions."""
        req_id = payload.get("requirement_id", "")
        answers = payload.get("answers", {})
        waive = payload.get("waive", False)
        import uawos_requirement_studio
        result = uawos_requirement_studio.update_clarifications(req_id, answers, waive)
        self.send_response(200)
        self.send_header("Content-Type", APPLICATION_JSON)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _handle_requirement_author(self, payload):
        """Author strategic proposition for a requirement."""
        req_id = payload.get("requirement_id", "")
        import uawos_requirement_studio
        result = uawos_requirement_studio.author_proposition(req_id)
        self.send_response(200)
        self.send_header("Content-Type", APPLICATION_JSON)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _handle_requirement_absorb(self, payload):
        """Absorb candidate and prioritize it against active roadmap."""
        req_id = payload.get("requirement_id", "")
        import uawos_requirement_studio
        result = uawos_requirement_studio.absorb_requirement(req_id)
        self.send_response(200)
        self.send_header("Content-Type", APPLICATION_JSON)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _handle_requirement_publish(self, payload):
        """Publish absorbed candidate to active roadmap portfolio."""
        cand_id = payload.get("roadmap_id", "")
        import uawos_requirement_studio
        result = uawos_requirement_studio.publish_roadmap_item(cand_id)
        self.send_response(200)
        self.send_header("Content-Type", APPLICATION_JSON)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _handle_requirement_reset(self):
        """Reset requirement studio state."""
        import uawos_requirement_studio
        state = uawos_requirement_studio.get_default_state()
        uawos_requirement_studio.save_state(state)
        if os.path.exists(uawos_requirement_studio.STATE_FILE):
            os.remove(uawos_requirement_studio.STATE_FILE)
        self.send_response(200)
        self.send_header("Content-Type", APPLICATION_JSON)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "SUCCESS"}).encode('utf-8'))

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            payload = {}
            if post_data:
                payload = json.loads(post_data.decode('utf-8'))
                
            if path == "/api/dtase/analyze":
                self._handle_dtase_analyze(payload)
            elif path == "/api/budget/action":
                self._handle_budget_action(payload)
            elif path == "/api/requirement/submit":
                self._handle_requirement_submit(payload)
            elif path == "/api/requirement/clarify":
                self._handle_requirement_clarify(payload)
            elif path == "/api/requirement/author":
                self._handle_requirement_author(payload)
            elif path == "/api/requirement/absorb":
                self._handle_requirement_absorb(payload)
            elif path == "/api/requirement/publish":
                self._handle_requirement_publish(payload)
            elif path == "/api/requirement/reset":
                self._handle_requirement_reset()
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", APPLICATION_JSON)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

def start_server():
    server = HTTPServer(("0.0.0.0", PORT), DashboardRequestHandler)
    print(f"Server started on http://0.0.0.0:{PORT}")
    try:
        server.serve_forever()
        # Keep linter happy
        return 0
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    # Perform initial check before starting server
    print("Initializing UAWOS health monitors...")
    status_cache = run_health_checks()
    with open(STATUS_FILE, "w") as f:
        json.dump(status_cache, f, indent=2)

    # Start the daemon monitoring thread
    t = threading.Thread(target=daemon_loop, daemon=True)
    t.start()

    # Start the web server
    start_server()
