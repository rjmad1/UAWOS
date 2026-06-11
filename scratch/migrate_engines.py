# scratch/migrate_engines.py
import os
import re

engines = [
    "uawos_objective",
    "uawos_outcome",
    "uawos_planning",
    "uawos_workflow",
    "uawos_action",
    "uawos_workforce",
    "uawos_agent_workforce",
    "uawos_governance",
    "uawos_knowledge",
    "uawos_memory",
    "uawos_learning",
    "uawos_resource",
    "uawos_budget",
    "uawos_decision",
    "uawos_simulation",
    "uawos_value",
    "uawos_observability",
    "uawos_integrations",
    "uawos_requirement_studio"
]

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for engine in engines:
    file_path = os.path.join(base_dir, f"{engine}.py")
    if not os.path.exists(file_path):
        print(f"Skipping {engine}.py (not found)")
        continue
        
    print(f"Migrating {engine}.py...")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Inject import uawos_db if not present
    if "import uawos_db" not in content:
        # Insert at line 2 (after initial comment or first import)
        lines = content.splitlines()
        inserted = False
        for idx, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                lines.insert(idx, "import uawos_db")
                inserted = True
                break
        if not inserted:
            lines.insert(1, "import uawos_db")
        content = "\n".join(lines) + "\n"
        
    # Replace load_state and save_state
    # We will look for def load_state and replace the whole block up to the next def or comment
    # Let's use a regex to identify the load_state and save_state functions
    pattern = r"(def load_state\(\)(?:\s*->\s*\w+)?:\s*[\s\S]*?)(def save_state\([\s\S]*?:\s*[\s\S]*?)(?=\n#|\ndef|\nif __name__)"
    
    new_load_save = f"""def load_state() -> dict:
    state = uawos_db.db_get_state("{engine}", None)
    if state is not None:
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(state, f, indent=2)
        except Exception:
            pass
        return state
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
        print(f"Error saving local state cache: {{e}}")
    uawos_db.db_save_state("{engine}", state)"""

    modified_content, count = re.subn(pattern, new_load_save, content)
    if count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        print(f"  Successfully migrated {engine}.py (replaced {count} matches)")
    else:
        print(f"  [ERROR] Pattern not matched for {engine}.py")

print("Migration completed!")
