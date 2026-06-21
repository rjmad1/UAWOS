#!/usr/bin/env python3
"""
UAWOS Dashboard Daemon
======================
Consolidated Control Plane launcher and BFF runner.
Proxies all REST API endpoints to the single authoritative router in apps/api/main.py,
eliminating duplicated route logic while preserving startup and test-client compatibility.
"""

import os
import sys
import threading

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apps.api.main import app, start_server  # noqa: F401
from config.settings import settings
from interfaces.rest.auth import SECURE_TOKEN, decode_token_payload  # noqa: F401
from interfaces.rest.system import daemon_loop, run_health_checks  # noqa: F401

# Ports and configurations for compatibility
PORT = settings.PORT

if __name__ == "__main__":
    print("Starting consolidated UAWOS Control Plane...")

    # Start the daemon monitoring thread
    t = threading.Thread(target=daemon_loop, daemon=True)
    t.start()

    # Start the web server
    sys.exit(start_server())
