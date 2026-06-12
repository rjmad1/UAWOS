import json
import urllib.request


def run():
    # 1. Create store if it doesn't exist
    try:
        url = "http://127.0.0.1:8083/stores"
        # Get existing stores
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            stores = data.get("stores", [])

        store_id = None
        for s in stores:
            if s.get("name") == "uawos":
                store_id = s.get("id")
                break

        if not store_id:
            print("Creating store 'uawos'...")
            req = urllib.request.Request(
                url,
                data=json.dumps({"name": "uawos"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                store_id = res.get("id")
                print("Store created:", store_id)
        else:
            print("Store 'uawos' already exists with ID:", store_id)

        # 2. Write authorization model
        model_url = f"http://127.0.0.1:8083/stores/{store_id}/authorization-models"

        # Define the authorization model
        auth_model = {
            "schema_version": "1.1",
            "type_definitions": [
                {"type": "user"},
                {
                    "type": "role",
                    "relations": {"member": {"this": {}}},
                    "metadata": {"relations": {"member": {"directly_related_user_types": [{"type": "user"}]}}},
                },
                {
                    "type": "action_category",
                    "relations": {"permitted": {"this": {}}},
                    "metadata": {
                        "relations": {
                            "permitted": {
                                "directly_related_user_types": [
                                    {"type": "user"},
                                    {"type": "role", "relation": "member"},
                                ]
                            }
                        }
                    },
                },
            ],
        }

        req_model = urllib.request.Request(
            model_url,
            data=json.dumps(auth_model).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_model, timeout=1.0) as resp:
            res_model = json.loads(resp.read().decode("utf-8"))
            print("Authorization model written:", res_model)

    except urllib.error.HTTPError as he:
        print("HTTP Error:", he.code, he.read().decode("utf-8"))
    except Exception as e:
        print("Failed:", e)


if __name__ == "__main__":
    run()
