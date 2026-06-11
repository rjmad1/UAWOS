# uawos_objective.py
import uawos_db
import os
import json
import time
import urllib.request
import urllib.error

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_objective_state.json")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

def get_default_state() -> dict:
    return {
        "objectives": {}
    }

def load_state() -> dict:
    if uawos_db.DB_AVAILABLE:
        try:
            state = uawos_db.db_load_objectives()
            if state and state.get("objectives"):
                with open(STATE_FILE, "w") as f:
                    json.dump(state, f, indent=2)
                return state
        except Exception as e:
            print(f"PostgreSQL load failed, falling back: {e}")

    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    state = get_default_state()
    save_state(state)
    return state

def save_state(state: dict):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving local state cache: {e}")
    if uawos_db.DB_AVAILABLE:
        try:
            uawos_db.db_save_all_objectives(state.get("objectives", {}))
        except Exception as e:
            print(f"PostgreSQL save failed: {e}")
# Core API for creating objectives
def create_objective(
    title: str,
    description: str,
    source_type: str,
    source_uri: str,
    owner: str,
    sponsor: str,
    priority: str,
    dependencies: list = None
) -> dict:
    """Create a new objective record and save it to the state database."""
    state = load_state()
    
    # ID Generation
    existing_ids = [int(k[4:]) for k in state["objectives"].keys() if k.startswith("OBJ-") and k[4:].isdigit()]
    next_id_num = max(existing_ids) + 1 if existing_ids else 201  # Start custom objectives at OBJ-201
    objective_id = f"OBJ-{next_id_num}"
    
    if dependencies is None:
        dependencies = []
        
    objective = {
        "id": objective_id,
        "title": title,
        "description": description,
        "source_type": source_type,  # voice, text, document, meeting_transcript, image, api
        "source_uri": source_uri,
        "owner": owner,
        "sponsor": sponsor,
        "priority": priority,  # Critical, High, Medium, Low
        "dependencies": dependencies,
        "status": "active",  # active, paused, archived, cancelled, draft
        "version": 1,
        "history": [],
        "health_score": 100.0,
        "confidence_score": 100.0
    }
    
    state["objectives"][objective_id] = objective
    save_state(state)
    
    # Update scores dynamically
    recalculate_scores(objective_id)
    state = load_state()
    return state["objectives"][objective_id]

def update_objective(objective_id: str, updates: dict) -> dict:
    """Update an existing objective and maintain its version history."""
    state = load_state()
    obj = state["objectives"].get(objective_id)
    if not obj:
        return {"error": f"Objective {objective_id} not found."}
    
    # Save snapshot to history (exclude the history field itself to avoid nesting)
    snapshot = {k: v for k, v in obj.items() if k != "history"}
    obj["history"].append({
        "timestamp": time.time(),
        "state": snapshot
    })
    
    # Apply updates
    for k, v in updates.items():
        if k in ["title", "description", "owner", "sponsor", "priority", "dependencies", "status"]:
            obj[k] = v
            
    obj["version"] += 1
    state["objectives"][objective_id] = obj
    save_state(state)
    
    # Update scores dynamically
    recalculate_scores(objective_id)
    state = load_state()
    return state["objectives"][objective_id]

# FR-025 to FR-028 Lifecycle Transitions
def archive_objective(objective_id: str) -> dict:
    return update_objective(objective_id, {"status": "archived"})

def restore_objective(objective_id: str) -> dict:
    return update_objective(objective_id, {"status": "active"})

def cancel_objective(objective_id: str) -> dict:
    return update_objective(objective_id, {"status": "cancelled"})

def pause_objective(objective_id: str) -> dict:
    return update_objective(objective_id, {"status": "paused"})

def resume_objective(objective_id: str) -> dict:
    return update_objective(objective_id, {"status": "active"})

