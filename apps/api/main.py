# apps/api/main.py
import os
import threading

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from config.settings import settings
from interfaces.rest.auth import SECURE_TOKEN, decode_token_payload
from interfaces.rest.billing import router as billing_router
from interfaces.rest.dtase import router as dtase_router
from interfaces.rest.governance import router as governance_router
from interfaces.rest.objectives import router as objectives_router
from interfaces.rest.requirements import router as requirements_router
from interfaces.rest.system import daemon_loop
from interfaces.rest.system import router as system_router
from interfaces.rest.meeting import router as meeting_router
from shared.utilities.context import reset_context, set_context

# HTML paths
WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")
HTML_FILE = os.path.join(WEB_DIR, "uawos_dashboard.html")
DELIVERY_FILE = os.path.join(WEB_DIR, "uawos_delivery.html")
ROADMAP_FILE = os.path.join(WEB_DIR, "uawos_roadmap.html")
REQUIREMENT_STUDIO_FILE = os.path.join(WEB_DIR, "uawos_requirement_studio.html")
ARCHITECTURE_FILE = os.path.join(WEB_DIR, "uawos_architecture.html")

app = FastAPI(title="UAWOS Operational Control Plane Daemon", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def tenant_context_middleware(request: Request, call_next):
    token = request.headers.get("x-uawos-token")
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]

    # Defaults
    tenant_id = "default_tenant"
    role = "Developer"
    owner = "system"

    # Decode if present
    if token:
        if token == SECURE_TOKEN:
            tenant_id = "default_tenant"
            role = "Admin"
            owner = "admin_user"
        else:
            claims = decode_token_payload(token, SECURE_TOKEN)
            if claims:
                tenant_id = claims.get("tenant_id", "default_tenant")
                role = claims.get("role", "Developer")
                owner = claims.get("owner") or claims.get("username") or claims.get("sub", "system")

    tokens = set_context(tenant_id, role, owner)
    try:
        response = await call_next(request)
        return response
    finally:
        reset_context(tokens)


# Include REST routers
app.include_router(objectives_router)
app.include_router(requirements_router)
app.include_router(billing_router)
app.include_router(governance_router)
app.include_router(dtase_router)
app.include_router(system_router)
app.include_router(meeting_router)


# HTML routers
@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def serve_dashboard():
    try:
        with open(HTML_FILE, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard UI file not found.")


@app.get("/operations", response_class=HTMLResponse)
@app.get("/operations_dashboard.html", response_class=HTMLResponse)
def serve_operations_dashboard():
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ops_file = os.path.join(root_dir, "operations_dashboard.html")
        with open(ops_file, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Operations Dashboard file not found.")

@app.get("/delivery", response_class=HTMLResponse)
@app.get("/delivery.html", response_class=HTMLResponse)
def serve_delivery():
    try:
        with open(DELIVERY_FILE, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Delivery UI file not found.")


@app.get("/roadmap", response_class=HTMLResponse)
@app.get("/roadmap.html", response_class=HTMLResponse)
def serve_roadmap():
    try:
        with open(ROADMAP_FILE, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Roadmap UI file not found.")


@app.get("/requirement_studio", response_class=HTMLResponse)
@app.get("/requirement_studio.html", response_class=HTMLResponse)
def serve_requirement_studio():
    try:
        with open(REQUIREMENT_STUDIO_FILE, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Requirement Studio UI file not found.")


@app.get("/architecture", response_class=HTMLResponse)
@app.get("/architecture.html", response_class=HTMLResponse)
def serve_architecture():
    try:
        with open(ARCHITECTURE_FILE, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Architecture UI file not found.")


def start_server():
    print(f"Starting server on http://0.0.0.0:{settings.PORT}")
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT, log_level="warning")
    return 0


if __name__ == "__main__":
    # Start the daemon monitoring thread
    t = threading.Thread(target=daemon_loop, daemon=True)
    t.start()

    # Start the web server
    start_server()
