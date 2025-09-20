#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-http://localhost:8080}"

echo "[1] JWKS"
jwks=$(curl -s "${BASE}/.well-known/jwks.json")
echo "$jwks" | jq . >/dev/null || true
keys=$(echo "$jwks" | jq '.keys | length')
test "$keys" -eq 1

kid=$(echo "$jwks" | jq -r '.keys[0].kid')

echo "[2] Active token"
resp=$(curl -s -X POST "${BASE}/auth")
akid=$(echo "$resp" | jq -r .kid)
test "$akid" = "$kid"

echo "[3] Expired token"
resp2=$(curl -s -X POST "${BASE}/auth?expired=1")
ekid=$(echo "$resp2" | jq -r .kid)
test "$ekid" != "$kid"

echo "OK"
