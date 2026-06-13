import os
import sys
import tempfile
from unittest.mock import patch

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import uawos_state_utils

def test_local_json_fallback_on_db_offline():
    # 1. Create a temporary path for the state file
    with tempfile.TemporaryDirectory() as tmpdir:
        state_path = os.path.join(tmpdir, "test_state.json")
        default_data = {"score": 100}
        
        # 2. Mock uawos_db.DB_AVAILABLE as False to force fallback
        with patch("uawos_db.DB_AVAILABLE", False):
            # Save state
            uawos_state_utils.save_state(state_path, default_data)
            
            # Verify the file was written locally
            assert os.path.exists(state_path)
            
            # Load state
            loaded = uawos_state_utils.load_state(state_path, lambda: {"score": 0})
            assert loaded == default_data

if __name__ == "__main__":
    test_local_json_fallback_on_db_offline()
    print("Local JSON state fallback tests passed successfully!")
