import subprocess
import sys
import os

test_files = [
    "uawos_objective.py",
    "uawos_budget.py",
    "uawos_governance.py",
    "uawos_planning.py",
    "uawos_workflow.py",
    "uawos_action.py",
    "uawos_outcome.py",
    "uawos_memory.py"
]

print("==================================================")
print("Running All UAWOS Engine Verification Tests")
print("==================================================")

python_exe = os.path.join(".venv", "Scripts", "python.exe")
if not os.path.exists(python_exe):
    python_exe = "python"

all_passed = True
results = {}

for f in test_files:
    print(f"\nRunning tests in {f}...")
    try:
        res = subprocess.run([python_exe, f], capture_output=True, text=True, timeout=75.0)
        if res.returncode == 0:
            print(f"  [PASS] {f}")
            results[f] = "PASS"
        else:
            print(f"  [FAIL] {f} (Exit code: {res.returncode})")
            print("--- STDERR ---")
            print(res.stderr)
            print("--- STDOUT ---")
            print(res.stdout)
            all_passed = False
            results[f] = "FAIL"
    except Exception as e:
        print(f"  [ERROR] {f}: {e}")
        all_passed = False
        results[f] = f"ERROR: {e}"

print("\n==================================================")
print("TEST SUMMARY:")
print("==================================================")
for f, status in results.items():
    print(f"{f:<25} : {status}")
print("==================================================")

if all_passed:
    print("ALL TESTS PASSED SUCCESSFULLY!")
    sys.exit(0)
else:
    print("SOME TESTS FAILED OR ENCOUNTERED ERRORS!")
    sys.exit(1)
