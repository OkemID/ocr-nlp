#!/usr/bin/env bash
set -euo pipefail

echo "[*] Checking Docker..."
docker --version >/dev/null

echo "[*] Building containers..."
docker compose up --build -d

echo "[*] Installing mobile deps..."
pushd apps/mobile >/dev/null
npm i
popd >/dev/null

echo "Done. Node API: http://localhost:4000  OCR: http://localhost:8000"
echo "Remember to set EXPO_PUBLIC_NODE_API_BASE in apps/mobile/.env"
