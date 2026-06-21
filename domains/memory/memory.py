# domains/memory/memory.py
from dataclasses import dataclass


@dataclass
class MemoryEntry:
    index: int
    timestamp: int
    content: str
    scope: str = "workspace"  # workspace, organizational
    owner: str = "system"
    status: str = "active"  # active, archived
    original_content: str | None = None
    curated_timestamp: int | None = None

    def to_dict(self) -> dict:
        data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "content": self.content,
            "scope": self.scope,
            "owner": self.owner,
            "status": self.status,
        }
        if self.original_content is not None:
            data["original_content"] = self.original_content
        if self.curated_timestamp is not None:
            data["curated_timestamp"] = self.curated_timestamp
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        return cls(
            index=int(data["index"]),
            timestamp=int(data["timestamp"]),
            content=data["content"],
            scope=data.get("scope", "workspace"),
            owner=data.get("owner", "system"),
            status=data.get("status", "active"),
            original_content=data.get("original_content"),
            curated_timestamp=data.get("curated_timestamp"),
        )