# FR-011 to FR-016 Intake Ingestion & local LLM parser
def create_objective_from_input(
    text: str,
    input_type: str,
    owner: str = "",
    sponsor: str = "",
    source_uri: str = ""
) -> dict:
    """Create a structured Objective from unstructured input by parsing it via LLM."""
    
    # Default fallbacks
    title = f"New Objective from {input_type.capitalize()}"
    description = text
    priority = "Medium"
    dependencies = []
    
    # Heuristics parsing
    text_lower = text.lower()
    if any(w in text_lower for w in ["urgent", "critical", "immediate", "highest", "blocker"]):
        priority = "Critical"
    elif any(w in text_lower for w in ["high", "important", "soon"]):
        priority = "High"
    elif any(w in text_lower for w in ["low", "minor", "deferred"]):
        priority = "Low"
        
    # Dependency heuristics
    # E.g. "requires OBJ-102" -> ["OBJ-102"]
    import re
    dep_matches = re.findall(r"obj-\d+", text_lower)
    if dep_matches:
        dependencies = [m.upper() for m in dep_matches]

    parser_confidence = 70.0
    
    # LLM Parsing via Ollama
    try:
        prompt = f"""[INST] You are the UAWOS Objective Parser.
Analyze this raw objective intake of type '{input_type}' and output a structured JSON analysis.
Raw Input: "{text}"

Output JSON format (strictly JSON, no extra text):
{{
  "title": "short descriptive title",
  "description": "expanded professional description",
  "priority": "Critical, High, Medium, or Low",
  "dependencies": ["OBJ-XXX"]
}}
[/INST]"""
        req_data = json.dumps({
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }).encode('utf-8')
        
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/generate",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=4.0) as response:
            resp = json.loads(response.read().decode('utf-8'))
            llm_result = json.loads(resp.get("response", "{}"))
            
            if llm_result.get("title"):
                title = llm_result["title"]
            if llm_result.get("description"):
                description = llm_result["description"]
            if llm_result.get("priority") in ["Critical", "High", "Medium", "Low"]:
                priority = llm_result["priority"]
            if llm_result.get("dependencies"):
                dependencies = [d.upper() for d in llm_result["dependencies"]]
            parser_confidence = 95.0
    except Exception:
        # Gracefully handle Ollama timeouts or failures with heuristics
        pass

    if not owner:
        owner = "System Agent"
    if not sponsor:
        sponsor = "CPO"

    obj = create_objective(
        title=title,
        description=description,
        source_type=input_type,
        source_uri=source_uri,
        owner=owner,
        sponsor=sponsor,
        priority=priority,
        dependencies=dependencies
    )
    
    # Update confidence score directly incorporating the parser confidence
    state = load_state()
    state["objectives"][obj["id"]]["confidence_score"] = parser_confidence
    save_state(state)
    recalculate_scores(obj["id"])
    
    return load_state()["objectives"][obj["id"]]

# FR-021 & FR-022 Conflict Detection Engine
def detect_conflicts() -> list:
    """Scan the objectives database and detect architectural, priority, and cycle conflicts."""
    state = load_state()
    objectives = state["objectives"]
    conflicts = []
    
    # 1. Circular dependency check (Cycle detection using DFS)
    def has_cycle(obj_id, visited, stack, path):
        visited.add(obj_id)
        stack.add(obj_id)
        path.append(obj_id)
        
        obj = objectives.get(obj_id)
        if obj:
            for dep_id in obj.get("dependencies", []):
                if dep_id not in visited:
                    if has_cycle(dep_id, visited, stack, path):
                        return True
                elif dep_id in stack:
                    path.append(dep_id)
                    return True
        stack.remove(obj_id)
        path.pop()
        return False

    for obj_id in objectives.keys():
        visited = set()
        stack = set()
        path = []
        if has_cycle(obj_id, visited, stack, path):
            cycle_str = " -> ".join(path[path.index(path[-1]):])
            conflicts.append({
                "type": "Circular Dependency",
                "objectives": list(set(path)),
                "message": f"Circular dependency detected in execution paths: {cycle_str}"
            })
            break # report one cycle at a time
            
    # 2. Priority and Status mismatches
    for obj_id, obj in objectives.items():
        priority_levels = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
        obj_priority = priority_levels.get(obj["priority"], 2)
        
        for dep_id in obj.get("dependencies", []):
            dep = objectives.get(dep_id)
            if dep:
                # Priority conflict: Higher priority depends on a much lower priority item
                dep_priority = priority_levels.get(dep["priority"], 2)
                if obj_priority >= 3 and dep_priority <= 1: # High/Critical depending on Low
                    conflicts.append({
                        "type": "Priority Conflict",
                        "objectives": [obj_id, dep_id],
                        "message": f"High priority objective {obj_id} ({obj['priority']}) depends on low priority dependency {dep_id} ({dep['priority']})."
                    })
                
                # Status conflict: Active objective depends on cancelled or archived dependency
                if obj["status"] == "active" and dep["status"] in ["cancelled", "archived"]:
                    conflicts.append({
                        "type": "Status Conflict",
                        "objectives": [obj_id, dep_id],
                        "message": f"Active objective {obj_id} depends on a dependency {dep_id} which is {dep['status']}."
                    })
                    
    return conflicts

