# interfaces/rest/auth.py
import sys

from fastapi import HTTPException

from config.settings import settings

SECURE_TOKEN = settings.SECURE_TOKEN
_DEFAULT_TOKENS = {"uawos-secure-token-2026", "uawos-secure-token-change-me"}

if SECURE_TOKEN in _DEFAULT_TOKENS:
    print(
        "WARNING: Using default development SECURE_TOKEN. "
        "Set UAWOS_SECURE_TOKEN environment variable for production deployments.",
        file=sys.stderr,
    )


def decode_token_payload(token: str, secret_key: str) -> dict:
    """Decodes JWT claims after cryptographically verifying the HMAC-SHA256 signature."""
    import base64
    import hashlib
    import hmac
    import json

    try:
        parts = token.split(".")
        if len(parts) == 3:
            header, payload_b64, signature = parts

            # Recreate signature payload
            signing_input = f"{header}.{payload_b64}".encode()

            # Base64url decode signature
            sig_bytes = base64.urlsafe_b64decode(signature + "=" * ((4 - len(signature) % 4) % 4))

            # Compute expected signature
            expected_sig = hmac.new(secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()

            # Cryptographically compare signatures to prevent timing attacks
            if hmac.compare_digest(sig_bytes, expected_sig):
                payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
                payload_json = base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8")
                return json.loads(payload_json)
    except Exception:
        pass
    return {}


def verify_secure_token(x_uawos_token: str = None, authorization: str = None):
    token = x_uawos_token
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing authentication credentials.")

    is_dev_mode = (SECURE_TOKEN in _DEFAULT_TOKENS)

    if token != SECURE_TOKEN and not (is_dev_mode and token in _DEFAULT_TOKENS):
        claims = decode_token_payload(token, SECURE_TOKEN)
        if not claims:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid security token.")
