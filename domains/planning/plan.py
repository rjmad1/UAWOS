# domains/planning/plan.py
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Plan:
    id: str
    objective_id: str
    title: str
    steps: List[str]
    cost_estimate: float
    duration_estimate: int
    resource_requirements: List[str]
    success_probability: float
    status: str = "draft"
    version: int = 1
    history: List[Dict[str, Any]] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    is_alternative: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "objective_id": self.objective_id,
            "title": self.title,
            "steps": self.steps,
            "cost_estimate": self.cost_estimate,
            "duration_estimate": self.duration_estimate,
            "resource_requirements": self.resource_requirements,
            "success_probability": self.success_probability,
            "status": self.status,
            "version": self.version,
            "history": self.history,
            "risks": self.risks,
            "assumptions": self.assumptions,
            "is_alternative": self.is_alternative,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Plan":
        return cls(
            id=data["id"],
            objective_id=data["objective_id"],
            title=data["title"],
            steps=list(data["steps"]),
            cost_estimate=float(data["cost_estimate"]),
            duration_estimate=int(data["duration_estimate"]),
            resource_requirements=list(data["resource_requirements"]),
            success_probability=float(data["success_probability"]),
            status=data.get("status", "draft"),
            version=int(data.get("version", 1)),
            history=list(data.get("history", [])),
            risks=list(data.get("risks", ["General delivery risk"])),
            assumptions=list(data.get("assumptions", ["Required resources are available"])),
            is_alternative=bool(data.get("is_alternative", False)),
        )

    def calculate_score(self) -> float:
        """Calculate ranking score based on success probability, cost, and duration."""
        # High success probability is good, low cost is good, low duration is good
        return self.success_probability * 100 - (self.cost_estimate / 10.0) - self.duration_estimate

    def simulate(self) -> dict:
        """Simulate execution pathway to predict success, cost, and duration shifts."""
        simulated_success = round(self.success_probability * 0.98, 2)
        simulated_cost = round(self.cost_estimate * 1.05, 2)
        simulated_duration = self.duration_estimate + 1

        return {
            "plan_id": self.id,
            "simulated_success_probability": simulated_success,
            "simulated_cost": simulated_cost,
            "simulated_duration": simulated_duration,
            "verdict": "Within acceptable limits" if simulated_success > 0.7 else "High risk",
        }
