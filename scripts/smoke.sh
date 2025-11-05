#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${OL_URL:-http://127.0.0.1:5000}"

echo "[smoke] using BASE_URL=${BASE_URL}"
ol invoke echo --url "${BASE_URL}" --data '{"hello":"ol"}' --pretty | grep '"hello": "ol"' >/dev/null

echo '{"a":123}' > /tmp/payload.json
ol invoke echo --url "${BASE_URL}" --json /tmp/payload.json --pretty | grep '"a": 123' >/dev/null

echo "hello-bytes" > /tmp/input.bin
ol invoke echo --url "${BASE_URL}" --file /tmp/input.bin --header "X-Demo: test" >/dev/null

echo "[smoke] OK"
