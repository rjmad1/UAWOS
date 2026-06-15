# domains/outcome/outcome.py
from dataclasses import dataclass, field
from typing import List


@dataclass
class Outcome:
    id: str
    objective_id: str
    title: str
    metric: str
    unit: str
    weight: float = 1.0
    dependencies: List[str] = field(default_factory=list)
    confidence_score: float = 90.0
    owner: str = "Product Owner"
    baseline_state: float = 0.0
    target_state: float = 100.0
    current_state: float = 0.0
    forecasted_state: float = 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "objective_id": self.objective_id,
            "title": self.title,
            "metric": self.metric,
            "unit": self.unit,
            "weight": self.weight,
            "dependencies": self.dependencies,
            "confidence_score": self.confidence_score,
            "owner": self.owner,
            "baseline_state": self.baseline_state,
            "target_state": self.target_state,
            "current_state": self.current_state,
            "forecasted_state": self.forecasted_state,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Outcome":
        return cls(
            id=data["id"],
            objective_id=data["objective_id"],
            title=data["title"],
            metric=data["metric"],
            unit=data["unit"],
            weight=float(data.get("weight", 1.0)),
            dependencies=list(data.get("dependencies", [])),
            confidence_score=float(data.get("confidence_score", 90.0)),
            owner=data.get("owner", "Product Owner"),
            baseline_state=float(data.get("baseline_state", 0.0)),
            target_state=float(data.get("target_state", 100.0)),
            current_state=float(data.get("current_state", 0.0)),
            forecasted_state=float(data.get("forecasted_state", 0.0)),
        )

    def calculate_forecast(self) -> float:
        """Estimate outcome forecasting based on progress trends (FR-036)."""
        diff = self.target_state - self.baseline_state
        progress = self.current_state - self.baseline_state

        if diff == 0:
            return self.target_state
        else:
            # Forecast 10% progress increment as estimate
            ratio = progress / diff
            return round(self.baseline_state + diff * min(1.0, ratio + 0.1), 2)
