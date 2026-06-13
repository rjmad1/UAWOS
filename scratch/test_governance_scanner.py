import os
import sys
import tempfile
import shutil

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import uawos_proactive_governance

def test_scanner_excludes_self_matches():
    # 1. Initialize scanner on the root directory
    scanner = uawos_proactive_governance.CodeRiskScanner(project_root)
    scanner.scan()
    
    # 2. Check if the scanner file is in python_files and check its TODOs
    assert "uawos_proactive_governance.py" in scanner.python_files
    
    # Get all todos found in uawos_proactive_governance.py
    self_todos = [t for t in scanner.todos if t["file"] == "uawos_proactive_governance.py"]
    
    # Assert that no implementation details are listed as TODO
    for t in self_todos:
        text = t["text"]
        # Ensure we didn't match the scanner's own code patterns
        assert "Scan for TODOs" not in text
        assert "Warning 2: TODO Accumulation" not in text
        assert "active TODO/FIXME lines" not in text
        assert "block merging critical TODO" not in text
        assert "derived from TODOs" not in text
        assert "Active TODOs and FIXMEs" not in text

def test_scanner_detects_real_todos():
    # 1. Create a temp directory with a test file containing a real TODO
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "uawos_dummy.py")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("# TODO: This is a real developer task\n")
            f.write("print('hello')\n")
            
        scanner = uawos_proactive_governance.CodeRiskScanner(tmpdir)
        scanner.scan()
        
        dummy_todos = [t for t in scanner.todos if t["file"] == "uawos_dummy.py"]
        assert len(dummy_todos) == 1
        assert "This is a real developer task" in dummy_todos[0]["text"]

if __name__ == "__main__":
    test_scanner_excludes_self_matches()
    test_scanner_detects_real_todos()
    print("Governance scanner TODO self-match tests passed successfully!")
