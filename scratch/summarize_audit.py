import json

with open(r"C:\Users\rajaj\Projects\UAWOS\scratch\audit_report_data.json", encoding="utf-8") as f:
    data = json.load(f)

print("=== CODEBASE STRUCTURE SUMMARY ===")
print(f"Total UAWOS files audited: {len(data)}\n")

# 1. AI Stack Usage
ai_packages = [
    "pydantic_ai",
    "dspy",
    "instructor",
    "outlines",
    "guidance",
    "mem0ai",
    "graphiti",
    "haystack",
    "llama_index",
    "fastembed",
    "litellm",
    "opentelemetry",
]
ai_usage = {}
for fname, info in data.items():
    if "error" in info:
        continue
    imports = info["imports"]
    used = []
    for pkg in ai_packages:
        for imp in imports:
            if imp.startswith(pkg):
                used.append(pkg)
    if used:
        ai_usage[fname] = list(set(used))

print("AI Stack / Agent / RAG / Memory Framework imports per file:")
for fname, pkgs in sorted(ai_usage.items()):
    print(f"  {fname}: {', '.join(pkgs)}")
print()

# 2. SQL Line Numbers
sql_files = {fname: info["sql_lines"] for fname, info in data.items() if info.get("sql_lines")}
print("SQL Execution calls found in files:")
for fname, lines in sorted(sql_files.items()):
    print(f"  {fname}: lines {lines}")
print()

# 3. urllib calls
urllib_files = {fname: info["urllib_lines"] for fname, info in data.items() if info.get("urllib_lines")}
print("urllib web request calls found in files:")
for fname, lines in sorted(urllib_files.items()):
    print(f"  {fname}: lines {lines}")
print()

# 4. Total classes and functions
total_classes = 0
total_functions = 0
all_classes = []
for fname, info in data.items():
    if "error" in info:
        continue
    total_classes += len(info["classes"])
    total_functions += len(info["functions"])
    for cls in info["classes"]:
        all_classes.append(f"{cls['name']} ({fname})")

print(f"Total Classes: {total_classes}")
print(f"Total Functions: {total_functions}")
print("\nSample Classes:")
for c in sorted(all_classes)[:30]:
    print(f"  - {c}")
if len(all_classes) > 30:
    print(f"  ... and {len(all_classes) - 30} more classes.")
