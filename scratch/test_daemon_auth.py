import os
import sys

# Add current directory to path so we can import the daemon
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

from uawos_dashboard_daemon import app

client = TestClient(app)

print("Running FastAPI Token Authentication Verification...")

endpoints = [
    ("/api/requirement/submit", "POST", {}),
    (
        "/api/objective/submit",
        "POST",
        {"title": "Test Obj", "category": "development", "owner": "Admin"},
    ),
    (
        "/api/budget/action",
        "POST",
        {"action": "allocate", "amount": 1000, "reason": "Test"},
    ),
    ("/api/objective/action", "POST", {"action_id": "ACT-101", "decision": "approve"}),
]

success = True

for path, method, payload in endpoints:
    print(f"\nTesting route: {path}")

    # 1. Test without token
    if method == "POST":
        response = client.post(path, json=payload)
    else:
        response = client.get(path)

    if response.status_code == 401:
        print("  [PASS] Blocked request without token (401 Unauthorized)")
    else:
        print(f"  [FAIL] Did not block request without token! Got status code {response.status_code}")
        success = False

    # 2. Test with invalid token
    if method == "POST":
        response = client.post(path, json=payload, headers={"X-UAWOS-Token": "bad-token"})
    else:
        response = client.get(path, headers={"X-UAWOS-Token": "bad-token"})

    if response.status_code == 401:
        print("  [PASS] Blocked request with invalid token (401 Unauthorized)")
    else:
        print(f"  [FAIL] Did not block request with invalid token! Got status code {response.status_code}")
        success = False

    # 3. Test with valid token
    if method == "POST":
        response = client.post(path, json=payload, headers={"X-UAWOS-Token": "uawos-secure-token-2026"})
    else:
        response = client.get(path, headers={"X-UAWOS-Token": "uawos-secure-token-2026"})

    if response.status_code != 401:
        print(f"  [PASS] Accepted request with valid token (Status: {response.status_code})")
    else:
        print(f"  [FAIL] Blocked request with valid token! Got status code {response.status_code}")
        success = False

if success:
    print("\nAll API token authorization tests PASSED successfully!")
    sys.exit(0)
else:
    print("\nSome API token authorization tests FAILED!")
    sys.exit(1)
