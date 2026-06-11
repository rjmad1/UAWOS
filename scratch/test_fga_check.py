import urllib.request
import json
import sys

def run():
    store_id = "01KTVDAXGM5B6HP47FARBW6383"
    model_id = "01KTVDAXH09W9ZRDPYGYY9K97B"
    
    # 1. Write relation tuples
    # user:Alice is member of role:CEO
    # role:CEO#member is permitted on action_category:budget
    write_url = f"http://127.0.0.1:8083/stores/{store_id}/write"
    
    tuples = [
        {
            "user": "user:Alice",
            "relation": "member",
            "object": "role:CEO"
        },
        {
            "user": "role:CEO#member",
            "relation": "permitted",
            "object": "action_category:budget"
        }
    ]
    
    # Write request payload
    payload = {
        "writes": {
            "tuple_keys": tuples
        },
        "authorization_model_id": model_id
    }
    
    try:
        req = urllib.request.Request(
            write_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            print("Write response:", json.loads(resp.read().decode('utf-8')))
            
        # 2. Check if Alice is permitted on action_category:budget
        check_url = f"http://127.0.0.1:8083/stores/{store_id}/check"
        check_payload = {
            "tuple_key": {
                "user": "user:Alice",
                "relation": "permitted",
                "object": "action_category:budget"
            },
            "authorization_model_id": model_id
        }
        req_check = urllib.request.Request(
            check_url,
            data=json.dumps(check_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_check, timeout=1.0) as resp:
            check_res = json.loads(resp.read().decode('utf-8'))
            print("Check Alice on budget:", check_res)
            
        # 3. Check if Bob is permitted on action_category:budget (should be False)
        check_payload_bob = {
            "tuple_key": {
                "user": "user:Bob",
                "relation": "permitted",
                "object": "action_category:budget"
            },
            "authorization_model_id": model_id
        }
        req_check_bob = urllib.request.Request(
            check_url,
            data=json.dumps(check_payload_bob).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_check_bob, timeout=1.0) as resp:
            check_res_bob = json.loads(resp.read().decode('utf-8'))
            print("Check Bob on budget:", check_res_bob)

    except urllib.error.HTTPError as he:
        print("HTTP Error:", he.code, he.read().decode('utf-8'))
    except Exception as e:
        print("Failed:", e)

if __name__ == "__main__":
    run()
