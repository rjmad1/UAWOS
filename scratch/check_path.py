# scratch/check_path.py
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apps.api.main import WEB_DIR

print("WEB_DIR:", WEB_DIR)
print("WEB_DIR exists:", os.path.exists(WEB_DIR))
assets_dir = os.path.join(WEB_DIR, "assets")
print("assets_dir:", assets_dir)
print("assets_dir exists:", os.path.exists(assets_dir))
if os.path.exists(assets_dir):
    print("Files in assets_dir:")
    for f in os.listdir(assets_dir):
        print(" -", f)
else:
    print("assets_dir does not exist!")
