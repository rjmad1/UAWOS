import os
import ast
import json
import re

class CodebaseAuditor(ast.NodeVisitor):
    def __init__(self, filepath):
        self.filepath = filepath
        self.imports = []
        self.classes = []
        self.functions = []
        self.ai_terms = []
        self.todo_comments = []
        self.sql_executions = []
        self.urllib_calls = []
        self.sys_calls = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.classes.append({
            "name": node.name,
            "lineno": node.lineno,
            "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        })
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.functions.append({
            "name": node.name,
            "lineno": node.lineno
        })
        self.generic_visit(node)

    def visit_Call(self, node):
        # Check for cursor.execute or conn.execute
        if isinstance(node.func, ast.Attribute) and node.func.attr == "execute":
            # get source line
            self.sql_executions.append(node.lineno)
        # Check for urllib.request.urlopen
        if isinstance(node.func, ast.Attribute) and node.func.attr == "urlopen":
            self.urllib_calls.append(node.lineno)
        self.generic_visit(node)

def audit_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Find comments like TODO/FIXME
    todos = []
    for i, line in enumerate(content.splitlines(), 1):
        if "TODO" in line or "FIXME" in line:
            todos.append((i, line.strip()))

    try:
        tree = ast.parse(content, filename=filepath)
        auditor = CodebaseAuditor(filepath)
        auditor.visit(tree)
        
        # Check for AI terms in content
        ai_terms = []
        for term in ["agent", "prompt", "rag", "embed", "llm", "openai", "claude", "gemini", "litellm", "telemetry", "opentelemetry"]:
            matches = list(re.finditer(r'\b' + re.escape(term) + r'\b', content, re.IGNORECASE))
            if matches:
                ai_terms.append((term, len(matches)))

        return {
            "file": os.path.basename(filepath),
            "imports": sorted(list(set(auditor.imports))),
            "classes": auditor.classes,
            "functions": auditor.functions,
            "todos": todos,
            "sql_lines": auditor.sql_executions,
            "urllib_lines": auditor.urllib_calls,
            "ai_terms": ai_terms
        }
    except Exception as e:
        return {
            "file": os.path.basename(filepath),
            "error": str(e)
        }

def run_audit(root_dir):
    results = {}
    for fname in os.listdir(root_dir):
        if fname.startswith("uawos_") and fname.endswith(".py") and fname != "__init__.py":
            filepath = os.path.join(root_dir, fname)
            results[fname] = audit_file(filepath)
            
    with open(os.path.join(root_dir, "scratch", "audit_report_data.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Audited {len(results)} files. Written to scratch/audit_report_data.json")

if __name__ == "__main__":
    run_audit(r"C:\Users\rajaj\Projects\UAWOS")
