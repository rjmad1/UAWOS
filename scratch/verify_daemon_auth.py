import base64
import hashlib
import hmac
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import uawos_dashboard_daemon

# Set secret key
secret = uawos_dashboard_daemon.SECURE_TOKEN

# 1. Create a validly signed token
header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
payload = base64.urlsafe_b64encode(json.dumps({"role": "Admin", "owner": "test"}).encode()).decode().rstrip("=")
message = f"{header}.{payload}"
sig = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
signature = base64.urlsafe_b64encode(sig).decode().rstrip("=")
valid_token = f"{message}.{signature}"

# 2. Create an unsigned/fabricated token
unsigned_token = f"{message}."

# 3. Test verification
claims_valid = uawos_dashboard_daemon.decode_token_payload(valid_token, secret)
assert claims_valid.get("role") == "Admin", "Failed to decode validly signed token"

claims_invalid = uawos_dashboard_daemon.decode_token_payload(unsigned_token, secret)
assert not claims_invalid, "Incorrectly accepted unsigned token!"

print("JWT authentication verification tests passed successfully!")
