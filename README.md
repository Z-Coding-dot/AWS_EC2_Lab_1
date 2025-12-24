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
