# ==============================================================================
# Stage 1: Build dependencies
# ==============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install only core runtime dependencies for the BFF daemon
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install \
    fastapi uvicorn psycopg2-binary qdrant-client networkx

# ==============================================================================
# Stage 2: Production runtime
# ==============================================================================
FROM python:3.11-slim AS runtime

LABEL maintainer="UAWOS Team"
LABEL description="UAWOS Dashboard Daemon — BFF API Server"
LABEL org.opencontainers.image.source="https://github.com/rjmad1/UAWOS"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Create non-root user for security
RUN groupadd --gid 1000 uawos && \
    useradd --uid 1000 --gid uawos --shell /bin/bash --create-home uawos

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source code
COPY uawos_*.py ./
COPY uawos_dashboard.html uawos_delivery.html uawos_roadmap.html \
     uawos_requirement_studio.html uawos_architecture.html ./

# Copy requirements and supporting files
COPY requirements.txt pyproject.toml ./
COPY Requirements\ Master/ ./Requirements\ Master/

# Set ownership
RUN chown -R uawos:uawos /app

# Switch to non-root user
USER uawos

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8099/api/status')" || exit 1

EXPOSE 8099

# Environment defaults (overridable at runtime)
ENV POSTGRES_HOST=postgres \
    POSTGRES_PORT=5432 \
    QDRANT_HOST=qdrant \
    QDRANT_PORT=6333 \
    PYTHONUNBUFFERED=1

CMD ["python", "uawos_dashboard_daemon.py"]
