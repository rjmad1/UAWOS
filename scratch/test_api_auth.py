import urllib.error
import urllib.request

print("Testing API Auth on daemon...")

# Test without token
req = urllib.request.Request(
    "http://127.0.0.1:8099/api/requirement/submit",
    method="POST",
    data=b"{}",
    headers={"Content-Type": "application/json"},
)
try:
    urllib.request.urlopen(req)
    print("FAIL: Request without token was NOT blocked!")
except urllib.error.HTTPError as e:
    print(f"PASS: Request without token blocked with code {e.code}")

# Test with token
req_secure = urllib.request.Request(
    "http://127.0.0.1:8099/api/requirement/submit",
    method="POST",
    data=b"{}",
    headers={
        "X-UAWOS-Token": "uawos-secure-token-2026",
        "Content-Type": "application/json",
    },
)
try:
    resp = urllib.request.urlopen(req_secure)
    print(f"PASS: Request with token accepted with status {resp.status}")
except urllib.error.HTTPError as e:
    print(f"FAILED: Request with token was blocked: {e.code} - {e.read().decode('utf-8')}")
