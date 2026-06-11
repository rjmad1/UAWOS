import importlib
import sys
import traceback
import os


def run_module_tests(module_name):
    try:
        mod = importlib.import_module(module_name)
        if hasattr(mod, "run_self_tests"):
            print(f"\nRunning self tests for {module_name}...")
            mod.run_self_tests()
        else:
            print(f"  [SKIP] {module_name} has no run_self_tests()")
    except Exception as e:
        print(f"  [ERROR] {module_name}: {e}")
        traceback.print_exc()


# Ensure project root is in path (resolve dynamically relative to this script)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Only scan top-level uawos_*.py files (skip .venv, scratch, subdirs)
for fname in sorted(os.listdir(project_root)):
    if fname.startswith("uawos_") and fname.endswith(".py") and fname != "__init__.py":
        module_name = fname[:-3]  # strip .py
        run_module_tests(module_name)

print("\n=== All UAWOS self tests executed. ===")
