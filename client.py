import socket
import json
import uuid

SERVER_IP = "54.82.55.139"
PORT = 5000
TIMEOUT = 2
RETRIES = 3

request = {
    "request_id": str(uuid.uuid4()),
    "method": "add",
    "params": {"a": 10, "b": 20}
}

for attempt in range(RETRIES):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect((SERVER_IP, PORT))
        s.send(json.dumps(request).encode())

        response = json.loads(s.recv(1024).decode())
        print("RPC Response:", response)
        s.close()
        break

    except socket.timeout:
        print(f"Timeout occurred, retry {attempt + 1}")
