#!/usr/bin/env python3
import sys, json, argparse, os
from urllib import request, error

# === "WORKER": HTTP helper ===
def post(url: str, data: bytes, headers: dict, timeout: int):
    req = request.Request(url, data=data, method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:
        return 599, str(e)

# === "MANAGER": CLI entrypoint ===
def main():
    p = argparse.ArgumentParser(prog="ol", description="OpenLambda helper CLI")
    s = p.add_subparsers(dest="cmd", required=True)

    iv = s.add_parser("invoke", help="Invoke a function")
    iv.add_argument("func", help="Function name")
    iv.add_argument("--data", help="Inline JSON string payload")
    iv.add_argument("--json", help="Path to JSON file payload")
    iv.add_argument("--file", help="Path to binary file payload")
    iv.add_argument("--header", action="append", default=[], help='Extra header "K: V" (repeatable)')
    iv.add_argument("--timeout", type=int, default=15, help="HTTP timeout seconds")
    iv.add_argument("--pretty", action="store_true", help="Pretty-print JSON responses if possible")
    iv.add_argument("--url", help="Base URL of worker (overrides OL_URL env)")

    a = p.parse_args()

    if a.cmd == "invoke":
        # 1) server address
        base = a.url or os.getenv("OL_URL", "http://127.0.0.1:5000")
        url = f"{base.rstrip('/')}/invoke/{a.func}"

        # 2) request body
        body = b"{}"
        headers = {"Content-Type": "application/json"}
        if a.file:
            body = open(a.file, "rb").read()
            headers["Content-Type"] = "application/octet-stream"
        elif a.json:
            body = open(a.json, "rb").read()
            headers["Content-Type"] = "application/json"
        elif a.data:
            body = a.data.encode()
            headers["Content-Type"] = "application/json"

        # extra headers
        for h in a.header:
            if ":" not in h:
                print(f"Invalid --header (use 'K: V'): {h}", file=sys.stderr)
                sys.exit(2)
            k, v = h.split(":", 1)
            headers[k.strip()] = v.strip()

        # 3) send + print
        status, resp = post(url, body, headers, a.timeout)
        if a.pretty:
            try:
                print(json.dumps(json.loads(resp), indent=2, ensure_ascii=False))
            except Exception:
                print(resp)
        else:
            print(resp)
        sys.exit(0 if 200 <= status < 300 else 1)

# === ignition ===
if __name__ == "__main__":
    main()
