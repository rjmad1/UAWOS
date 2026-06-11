# scratch/debug_hang.py
import os
import sys
import threading
import time
import traceback

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def dump_stack():
    time.sleep(5)
    print("=== HANG DETECTED, DUMPING STACKS ===")
    for thread_id, stack in sys._current_frames().items():
        print(f"\nThread ID: {thread_id}")
        traceback.print_stack(stack)
    sys.exit(1)


# Start monitor thread
t = threading.Thread(target=dump_stack, daemon=True)
t.start()

print("Importing uawos_objective...")
import uawos_objective

print("Running verify_fr_011...")
uawos_objective.verify_fr_011()
print("verify_fr_011 finished.")
