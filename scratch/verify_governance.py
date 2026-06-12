import json
import os
import sys
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOVERNANCE_DIR = os.path.join(BASE_DIR, "governance")

REGISTRY_FILES = [
    "TEST_INTELLIGENCE_REGISTRY.md",
    "BLAST_RADIUS_REGISTRY.md",
    "ARCHITECTURE_RISK_REGISTER.md",
    "ENGINEERING_DEBT_REGISTER.md",
    "SERVICE_HEALTH_REGISTRY.md",
    "DEPENDENCY_RISK_REGISTER.md",
    "INCIDENT_LEARNING_REGISTRY.md",
    "PLATFORM_GOVERNANCE_REPORT.md",
]


def verify_files():
    print("--- Verifying Governance Registries ---")
    if not os.path.exists(GOVERNANCE_DIR):
        print(f"Error: Governance directory {GOVERNANCE_DIR} does not exist.")
        return False

    missing = []
    for f in REGISTRY_FILES:
        path = os.path.join(GOVERNANCE_DIR, f)
        if not os.path.exists(path):
            missing.append(f)
        else:
            size = os.path.getsize(path)
            print(f"  [OK] {f} (size: {size} bytes)")

    if missing:
        print(f"Error: The following registries are missing: {missing}")
        return False

    print("All 8 registries verified on disk.\n")
    return True


def verify_api():
    print("--- Verifying Governance daemon API endpoints ---")
    url = "http://127.0.0.1:8099/api/governance/status"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                print(f"Error: Received status code {response.status} from API.")
                return False
            data = json.loads(response.read().decode("utf-8"))
            print("  [OK] /api/governance/status returned HTTP 200")

            # Verify keys in JSON
            required_keys = [
                "platform",
                "timestamp",
                "metrics",
                "blast_radius",
                "test_confidence",
                "reliability_forecast",
                "warnings",
                "decisions",
            ]
            missing_keys = [k for k in required_keys if k not in data]
            if missing_keys:
                print(f"Error: API response is missing keys: {missing_keys}")
                return False

            print("  [OK] All core schema properties validated.")
            print(f"    Confidence Score   : {data['metrics'].get('platform_confidence_score')}/100")
            print(f"    Future Risk Score  : {data['metrics'].get('future_risk_score')}/100")
            print(f"    Readiness Score    : {data['metrics'].get('operational_readiness_score')}/100")
            print(f"    Stability Trend    : {data['metrics'].get('predicted_stability_trend')}")
            print(f"    Warnings Count     : {len(data.get('warnings', []))}")
            print(f"    Decisions Count    : {len(data.get('decisions', []))}")
            return True
    except Exception as e:
        print(f"Error: Could not connect to daemon API on port 8099. Is it running? Details: {e}")
        return False


def verify_engine():
    print("--- Verifying Proactive Governance Engine execution ---")
    try:
        sys.path.append(BASE_DIR)
        import uawos_proactive_governance

        report = uawos_proactive_governance.run_full_governance_audit()
        if report and "metrics" in report:
            print("  [OK] uawos_proactive_governance engine ran successfully and produced report dict.")
            return True
        else:
            print("Error: Engine returned empty or invalid report.")
            return False
    except Exception as e:
        print(f"Error executing governance engine: {e}")
        return False


if __name__ == "__main__":
    print("Running Proactive Platform Governance System (PPGS) Validation Tests\n")
    success = True

    # Check engine first
    if not verify_engine():
        success = False

    # Check registries on disk
    if not verify_files():
        success = False

    # Check API endpoints (requires daemon to be running)
    if not verify_api():
        print("\nWARNING: API verification failed. Make sure the daemon is running and try again.")
        success = False

    if success:
        print("\nALL GOVERNANCE TESTS PASSED SUCCESSFULLY.")
        sys.exit(0)
    else:
        print("\nGOVERNANCE VERIFICATION FAILED.")
        sys.exit(1)
