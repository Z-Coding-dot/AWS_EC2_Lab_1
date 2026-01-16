from flask import Flask, request, jsonify
import threading
import time
import requests
import sys
import random

app = Flask(__name__)

# ----------------------------
# Node state
# ----------------------------
node_id = None
port = None
peers = []

state = "Follower"   # Follower | Candidate | Leader
current_term = 0
voted_for = None
log = []
commit_index = -1

votes_received = 0
leader_id = None

election_timeout = random.uniform(3, 5)
last_heartbeat = time.time()

lock = threading.Lock()

# ----------------------------
# RPC: RequestVote
# ----------------------------
@app.route("/request_vote", methods=["POST"])
def request_vote():
    global current_term, voted_for, state

    data = request.json
    term = data["term"]
    candidate = data["candidate"]

    with lock:
        if term > current_term:
            current_term = term
            voted_for = None
            state = "Follower"

        vote_granted = False
        if term == current_term and (voted_for is None or voted_for == candidate):
            voted_for = candidate
            vote_granted = True

    print(f"[{node_id}] Vote request from {candidate} (term {term}) → {vote_granted}")
    return jsonify({"term": current_term, "voteGranted": vote_granted})

# ----------------------------
# RPC: AppendEntries (heartbeat + log replication)
# ----------------------------
@app.route("/append_entries", methods=["POST"])
def append_entries():
    global current_term, state, last_heartbeat, leader_id

    data = request.json
    term = data["term"]
    leader = data["leader"]
    entries = data.get("entries", [])

    with lock:
        if term >= current_term:
            current_term = term
            state = "Follower"
            leader_id = leader
            last_heartbeat = time.time()

            if entries:
                for entry in entries:
                    log.append(entry)
                    print(f"[{node_id}] Appended log entry {entry}")

            return jsonify({"term": current_term, "success": True})

    return jsonify({"term": current_term, "success": False})

# ----------------------------
# Background: election timeout
# ----------------------------
def election_daemon():
    global state, current_term, voted_for, votes_received

    while True:
        time.sleep(0.5)
        with lock:
            if state != "Leader" and time.time() - last_heartbeat > election_timeout:
                state = "Candidate"
                current_term += 1
                voted_for = node_id
                votes_received = 1
                print(f"[{node_id}] Timeout → Candidate (term {current_term})")

                for peer in peers:
                    try:
                        r = requests.post(
                            f"http://{peer}/request_vote",
                            json={"term": current_term, "candidate": node_id},
                            timeout=1
                        )
                        if r.json().get("voteGranted"):
                            votes_received += 1
                    except:
                        pass

                if votes_received > (len(peers) + 1) // 2:
                    state = "Leader"
                    print(f"[{node_id}] Elected Leader (term {current_term})")

# ----------------------------
# Background: leader heartbeat
# ----------------------------
def heartbeat_daemon():
    while True:
        time.sleep(1)
        with lock:
            if state == "Leader":
                for peer in peers:
                    try:
                        requests.post(
                            f"http://{peer}/append_entries",
                            json={"term": current_term, "leader": node_id},
                            timeout=1
                        )
                    except:
                        pass

# ----------------------------
# Client command (leader only)
# ----------------------------
@app.route("/command", methods=["POST"])
def command():
    global commit_index

    if state != "Leader":
        return jsonify({"error": "Not leader"}), 400

    cmd = request.json["cmd"]
    entry = {"term": current_term, "cmd": cmd}
    log.append(entry)

    acks = 1
    for peer in peers:
        try:
            r = requests.post(
                f"http://{peer}/append_entries",
                json={"term": current_term, "leader": node_id, "entries": [entry]},
                timeout=1
            )
            if r.json().get("success"):
                acks += 1
        except:
            pass

    if acks > (len(peers) + 1) // 2:
        commit_index += 1
        print(f"[Leader {node_id}] Entry committed: {cmd}")
        return jsonify({"status": "committed"})

    return jsonify({"status": "failed"}), 500

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    node_id = sys.argv[1]
    port = int(sys.argv[2])
    peers = sys.argv[3:]

    threading.Thread(target=election_daemon, daemon=True).start()
    threading.Thread(target=heartbeat_daemon, daemon=True).start()

    app.run(host="0.0.0.0", port=port)
