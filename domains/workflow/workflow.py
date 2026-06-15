# domains/workflow/workflow.py
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Workflow:
    id: str
    plan_id: str
    title: str
    tasks: List[str]
    dependencies: List[str] = field(default_factory=list)
    state: str = "active"
    version: int = 1
    history: List[Dict[str, Any]] = field(default_factory=list)
    governed: bool = True
    execution_mode: str = None
    temporal_run_id: str = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "title": self.title,
            "tasks": self.tasks,
            "dependencies": self.dependencies,
            "state": self.state,
            "version": self.version,
            "history": self.history,
            "governed": self.governed,
            "execution_mode": self.execution_mode,
            "temporal_run_id": self.temporal_run_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Workflow":
        return cls(
            id=data["id"],
            plan_id=data["plan_id"],
            title=data["title"],
            tasks=list(data["tasks"]),
            dependencies=list(data.get("dependencies", [])),
            state=data.get("state", "active"),
            version=int(data.get("version", 1)),
            history=list(data.get("history", [])),
            governed=bool(data.get("governed", True)),
            execution_mode=data.get("execution_mode"),
            temporal_run_id=data.get("temporal_run_id"),
        )

    def simulate(self) -> dict:
        """Simulate workflow execution."""
        return {
            "workflow_id": self.id,
            "estimated_duration_seconds": len(self.tasks) * 3600,
            "bottlenecks": ["Dependency check bottleneck" if self.dependencies else "None"],
            "simulation_verdict": "Success predicted",
        }

    def optimize(self) -> List[str]:
        """Sort tasks to optimize execution order (simulated optimization)."""
        return sorted(self.tasks)
