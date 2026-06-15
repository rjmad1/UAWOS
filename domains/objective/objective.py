# domains/objective/objective.py
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Objective:
    id: str
    title: str
    description: str
    source_type: str = "text"
    source_uri: str = ""
    owner: str = "System Agent"
    sponsor: str = "CPO"
    priority: str = "Medium"
    dependencies: List[str] = field(default_factory=list)
    status: str = "active"
    version: int = 1
    history: List[Dict[str, Any]] = field(default_factory=list)
    health_score: float = 100.0
    confidence_score: float = 100.0
    tenant_id: str = "default_tenant"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "source_type": self.source_type,
            "source_uri": self.source_uri,
            "owner": self.owner,
            "sponsor": self.sponsor,
            "priority": self.priority,
            "dependencies": self.dependencies,
            "status": self.status,
            "version": self.version,
            "history": self.history,
            "health_score": self.health_score,
            "confidence_score": self.confidence_score,
            "tenant_id": self.tenant_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Objective":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            source_type=data.get("source_type", "text"),
            source_uri=data.get("source_uri", ""),
            owner=data.get("owner", "System Agent"),
            sponsor=data.get("sponsor", "CPO"),
            priority=data.get("priority", "Medium"),
            dependencies=list(data.get("dependencies", [])),
            status=data.get("status", "active"),
            version=data.get("version", 1),
            history=list(data.get("history", [])),
            health_score=float(data.get("health_score", 100.0)),
            confidence_score=float(data.get("confidence_score", 100.0)),
            tenant_id=data.get("tenant_id", "default_tenant"),
        )
