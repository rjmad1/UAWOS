# domains/billing/billing.py
from dataclasses import dataclass

# Model pricing structures per 1M tokens
MODEL_PRICING = {
    "tinyllama": {"input": 0.07, "output": 0.07, "reasoning": 0.07},
    "llama3": {"input": 0.15, "output": 0.60, "reasoning": 0.60},
    "deepseek-r1": {"input": 0.55, "output": 2.19, "reasoning": 2.19},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00, "reasoning": 5.00},
    "default": {"input": 0.15, "output": 0.60, "reasoning": 0.60},
}


@dataclass
class ObjectiveBudget:
    name: str
    budget: float
    actual: float = 0.0
    status: str = "Pending"  # Pending, Approved, Rejected

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "budget": self.budget,
            "actual": self.actual,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ObjectiveBudget":
        return cls(
            name=data["name"],
            budget=float(data["budget"]),
            actual=float(data.get("actual", 0.0)),
            status=data.get("status", "Pending"),
        )


@dataclass
class ActionBudget:
    name: str
    objective_id: str
    budget: float
    actual: float = 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "objective_id": self.objective_id,
            "budget": self.budget,
            "actual": self.actual,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActionBudget":
        return cls(
            name=data["name"],
            objective_id=data["objective_id"],
            budget=float(data["budget"]),
            actual=float(data.get("actual", 0.0)),
        )


@dataclass
class AgentCost:
    cost: float = 0.0
    token_count: int = 0
    call_count: int = 0

    def to_dict(self) -> dict:
        return {
            "cost": self.cost,
            "token_count": self.token_count,
            "call_count": self.call_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentCost":
        return cls(
            cost=float(data.get("cost", 0.0)),
            token_count=int(data.get("token_count", 0)),
            call_count=int(data.get("call_count", 0)),
        )


@dataclass
class TokenConsumption:
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    cost: float = 0.0

    def to_dict(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "cost": self.cost,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TokenConsumption":
        return cls(
            input_tokens=int(data.get("input_tokens", 0)),
            output_tokens=int(data.get("output_tokens", 0)),
            reasoning_tokens=int(data.get("reasoning_tokens", 0)),
            cost=float(data.get("cost", 0.0)),
        )


@dataclass
class BudgetApproval:
    id: str
    objective_id: str
    amount: float
    status: str = "Pending"  # Pending, Approved, Rejected
    requested_by: str = ""
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "objective_id": self.objective_id,
            "amount": self.amount,
            "status": self.status,
            "requested_by": self.requested_by,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BudgetApproval":
        return cls(
            id=data["id"],
            objective_id=data["objective_id"],
            amount=float(data["amount"]),
            status=data.get("status", "Pending"),
            requested_by=data.get("requested_by", ""),
            timestamp=data.get("timestamp", ""),
        )


def calculate_cost_run_rate(objective_budgets: dict[str, ObjectiveBudget]) -> dict:
    """Calculate linear forecast and variances across all objective budgets."""
    total_budget = sum(o.budget for o in objective_budgets.values())
    total_actual = sum(o.actual for o in objective_budgets.values())

    # Assume 10 days of run elapsed, total 30 planned (preserving historical logic)
    elapsed_days = 10
    total_days = 30
    run_rate_per_day = round(total_actual / elapsed_days, 2) if elapsed_days > 0 else 0.0
    forecast_spend = round(run_rate_per_day * total_days, 2)

    variance = round(total_actual - total_budget, 2)
    variance_pct = round((variance / total_budget) * 100, 1) if total_budget > 0 else 0.0

    is_over_budget_risk = forecast_spend > total_budget

    return {
        "total_budget": total_budget,
        "total_actual": total_actual,
        "run_rate_per_day": run_rate_per_day,
        "forecast_spend": forecast_spend,
        "variance": variance,
        "variance_pct": variance_pct,
        "is_over_budget_risk": is_over_budget_risk,
    }


def evaluate_cost_governance(budget: float, actual: float, threshold_ratio: float = 0.9) -> dict:
    """Compute consumption ratio and cost status verdict."""
    ratio = actual / budget if budget > 0 else 0.0

    verdict = "APPROVED"
    message = "Cost levels within safe operating parameters."

    if ratio >= 1.0:
        verdict = "BREACHED"
        message = f"Budget limit of ${budget:.2f} exceeded! Active execution blocked by Governor."
    elif ratio >= threshold_ratio:
        verdict = "WARNING"
        message = f"Objective has consumed {ratio * 100:.1f}% of allocated budget. Optimization recommended."

    return {
        "budget": budget,
        "actual": actual,
        "consumption_ratio": round(ratio, 3),
        "governance_verdict": verdict,
        "message": message,
    }
