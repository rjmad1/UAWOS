import json
import urllib.request


def test_fga():
    try:
        url = "http://127.0.0.1:8083/stores"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("Stores:", data)
    except Exception as e:
        print("Failed to query OpenFGA:", e)


if __name__ == "__main__":
    test_fga()
