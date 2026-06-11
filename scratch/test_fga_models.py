import urllib.request
import json

def test_models():
    store_id = "01KTVDAXGM5B6HP47FARBW6383"
    try:
        url = f"http://127.0.0.1:8083/stores/{store_id}/authorization-models"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print("Models:", data)
    except Exception as e:
        print("Failed to query models:", e)

if __name__ == "__main__":
    test_models()
