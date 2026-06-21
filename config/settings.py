# config/settings.py
import os

# Load local .env file variables if present (bootstrap env)
_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(_env_path):
    with open(_env_path, encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                _k = _k.strip()
                _v = _v.strip()
                if _v.startswith(('"', "'")) and _v.endswith(('"', "'")):
                    _v = _v[1:-1]
                if _k not in os.environ:
                    os.environ[_k] = _v

class Settings:
    # Service Port
    PORT: int = int(os.environ.get("PORT", 8099))
    
    # Secure token
    SECURE_TOKEN: str = os.environ.get("UAWOS_SECURE_TOKEN", "uawos-secure-token-change-me")
    
    # Relational Database
    POSTGRES_HOST: str = os.environ.get("POSTGRES_HOST", "127.0.0.1")
    POSTGRES_PORT: int = int(os.environ.get("POSTGRES_PORT", 5435))
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "marquez")
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "marquez")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "marquez")
    
    @property
    def POSTGRES_CONN_STR(self) -> str:
        return os.environ.get(
            "POSTGRES_CONN_STR",
            f"host={self.POSTGRES_HOST} port={self.POSTGRES_PORT} dbname={self.POSTGRES_DB} user={self.POSTGRES_USER} password={self.POSTGRES_PASSWORD}"
        )
        
    # Vector Database
    QDRANT_HOST: str = os.environ.get("QDRANT_HOST", "127.0.0.1")
    QDRANT_PORT: int = int(os.environ.get("QDRANT_PORT", 6333))
    
    # Model Gateways
    OLLAMA_HOST: str = os.environ.get("OLLAMA_HOST", "127.0.0.1")
    OLLAMA_PORT: int = int(os.environ.get("OLLAMA_PORT", 11434))
    
    @property
    def OLLAMA_BASE_URL(self) -> str:
        return os.environ.get("OLLAMA_BASE_URL", f"http://{self.OLLAMA_HOST}:{self.OLLAMA_PORT}")
        
    WEAVEROUTER_BASE_URL: str = os.environ.get("WEAVEROUTER_BASE_URL", "http://127.0.0.1:8092")
    WEAVEROUTER_API_KEY: str = os.environ.get("WEAVEROUTER_API_KEY", "rk_uawos_dev_key")
    
    # Security Sandbox and Governance
    OPA_HOST: str = os.environ.get("OPA_HOST", "127.0.0.1")
    OPA_PORT: int = int(os.environ.get("OPA_PORT", 8181))
    
    @property
    def OPA_URL(self) -> str:
        return f"http://{self.OPA_HOST}:{self.OPA_PORT}"
        
    OPENFGA_HOST: str = os.environ.get("OPENFGA_HOST", "127.0.0.1")
    OPENFGA_PORT: int = int(os.environ.get("OPENFGA_PORT", 8083))
    
    @property
    def OPENFGA_URL(self) -> str:
        return f"http://{self.OPENFGA_HOST}:{self.OPENFGA_PORT}"
        
    SANDBOX_HOST: str = os.environ.get("SANDBOX_HOST", "127.0.0.1")
    SANDBOX_PORT: int = int(os.environ.get("SANDBOX_PORT", 5001))
    
    @property
    def MOCK_SERVICES_BASE_URL(self) -> str:
        return f"http://{self.SANDBOX_HOST}:{self.SANDBOX_PORT}"
        
    # Observability & Lineage
    MARQUEZ_HOST: str = os.environ.get("MARQUEZ_HOST", "127.0.0.1")
    MARQUEZ_PORT: int = int(os.environ.get("MARQUEZ_PORT", 5000))
    
    SUPERSET_HOST: str = os.environ.get("SUPERSET_HOST", "127.0.0.1")
    SUPERSET_PORT: int = int(os.environ.get("SUPERSET_PORT", 8088))
    
    DTRACK_HOST: str = os.environ.get("DTRACK_HOST", "127.0.0.1")
    DTRACK_PORT: int = int(os.environ.get("DTRACK_PORT", 8081))
    
    DTRACK_UI_HOST: str = os.environ.get("DTRACK_UI_HOST", "127.0.0.1")
    DTRACK_UI_PORT: int = int(os.environ.get("DTRACK_UI_PORT", 8085))
    
    OPENMETADATA_HOST: str = os.environ.get("OPENMETADATA_HOST", "127.0.0.1")
    OPENMETADATA_PORT: int = int(os.environ.get("OPENMETADATA_PORT", 8585))
    
    CLICKHOUSE_HOST: str = os.environ.get("CLICKHOUSE_HOST", "127.0.0.1")
    CLICKHOUSE_PORT: int = int(os.environ.get("CLICKHOUSE_PORT", 8123))
    
    TELEMETRY_HOST: str = os.environ.get("TELEMETRY_HOST", "127.0.0.1")
    TELEMETRY_PORT: int = int(os.environ.get("TELEMETRY_PORT", 3000))
    
    ALARM_HOST: str = os.environ.get("ALARM_HOST", "127.0.0.1")
    ALARM_PORT: int = int(os.environ.get("ALARM_PORT", 9093))
    
    NEO4J_HOST: str = os.environ.get("NEO4J_HOST", "127.0.0.1")
    NEO4J_PORT_1: int = int(os.environ.get("NEO4J_PORT_1", 7687))
    NEO4J_PORT_2: int = int(os.environ.get("NEO4J_PORT_2", 7474))

    # State Directory Configuration
    STATE_DIR: str = os.environ.get("UAWOS_STATE_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

settings = Settings()
