# domains/action/action.py
from dataclasses import dataclass, field


@dataclass
class Action:
    id: str
    workflow_id: str
    name: str
    owner: str = "Unassigned"
    dependencies: list[str] = field(default_factory=list)
    priority: str = "Medium"
    budget: float = 0.0
    deadline: int = 0
    status: str = "pending"  # pending, completed, failed
    approval_required: bool = False
    executed_command: str = None
    sandbox_env: str = None
    error: str = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "name": self.name,
            "owner": self.owner,
            "dependencies": self.dependencies,
            "priority": self.priority,
            "budget": self.budget,
            "deadline": self.deadline,
            "status": self.status,
            "approval_required": self.approval_required,
            "executed_command": self.executed_command,
            "sandbox_env": self.sandbox_env,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Action":
        return cls(
            id=data["id"],
            workflow_id=data.get("workflow_id", ""),
            name=data["name"],
            owner=data.get("owner", "Unassigned"),
            dependencies=list(data.get("dependencies", [])),
            priority=data.get("priority", "Medium"),
            budget=float(data.get("budget", 0.0)),
            deadline=int(data.get("deadline", 0)),
            status=data.get("status", "pending"),
            approval_required=bool(data.get("approval_required", False)),
            executed_command=data.get("executed_command"),
            sandbox_env=data.get("sandbox_env"),
            error=data.get("error"),
        )

    def validate_command_security(self, command: str) -> tuple[bool, str]:
        """Validate command for security (check dangerous characters or commands)."""
        dangerous_keywords = ["rm", "mv", "chmod", "chown", "sudo", "wget", "curl"]
        dangerous_chars = [";", "&&", "||", "|", "`", "$", ".."]

        for kw in dangerous_keywords:
            if kw in command.split() or command.startswith(kw + " "):
                return False, f"Forbidden command/keyword: '{kw}'"

        for char in dangerous_chars:
            if char in command:
                return False, f"Forbidden shell operator/character: '{char}'"

        return True, ""
