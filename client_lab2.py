#!/usr/bin/env python3
"""
Lab 2 Client
PUT / GET / STATUS helper
"""

import argparse
import json
from urllib import request, parse


def post(url, data):
    payload = json.dumps(data).encode()
    req = request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with request.urlopen(req) as r:
        return json.loads(r.read())


def get(url):
    with request.urlopen(url) as r:
        return json.loads(r.read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", required=True)
    parser.add_argument("cmd", choices=["put", "get", "status"])
    parser.add_argument("key", nargs="?")
    parser.add_argument("value", nargs="?")
    args = parser.parse_args()

    base = args.node.rstrip("/")

    if args.cmd == "put":
        print(post(base + "/put", {
            "key": args.key,
            "value": args.value
        }))

    elif args.cmd == "get":
        print(get(base + f"/get?key={parse.quote(args.key)}"))

    elif args.cmd == "status":
        print(json.dumps(get(base + "/status"), indent=2))


if __name__ == "__main__":
    main()
