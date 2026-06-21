import os
import sys
import traceback
from unittest.mock import MagicMock, patch

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import uawos_governance


def test_opa_policy_drift_recovery():
    # 1. Reset state
    uawos_governance._policy_uploaded = False

    # Custom mock for urlopen
    call_index = 0

    def mock_urlopen(req, *args, **kwargs):
        nonlocal call_index
        call_index += 1
        print(f"\n[Mock urlopen] Call #{call_index} to: {req.full_url} ({req.get_method()})")

        if call_index == 1:
            resp = MagicMock()
            resp.status = 200
            resp.__enter__.return_value = resp
            return resp
        elif call_index == 2:
            resp = MagicMock()
            resp.status = 200
            resp.__enter__.return_value = resp
            resp.read.return_value = b'{"result": {"allow": true, "reason": "Passed"}}'
            return resp
        elif call_index == 3:
            resp = MagicMock()
            resp.status = 200
            resp.__enter__.return_value = resp
            resp.read.return_value = b'{"result": {}}'
            return resp
        elif call_index == 4:
            resp = MagicMock()
            resp.status = 200
            resp.__enter__.return_value = resp
            return resp
        elif call_index == 5:
            resp = MagicMock()
            resp.status = 200
            resp.__enter__.return_value = resp
            resp.read.return_value = b'{"result": {"allow": false, "reason": "Failed"}}'
            return resp

        raise RuntimeError("Unexpected call to urlopen")

    try:
        with patch("urllib.request.urlopen", side_effect=mock_urlopen):
            print("\n--- Running Test Step 1 (Normal Execution) ---")
            res = uawos_governance.evaluate_via_opa({"action": "test"})
            print("Result 1:", res)
            assert res is not None, "Normal execution returned None"
            assert res["verdict"] == "APPROVED"
            assert uawos_governance._policy_uploaded is True
            assert call_index == 2

            print("\n--- Running Test Step 2 (Restart/Empty Result) ---")
            res = uawos_governance.evaluate_via_opa({"action": "test"})
            print("Result 2:", res)
            assert res is None, "Expected None result after OPA restart"
            assert uawos_governance._policy_uploaded is False
            assert call_index == 3

            print("\n--- Running Test Step 3 (Re-upload/Evaluation) ---")
            res = uawos_governance.evaluate_via_opa({"action": "test"})
            print("Result 3:", res)
            assert res is not None
            assert res["verdict"] == "REJECTED"
            assert uawos_governance._policy_uploaded is True
            assert call_index == 5

            print("\nOPA policy cache drift recovery test passed successfully!")
    except Exception:
        print("\nTest failed with exception:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_opa_policy_drift_recovery()
