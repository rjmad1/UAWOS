# shared/constants/__init__.py

# HTTP Media Types
APPLICATION_JSON = "application/json"
TEXT_HTML_UTF8 = "text/html; charset=utf-8"

# System Components
QDRANT_VECTOR_DB = "Qdrant Vector DB"
MARQUEZ_LINEAGE = "Marquez Lineage"
APACHE_SUPERSET = "Apache Superset"
DEP_TRACK_API = "Dependency-Track API"

# Priorities
PRIORITY_CRITICAL = "Critical"
PRIORITY_HIGH = "High"
PRIORITY_MEDIUM = "Medium"
PRIORITY_LOW = "Low"

VALID_PRIORITIES = {PRIORITY_CRITICAL, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW}

# Objectives/Actions statuses
STATUS_ACTIVE = "active"
STATUS_PAUSED = "paused"
STATUS_ARCHIVED = "archived"
STATUS_CANCELLED = "cancelled"
STATUS_DRAFT = "draft"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"

VALID_STATUSES = {
    STATUS_ACTIVE,
    STATUS_PAUSED,
    STATUS_ARCHIVED,
    STATUS_CANCELLED,
    STATUS_DRAFT,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_APPROVED,
    STATUS_REJECTED,
}
