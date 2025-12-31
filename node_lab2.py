#!/usr/bin/env python3
"""
Lab 2 — 3 Nodes Distributed System
Lamport Clock + Replicated Key–Value Store (Last-Writer-Wins)
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import request, parse
import argparse
import json
import threading
import time
from typing import Dict, Any, Tuple, List

lock = threading.Lock()

LAMPORT = 0
STORE: Dict[str, Tuple[Any, int, str]] = {}
NODE_ID = ""
PEERS: List[str] = []

# Scenario A: Delay A -> C
ENABLE_DELAY = True
DELAY_RULES = {
    ("A", "C"): 2.0
}


# ---------- Lamport Clock ----------

def lamport_tick_local() -> int:
    global LAMPORT
    with lock:
        LAMPORT += 1
        return LAMPORT


def lamport_on_receive(ts: int) -> int:
    global LAMPORT
    with lock:
        LAMPORT = max(LAMPORT, ts) + 1
        return LAMPORT


def get_lamport() -> int:
    with lock:
        return LAMPORT


# ---------- Store Logic (LWW) ----------

def apply_lww(key: str, value: Any, ts: int, origin: str) -> bool:
    with lock:
        cur = STORE.get(key)
        if cur is None:
            STORE[key] = (value, ts, origin)
            return True

        _, cur_ts, cur_origin = cur
        if ts > cur_ts or (ts == cur_ts and origin > cur_origin):
            STORE[key] = (value, ts, origin)
            return True
        return False


# ---------- Replication ----------

def replicate_to_peers(key: str, value: Any, ts: int, origin: str):
    payload = json.dumps({
        "key": key,
        "value": value,
        "ts": ts,
        "origin": origin
    }).encode()

    for peer in PEERS:
        peer_id = peer.split(":")[-1]
        delay = DELAY_RULES.get((NODE_ID, peer_id), 0) if ENABLE_DELAY else 0
        if delay > 0:
            time.sleep(delay)

        try:
            req = request.Request(
                peer.rstrip("/") + "/replicate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            request.urlopen(req, timeout=2)
        except Exception as e:
            print(f"[{NODE_ID}] replication failed -> {peer}: {e}")


# ---------- HTTP Handler ----------

class Handler(BaseHTTPRequestHandler):

    def send_json(self, code: int, data: Dict[str, Any]):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/get"):
            qs = parse.parse_qs(parse.urlparse(self.path).query)
            key = qs.get("key", [""])[0]
            with lock:
                item = STORE.get(key)

            if not item:
                self.send_json(404, {"ok": False})
            else:
                value, ts, origin = item
                self.send_json(200, {
                    "ok": True,
                    "key": key,
                    "value": value,
                    "ts": ts,
                    "origin": origin,
                    "lamport": get_lamport()
                })
            return

        if self.path == "/status":
            with lock:
                snapshot = {
                    k: {"value": v, "ts": ts, "origin": o}
                    for k, (v, ts, o) in STORE.items()
                }
            self.send_json(200, {
                "node": NODE_ID,
                "lamport": get_lamport(),
                "store": snapshot
            })
            return

        if self.path == "/sync":
            with lock:
                snapshot = STORE.copy()
            self.send_json(200, {
                "lamport": get_lamport(),
                "store": {
                    k: {"value": v, "ts": ts, "origin": o}
                    for k, (v, ts, o) in snapshot.items()
                }
            })
            return

        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))

        if self.path == "/put":
            key = body["key"]
            value = body["value"]

            ts = lamport_tick_local()
            apply_lww(key, value, ts, NODE_ID)

            threading.Thread(
                target=replicate_to_peers,
                args=(key, value, ts, NODE_ID),
                daemon=True
            ).start()

            self.send_json(200, {
                "ok": True,
                "key": key,
                "value": value,
                "ts": ts,
                "lamport": get_lamport()
            })
            return

        if self.path == "/replicate":
            key = body["key"]
            value = body["value"]
            ts = body["ts"]
            origin = body["origin"]

            lamport_on_receive(ts)
            applied = apply_lww(key, value, ts, origin)

            self.send_json(200, {"ok": True, "applied": applied})
            return

        self.send_json(404, {"error": "not found"})

    def log_message(self, *_):
        return


# ---------- Startup ----------

def sync_from_peers():
    for peer in PEERS:
        try:
            with request.urlopen(peer + "/sync", timeout=2) as r:
                data = json.loads(r.read())
                lamport_on_receive(data["lamport"])
                for k, v in data["store"].items():
                    apply_lww(k, v["value"], v["ts"], v["origin"])
        except:
            pass


def main():
    global NODE_ID, PEERS

    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--peers", default="")
    args = parser.parse_args()

    NODE_ID = args.id
    PEERS = [p.strip() for p in args.peers.split(",") if p.strip()]

    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    print(f"[{NODE_ID}] running on port {args.port}")

    threading.Thread(target=sync_from_peers, daemon=True).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