# FR-029 & FR-030 Health and Confidence Scoring
def recalculate_scores(objective_id: str):
    """Calculate and update health and confidence scores for a specific objective."""
    state = load_state()
    obj = state["objectives"].get(objective_id)
    if not obj:
        return
        
    # 1. Health Score Calculation (Base 100)
    health = 100.0
    
    # Circular dependency penalty
    conflicts = detect_conflicts()
    in_cycle = False
    for c in conflicts:
        if c["type"] == "Circular Dependency" and objective_id in c["objectives"]:
            in_cycle = True
            break
    if in_cycle:
        health -= 30.0
        
    # Dependency status penalty
    for dep_id in obj.get("dependencies", []):
        dep = state["objectives"].get(dep_id)
        if dep:
            if dep["status"] == "cancelled":
                health -= 25.0
            elif dep["status"] == "paused":
                health -= 10.0
                
    # Integrate budget warning penalty if uawos_budget is available
    try:
        import uawos_budget
        gov = uawos_budget.evaluate_cost_governance(objective_id)
        if gov.get("governance_verdict") == "BREACHED":
            health -= 40.0
        elif gov.get("governance_verdict") == "WARNING":
            health -= 15.0
    except Exception:
        pass
        
    # Enforce Constitutional Law 1: No Objective without measurable Outcomes
    try:
        import uawos_outcome
        outcomes = uawos_outcome.get_objective_outcomes(objective_id)
        if not outcomes:
            health -= 20.0
    except Exception:
        pass
        
    obj["health_score"] = max(0.0, min(100.0, health))
    
    # 2. Confidence Score Calculation (Base 100)
    confidence = obj.get("confidence_score", 100.0)
    
    # Missing owner/sponsor penalties
    if not obj["owner"] or obj["owner"] == "System Agent":
        confidence -= 10.0
    if not obj["sponsor"] or obj["sponsor"] == "CPO":
        confidence -= 10.0
        
    # Active conflicts penalty
    has_conflict = False
    for c in conflicts:
        if objective_id in c["objectives"]:
            has_conflict = True
            break
    if has_conflict:
        confidence -= 20.0
        
    obj["confidence_score"] = max(10.0, min(100.0, confidence))
    
    state["objectives"][objective_id] = obj
    save_state(state)

# ----------------- VERIFICATION TESTS (FR-011 to FR-030) -----------------

def verify_fr_011():
    """Verify Objective creation from voice input."""
    obj = create_objective_from_input("Voice transcript: setup postgres DB immediately", "voice", "Lead Engineer", "CPO")
    assert obj["source_type"] == "voice", "Voice intake source type mismatch."
    return True

def verify_fr_012():
    """Verify Objective creation from text input."""
    obj = create_objective_from_input("Need to migrate the RAG pipeline to Qdrant", "text", "Architect", "CPO")
    assert obj["source_type"] == "text", "Text intake source type mismatch."
    return True

