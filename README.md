# OL Invocation Tools (sandbox)

Phase-1 goal: make invoking functions trivial from the terminal while staying portable (works against a mock server and the real OpenLambda worker once pointed via OL_URL).

Note: This is an active sandbox. I’ll keep iterating (nicer flags, docs, examples) and then upstream the pieces to OpenLambda after feedback.

What’s included today

ol CLI (editable install): invoke subcommand with:

Input sources: --data (inline JSON), --json <file>, --file <path>

Request options: --header "K: V", --timeout <seconds>, --url <base>, --pretty

Exit code mirrors HTTP status class (0 on 2xx; non-zero otherwise)

Mock worker: tiny Python HTTP server to test the CLI locally.

Smoke script: one command that runs 3 invocations and asserts success (works against any base URL via OL_URL).

Requirements

macOS/Linux with Python 3.9+

(Optional) Go/Docker for later when testing against the real OpenLambda worker

Quickstart
1) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate
python -V

2) Install the CLI (editable)
pip install -e .
ol --help

3) Start the mock worker (Terminal A — leave running)
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

4) Invoke from the CLI (Terminal B)
# inline JSON
ol invoke echo --data '{"hello":"ol"}' --pretty

# JSON from file
echo '{"a":123}' > payload.json
ol invoke echo --json payload.json --pretty

# binary payload with custom header
echo "hello-bytes" > input.bin
ol invoke echo --file input.bin --header "X-Demo: test"

5) One-command smoke test
./scripts/smoke.sh
# output:
# [smoke] using BASE_URL=http://127.0.0.1:5000
# [smoke] OK

Environment variables

OL_URL — base URL for the worker (default: http://127.0.0.1:5000)

export OL_URL=http://127.0.0.1:3000
./scripts/smoke.sh

Usage reference
ol invoke <func> [--data JSON] [--json FILE] [--file PATH] \
              [--header "K: V"] [--timeout SECONDS] \
              [--pretty] [--url BASE]


--data expects a JSON string.

--json reads JSON from a file.

--file sends raw bytes and sets Content-Type: application/octet-stream.

--header can be repeated to add multiple headers.

--url overrides OL_URL just for this call.

Exit status:

0 = success (HTTP 2xx)

1 = non-2xx response

2 = bad CLI input (e.g., malformed header)

>= 3 = network/other errors

Repo layout (current)
.
├─ cli/ol/cli.py          # 'ol' CLI (argparse + urllib)
├─ docs/invocation-tools.md
├─ examples/              # placeholder for tiny sample functions
├─ scripts/smoke.sh       # endpoint-agnostic smoke test
├─ pyproject.toml         # packaging (editable install) -> 'ol' entrypoint
└─ README.md

Next steps (planned)

Confirm the exact HTTP route/headers expected by the real OpenLambda worker and align defaults (or add a --path flag).

Add a tiny example function (e.g., echo/WSGI) wired to the real worker.

Record a short demo (GIF/asciinema) and propose upstream placement (CLI + docs + example).

Expand docs with troubleshooting, return-code matrix, and integration snippets.

Last updated: 2025-11-29 — more changes to come after testing against the real OpenLambda worker.
MD
