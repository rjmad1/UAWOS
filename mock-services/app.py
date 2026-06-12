import socket
import threading
import time


def listen_on_port(port, name):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", port))
        server.listen(5)
        print(f"Mock service '{name}' listening on port {port}")
        while True:
            client, addr = server.accept()
            try:
                client.recv(1024)
                response = f'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{{"status":"healthy","mock":"{name}"}}\n'
                client.sendall(response.encode("utf-8"))
            except Exception as client_err:
                print(f"Client socket error on port {port}: {client_err}")
            finally:
                client.close()
    except Exception as e:
        print(f"Error on port {port} ({name}): {e}")


services = [
    (8585, "OpenMetadata Catalog"),
    (3000, "Langfuse Telemetry"),
    (9093, "Alertmanager Operational Alarms"),
    (5001, "OpenHands Sandbox"),
]

threads = []
for port, name in services:
    t = threading.Thread(target=listen_on_port, args=(port, name), daemon=True)
    t.start()
    threads.append(t)

print("All mock services started. Keeping container alive...")
while True:
    time.sleep(1)
