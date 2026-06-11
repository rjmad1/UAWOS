# migrate_state_utils.py
import os
import re
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Find load_state and save_state definitions
    load_start = None
    save_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("def load_state"):
            load_start = i
        if line.strip().startswith("def save_state"):
            save_start = i
    if load_start is None and save_start is None:
        return False

    # Remove the function bodies (simple heuristic: remove until a blank line or next def)
    def remove_block(start_idx):
        end_idx = start_idx + 1
        while end_idx < len(lines) and not lines[end_idx].startswith("def "):
            end_idx += 1
        return start_idx, end_idx

    if load_start is not None:
        ls_start, ls_end = remove_block(load_start)
        del lines[ls_start:ls_end]
    if save_start is not None:
        sv_start, sv_end = remove_block(save_start)
        # adjust if indices shifted due to previous deletion
        if save_start > load_start:
            sv_start -= (ls_end - ls_start) if load_start is not None else 0
            sv_end -= (ls_end - ls_start) if load_start is not None else 0
        del lines[sv_start:sv_end]
    # Insert import after existing imports
    import_line = "from uawos_state_utils import load_state, save_state\n"
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_idx = i + 1
    lines.insert(insert_idx, import_line)
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return True


def main():
    for root, _, files in os.walk(PROJECT_ROOT):
        for f in files:
            if f.endswith(".py") and f not in (
                "uawos_state_utils.py",
                "migrate_state_utils.py",
            ):
                full_path = os.path.join(root, f)
                try:
                    changed = process_file(full_path)
                    if changed:
                        print(f"Refactored {full_path}")
                except Exception as e:
                    print(f"Error processing {full_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