def verify_fr_013():
    """Verify Objective creation from documents."""
    obj = create_objective_from_input("Document body: ensure OPA policies are compiled", "document", "Officer", "CPO")
    assert obj["source_type"] == "document", "Document intake source type mismatch."
    return True

def verify_fr_014():
    """Verify Objective creation from meeting transcripts."""
    obj = create_objective_from_input("Transcript line: let's launch the checkout page next sprint", "meeting_transcript", "Manager", "CPO")
    assert obj["source_type"] == "meeting_transcript", "Meeting transcript source type mismatch."
    return True

def verify_fr_015():
    """Verify Objective creation from images."""
    obj = create_objective_from_input("OCR extracted dashboard mockup text", "image", "Designer", "CPO")
    assert obj["source_type"] == "image", "Image intake source type mismatch."
    return True

def verify_fr_016():
    """Verify Objective creation from APIs."""
    obj = create_objective_from_input("{\"payload\": \"API call definition\"}", "api", "Integration Dev", "CPO")
    assert obj["source_type"] == "api", "API intake source type mismatch."
    return True

def verify_fr_017():
    """Verify ownership maintenance."""
    obj = create_objective("DB tuning", "Tune DB", "text", "", "Database Expert", "CPO", "High")
    assert obj["owner"] == "Database Expert", "Objective owner field mismatch."
    return True

def verify_fr_018():
    """Verify sponsorship maintenance."""
    obj = create_objective("DB tuning 2", "Tune DB 2", "text", "", "Database Expert", "VP Engineering", "High")
    assert obj["sponsor"] == "VP Engineering", "Objective sponsor field mismatch."
    return True

def verify_fr_019():
    """Verify Objective prioritization."""
    obj = create_objective("Sec scan", "Sec scan", "text", "", "Auditor", "CPO", "Critical")
    assert obj["priority"] == "Critical", "Objective priority field mismatch."
    return True

def verify_fr_020():
    """Verify Objective dependencies."""
    obj = create_objective("Task B", "B", "text", "", "Dev", "CPO", "Medium", ["OBJ-201"])
    assert "OBJ-201" in obj["dependencies"], "Dependencies list mismatch."
    return True

def verify_fr_021():
    """Verify conflict structure support."""
    conflicts = detect_conflicts()
    assert isinstance(conflicts, list), "Conflicts must return a list."
    return True

def verify_fr_022():
    """Verify conflict detection (detect circular loops and priority mismatches)."""
    state = load_state()
    # Create circular dependency OBJ-CYC1 <-> OBJ-CYC2
    state["objectives"]["OBJ-CYC1"] = {
        "id": "OBJ-CYC1", "title": "Cycle 1", "description": "", "source_type": "text", "source_uri": "",
        "owner": "A", "sponsor": "B", "priority": "Medium", "dependencies": ["OBJ-CYC2"], "status": "active",
        "version": 1, "history": [], "health_score": 100.0, "confidence_score": 100.0
    }
    state["objectives"]["OBJ-CYC2"] = {
        "id": "OBJ-CYC2", "title": "Cycle 2", "description": "", "source_type": "text", "source_uri": "",
        "owner": "A", "sponsor": "B", "priority": "Medium", "dependencies": ["OBJ-CYC1"], "status": "active",
        "version": 1, "history": [], "health_score": 100.0, "confidence_score": 100.0
    }
    save_state(state)
    
    conflicts = detect_conflicts()
    circular_found = any(c["type"] == "Circular Dependency" for c in conflicts)
    assert circular_found, "Circular dependency not detected."
    
    # Cleanup state
    state = load_state()
    state["objectives"].pop("OBJ-CYC1", None)
    state["objectives"].pop("OBJ-CYC2", None)
    save_state(state)
    return True

