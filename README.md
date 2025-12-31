# Lab 1 – RPC Implementation on AWS EC2

## Overview
This project implements a simple RPC system where a client sends requests to a server over TCP. The server executes a function and returns the result. The project demonstrates deployment on AWS EC2 and basic failure handling.

## Requirements
- Python 3.x
- Ubuntu 22.04 EC2 instances
- Port 5000 open in Security Group

## Files
- `server.py` – Server-side code
- `client.py` – Client-side code

## How to Run
1. SSH into the server instance:
   ```bash
   python3 server.py
````

2. SSH into the client instance:

   ```bash
   python3 client.py
   ```
3. Observe the output on the client terminal.

## Notes

* The client retries requests in case of server delays or failures.
* RPC message format is JSON:

  ```json
  {
    "request_id": "uuid",
    "method": "function_name",
    "params": {"key": "value"}
  }
  ```

# LAB 2 — Logical Clocks and Replication Consistency

## Overview
This project implements a distributed replicated key–value store using Lamport logical clocks across three AWS EC2 nodes.

## Features
- Lamport logical clocks
- Asynchronous replication
- Last-Writer-Wins conflict resolution
- Message delay simulation
- Node failure and recovery handling

## Files
- `node.py` — Distributed node server
- `client.py` — Client to issue PUT/GET/STATUS commands

## Requirements
- Python 3
- AWS EC2 (Ubuntu 22.04)
- Open TCP ports: 8000–8002

## Run Nodes
### Node A
```bash
python3 node.py --id A --port 8000 --peers http://IP_B:8001,http://IP_C:8002
````

### Node B

```bash
python3 node.py --id B --port 8001 --peers http://IP_A:8000,http://IP_C:8002
```

### Node C

```bash
python3 node.py --id C --port 8002 --peers http://IP_A:8000,http://IP_B:8001
```

## Test Connectivity

```bash
nc -vz IP_B 8001
nc -vz IP_C 8002
```

## Client Usage

### PUT

```bash
python3 client.py --node http://IP_A:8000 put x 10
```

### GET

```bash
python3 client.py --node http://IP_B:8001 get x
```

### STATUS

```bash
python3 client.py --node http://IP_C:8002 status
```

## Scenarios

* Scenario A: Delayed replication A → C
* Scenario B: Concurrent writes
* Scenario C: Temporary node outage

## Consistency Model

* Eventual consistency
* Last-Writer-Wins using Lamport timestamps

## Author

Ziaulhaq Parsa Karimi
