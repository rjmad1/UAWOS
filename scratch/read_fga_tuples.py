import urllib.request
import json

def read_tuples():
    store_id = "01KTVDAXGM5B6HP47FARBW6383"
    try:
        url = f"http://127.0.0.1:8083/stores/{store_id}/read"
        # Reading all tuples
        req = urllib.request.Request(
            url,
            data=json.dumps({}).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print("Tuples in store:")
            for t in data.get("tuples", []):
                print(" ", t.get("key"))
    except Exception as e:
        print("Failed to read tuples:", e)

if __name__ == "__main__":
    read_tuples()
