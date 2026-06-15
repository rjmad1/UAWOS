# domains/governance/governance.py
from dataclasses import dataclass, field
import time


@dataclass
class Policy:
    id: str
    name: str
    rule: str
    category: str
    version: int = 1
    status: str = "draft"  # draft, approved

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "rule": self.rule,
            "category": self.category,
            "version": self.version,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Policy":
        return cls(
            id=data["id"],
            name=data["name"],
            rule=data["rule"],
            category=data["category"],
            version=int(data.get("version", 1)),
            status=data.get("status", "draft"),
        )


@dataclass
class ExceptionRequest:
    id: str
    action_id: str
    reason: str
    status: str = "Pending"  # Pending, Approved, Rejected
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "action_id": self.action_id,
            "reason": self.reason,
            "status": self.status,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExceptionRequest":
        return cls(
            id=data["id"],
            action_id=data["action_id"],
            reason=data["reason"],
            status=data.get("status", "Pending"),
            timestamp=float(data.get("timestamp", time.time())),
        )


@dataclass
class RiskAcceptance:
    risk_id: str
    justification: str
    status: str = "Accepted"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "risk_id": self.risk_id,
            "justification": self.justification,
            "status": self.status,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RiskAcceptance":
        return cls(
            risk_id=data["risk_id"],
            justification=data["justification"],
            status=data.get("status", "Accepted"),
            timestamp=float(data.get("timestamp", time.time())),
        )


@dataclass
class AuditLog:
    event_type: str
    details: dict
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "details": self.details,
            "timestamp": self.timestamp,
        }
