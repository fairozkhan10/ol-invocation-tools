# OL Invocation Tools

## Overview

The **OL Invocation Tools** project is a lightweight, endpoint-agnostic command-line interface (CLI) for invoking functions on a local or remote worker (e.g., OpenLambda). Instead of crafting long `curl` commands, it provides a clean UX like:

```bash
ol invoke <func> --data '{"x":1}' --pretty

Phase 1 focuses on developer experience and portability: JSON and file payloads, custom headers, pretty output, and a smoke script that targets any worker via OL_URL. A tiny mock worker is included so you can demo the CLI without spinning up the full OpenLambda stack.

Features

Friendly CLI: Replace complex curl with ol invoke <func>.

Flexible Inputs: Send payloads via --data (inline JSON), --json <file>, or --file <path>.

Headers & Timeout: Add --header "K: V" and tune --timeout.

Pretty Output: Use --pretty to format JSON responses.

Endpoint-Agnostic: Point to any base URL with --url or OL_URL.

Smoke Test: A one-command script validates the CLI end-to-end.

Mock Worker: Minimal HTTP server for local testing and demos.

Setup Instructions

Clone the Repository:

git clone https://github.com/fairozkhan10/ol-invocation-tools.git
cd ol-invocation-tools


Set Up a Python Virtual Environment:

python3 -m venv .venv
source .venv/bin/activate
python -V


Install the CLI (Editable):

pip install -e .
ol --help


Run the Mock Worker (Terminal A — keep it running):

python - <<'PY'
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, re
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        m = re.match(r"^/invoke/([^/]+)$", self.path)
        ln = int(self.headers.get("Content-Length","0"))
        body = self.rfile.read(ln).decode() if ln>0 else "{}"
        try: payload = json.loads(body or "{}")
        except: payload = {"raw": body}
        if not m: self.send_response(404); self.end_headers(); return
        self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers()
        self.wfile.write(json.dumps({"function": m.group(1), "received": payload}).encode())
print("mock worker on http://127.0.0.1:5000 ...")
HTTPServer(("127.0.0.1", 5000), H).serve_forever()
PY


Use the CLI (Terminal B):

# Inline JSON payload
ol invoke echo --data '{"hello":"ol"}' --pretty

# JSON from a file
echo '{"a":123}' > payload.json
ol invoke echo --json payload.json --pretty

# Binary payload with a custom header
echo "hello-bytes" > input.bin
ol invoke echo --file input.bin --header "X-Demo: test"


Run the Smoke Test:

./scripts/smoke.sh
# Expected:
# [smoke] using BASE_URL=http://127.0.0.1:5000
# [smoke] OK

Usage Guidelines

Basic Invocation: Use inline JSON for quick tests.

ol invoke <func> --data '{"k":"v"}'


Switch Endpoints: Target a different worker by URL or environment.

Per call:

ol invoke echo --url http://127.0.0.1:3000 --data '{}'


Via environment:

export OL_URL=http://127.0.0.1:3000
./scripts/smoke.sh


Headers, Timeout, Pretty Output: Add headers, adjust timeout, and pretty-print.

ol invoke echo --data '{}' --header "X-Trace: 1" --timeout 10 --pretty


Exit Codes:

0 — success (HTTP 2xx)

1 — non-2xx response

2 — bad CLI input (e.g., malformed --header)

>=3 — network/other errors

Project Structure

ol-invocation-tools/
├── cli/
│ └── ol/
│ └── cli.py # 'ol' CLI (argparse + urllib)
├── docs/
│ └── invocation-tools.md # Detailed usage & notes
├── examples/ # (Placeholder) sample functions
├── scripts/
│ └── smoke.sh # Endpoint-agnostic smoke test
├── pyproject.toml # Packaging (entrypoint 'ol')
└── README.md # Project documentation

Future Enhancements

Real OpenLambda Integration: Confirm official route/headers (e.g., /invoke/<func> vs /run/<func>) and align defaults or add a --path flag.

Examples: Add a tiny echo/WSGI example wired to the real worker.

Developer Experience: Retries/backoff, richer error messages, streaming output.

Docs & Demos: Short GIF/asciinema demo and a troubleshooting guide.

Upstream Plan: After feedback, open a focused PR to open-lambda/open-lambda (CLI + docs + example).

Contact

For any queries or suggestions, feel free to contact me at:

Email: fkhan35@wisc.edu

GitHub: https://github.com/fairozkhan10

