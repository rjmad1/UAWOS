# scratch/test_api.py
import urllib.request
import json

url = "http://127.0.0.1:8099/api/dtase/analyze"
data = {
    "text": "I worked 12 hours overtime this week on the product launch, but my supervisor denied my overtime compensation claim and threatened that if I escalated it to HR, I would be terminated immediately. This is totally illegal and violating my contract."
}

payload = json.dumps(data).encode("utf-8")
req = urllib.request.Request(
    url,
    data=payload,
    headers={"Content-Type": "application/json"}
)

try:
    print("Sending POST request to dashboard daemon DTASE API...")
    with urllib.request.urlopen(req, timeout=15.0) as response:
        res_data = json.loads(response.read().decode())
        print("Response received successfully!")
        print(json.dumps(res_data, indent=2)[:500] + "...")
except Exception as e:
    print(f"Error during API call: {e}")
