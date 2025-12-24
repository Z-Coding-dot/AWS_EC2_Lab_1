import socket
import json
import time

HOST = "0.0.0.0"
PORT = 5000

def add(a, b):
    return a + b

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("RPC Server running on port 5000")

while True:
    conn, addr = server.accept()
    data = conn.recv(1024)

    if not data:
        conn.close()
        continue

    request = json.loads(data.decode())

    # Failure simulation (REQUIRED)
    time.sleep(5)

    result = add(request["params"]["a"], request["params"]["b"])

    response = {
        "request_id": request["request_id"],
        "result": result,
        "status": "OK"
    }

    conn.send(json.dumps(response).encode())
    conn.close()
