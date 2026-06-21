import os
import json
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXCLUDE_DIRS = {'.git', '.venv', '.vscode', '.pytest_cache', '__pycache__', '.ruff_cache', '.agents', '.ai', '.claude', '.codex', '.playwright-mcp'}

def get_title_and_desc(filepath):
    title = os.path.basename(filepath)
    desc = "No description available."
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find first h1
            h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()
            
            # Find some introductory text (not code, headers, etc)
            lines = content.split('\n')
            desc_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                if line.startswith('```'):
                    continue
                if line.startswith('-') or line.startswith('*'):
                    continue
                # Take first 1-2 substantial sentences
                desc_lines.append(line)
                if len(desc_lines) >= 2:
                    break
            if desc_lines:
                desc = " ".join(desc_lines)
                if len(desc) > 120:
                    desc = desc[:117] + "..."
    except Exception as e:
        pass
    return title, desc

def get_category(rel_path):
    parts = rel_path.split('/')
    if len(parts) == 1:
        return "Core Guides"
    
    first_dir = parts[0]
    if first_dir == "wiki_repo":
        return "System Wiki & Design"
    elif first_dir == "Requirements Master":
        if "UI UX Needs" in rel_path:
            return "UI & UX Strategy"
        elif "claudedirectory_imports" in rel_path:
            if "agents" in rel_path:
                return "Agent Personas"
            elif "skills" in rel_path:
                return "Agent Skills"
        return "System Requirements & Standards"
    elif first_dir == "weaverouter":
        return "WeaveRouter Specs"
    elif first_dir == "governance":
        return "Governance Policies"
    elif first_dir == "plans":
        return "Implementation Plans"
    
    return "Other Specs"

def scan():
    documents = []
    for root, dirs, files in os.walk(ROOT_DIR):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file.endswith('.md'):
                fullpath = os.path.join(root, file)
                rel_path = os.path.relpath(fullpath, ROOT_DIR).replace('\\', '/')
                title, desc = get_title_and_desc(fullpath)
                
                # Exclude temporary or scratch docs if any
                if 'scratch/' in rel_path or 'tmp/' in rel_path:
                    continue
                
                category = get_category(rel_path)
                
                # Determine owner based on folder/file
                owner = "System Architect"
                if "governance" in rel_path or "security" in rel_path.lower():
                    owner = "Security Office"
                elif "UI UX" in rel_path or "design" in rel_path.lower():
                    owner = "UX Designer"
                elif "claudedirectory_imports" in rel_path:
                    owner = "AI Workforce Dev"
                elif "weaverouter" in rel_path:
                    owner = "Router Team"
                
                # Mock a last updated date based on file mod time or constant
                try:
                    mtime = os.path.getmtime(fullpath)
                    import time
                    last_updated = time.strftime('%Y-%m-%d', time.localtime(mtime))
                except Exception:
                    last_updated = "2026-06-21"
                
                documents.append({
                    "name": title,
                    "type": category,
                    "path": rel_path,
                    "description": desc,
                    "lastUpdated": last_updated,
                    "owner": owner
                })
    
    # Sort documents by category then name
    documents.sort(key=lambda d: (d["type"], d["name"]))
    with open(os.path.join(ROOT_DIR, "scratch", "all_docs.json"), "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2)
    print(f"Scanned {len(documents)} documents and saved to scratch/all_docs.json")

if __name__ == "__main__":
    scan()