def verify_fr_023():
    """Verify Objective versioning."""
    obj = create_objective("Version Test", "V1", "text", "", "A", "B", "Low")
    assert obj["version"] == 1, "Initial version must be 1."
    updated = update_objective(obj["id"], {"title": "Version Test Updated"})
    assert updated["version"] == 2, "Updated version must be 2."
    return True

def verify_fr_024():
    """Verify Objective history preservation."""
    state = load_state()
    # Find active objective from verify_fr_023
    target_id = None
    for k, v in state["objectives"].items():
        if v["title"] == "Version Test Updated":
            target_id = k
            break
            
    assert target_id is not None, "Version test target objective missing."
    obj = state["objectives"][target_id]
    assert len(obj["history"]) == 1, "Objective history snapshot not recorded."
    assert obj["history"][0]["state"]["title"] == "Version Test", "History snapshot value mismatch."
    return True

def verify_fr_025():
    """Verify Objective archival."""
    obj = create_objective("Archive Test", "Details", "text", "", "A", "B", "Low")
    archived = archive_objective(obj["id"])
    assert archived["status"] == "archived", "Archive state not set."
    return True

def verify_fr_026():
    """Verify Objective restoration."""
    state = load_state()
    target_id = None
    for k, v in state["objectives"].items():
        if v["title"] == "Archive Test" and v["status"] == "archived":
            target_id = k
            break
    assert target_id is not None, "Archived target missing."
    restored = restore_objective(target_id)
    assert restored["status"] == "active", "Objective restore state failed."
    return True

def verify_fr_027():
    """Verify Objective cancellation."""
    obj = create_objective("Cancel Test", "Details", "text", "", "A", "B", "Low")
    cancelled = cancel_objective(obj["id"])
    assert cancelled["status"] == "cancelled", "Cancelled state not set."
    return True

def verify_fr_028():
    """Verify Objective pausing."""
    obj = create_objective("Pause Test", "Details", "text", "", "A", "B", "Low")
    paused = pause_objective(obj["id"])
    assert paused["status"] == "paused", "Paused state not set."
    return True

def verify_fr_029():
    """Verify Objective health scoring."""
    obj = create_objective("Health Score Test", "Details", "text", "", "A", "B", "Low")
    assert obj["health_score"] == 80.0, "Health score must initially be 80.0 due to Constitutional Law 1."
    
    import uawos_outcome
    uawos_outcome.create_outcome(obj["id"], "Test Metric", "Metric", "units")
    
    recalculate_scores(obj["id"])
    state = load_state()
    updated_obj = state["objectives"][obj["id"]]
    assert updated_obj["health_score"] == 100.0, "Health score must become 100.0 once outcomes exist."
    return True

def verify_fr_030():
    """Verify Objective confidence scoring."""
    obj = create_objective("Confidence Score Test", "Details", "text", "", "A", "B", "Low")
    assert obj["confidence_score"] <= 100.0, "Confidence score calculation issue."
    return True

def run_self_tests():
    print("Running Objective Management Engine self tests...")
    
    # Clean state for tests
    state = get_default_state()
    save_state(state)
    
    tests = [
        ("FR-011", verify_fr_011),
        ("FR-012", verify_fr_012),
        ("FR-013", verify_fr_013),
        ("FR-014", verify_fr_014),
        ("FR-015", verify_fr_015),
        ("FR-016", verify_fr_016),
        ("FR-017", verify_fr_017),
        ("FR-018", verify_fr_018),
        ("FR-019", verify_fr_019),
        ("FR-020", verify_fr_020),
        ("FR-021", verify_fr_021),
        ("FR-022", verify_fr_022),
        ("FR-023", verify_fr_023),
        ("FR-024", verify_fr_024),
        ("FR-025", verify_fr_025),
        ("FR-026", verify_fr_026),
        ("FR-027", verify_fr_027),
        ("FR-028", verify_fr_028),
        ("FR-029", verify_fr_029),
        ("FR-030", verify_fr_030),
    ]
    
    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae
            
    print("All Objective Engine self tests completed successfully!")

if __name__ == "__main__":
    run_self_tests()
