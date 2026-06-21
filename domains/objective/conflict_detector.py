# domains/objective/conflict_detector.py

from .objective import Objective

PRIORITY_LEVELS = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}


def detect_conflicts(objectives: dict[str, Objective]) -> list[dict]:
    """Scan objectives and detect circular dependency cycles, priority mismatches, and status mismatches."""
    conflicts = []

    # 1. Circular dependency check (Cycle detection using DFS)
    def has_cycle(obj_id, visited, stack, path):
        visited.add(obj_id)
        stack.add(obj_id)
        path.append(obj_id)

        obj = objectives.get(obj_id)
        if obj:
            for dep_id in obj.dependencies:
                if dep_id not in visited:
                    if has_cycle(dep_id, visited, stack, path):
                        return True
                elif dep_id in stack:
                    path.append(dep_id)
                    return True
        stack.remove(obj_id)
        path.pop()
        return False

    for obj_id in objectives:
        visited = set()
        stack = set()
        path = []
        if has_cycle(obj_id, visited, stack, path):
            cycle_str = " -> ".join(path[path.index(path[-1]) :])
            conflicts.append(
                {
                    "type": "Circular Dependency",
                    "objectives": list(set(path)),
                    "message": f"Circular dependency detected in execution paths: {cycle_str}",
                }
            )
            break  # report one cycle at a time

    # 2. Priority and Status mismatches
    for obj_id, obj in objectives.items():
        obj_priority = PRIORITY_LEVELS.get(obj.priority, 2)

        for dep_id in obj.dependencies:
            dep = objectives.get(dep_id)
            if dep:
                # Priority conflict: Higher priority depends on a much lower priority item
                dep_priority = PRIORITY_LEVELS.get(dep.priority, 2)
                if obj_priority >= 3 and dep_priority <= 1:  # High/Critical depending on Low
                    conflicts.append(
                        {
                            "type": "Priority Conflict",
                            "objectives": [obj_id, dep_id],
                            "message": f"High priority objective {obj_id} ({obj.priority}) depends on low priority dependency {dep_id} ({dep.priority}).",
                        }
                    )

                # Status conflict: Active objective depends on cancelled or archived dependency
                if obj.status == "active" and dep.status in ["cancelled", "archived"]:
                    conflicts.append(
                        {
                            "type": "Status Conflict",
                            "objectives": [obj_id, dep_id],
                            "message": f"Active objective {obj_id} depends on a dependency {dep_id} which is {dep.status}.",
                        }
                    )

    return conflicts
