#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_DIR="$ROOT_DIR/backend"
BACKEND_ENV_FILE="$BACKEND_DIR/.env.local"
FRONTEND_ENV_FILE="$FRONTEND_DIR/.env.local"

if [[ ! -f "$FRONTEND_ENV_FILE" ]]; then
  echo "Missing $FRONTEND_ENV_FILE"
  exit 1
fi

if [[ ! -f "$BACKEND_ENV_FILE" ]]; then
  echo "Missing $BACKEND_ENV_FILE"
  exit 1
fi

if [[ ! -x "$BACKEND_DIR/.venv/bin/uvicorn" ]]; then
  echo "Missing backend/.venv/bin/uvicorn (create backend venv and install requirements first)"
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found"
  exit 1
fi

# Export backend auth env vars from the local env file.
set -a
source "$BACKEND_ENV_FILE"
set +a

backend_pid=""

cleanup() {
  if [[ -n "$backend_pid" ]] && kill -0 "$backend_pid" >/dev/null 2>&1; then
    kill "$backend_pid" >/dev/null 2>&1 || true
    wait "$backend_pid" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

echo "Starting backend on http://localhost:8000"
(
  cd "$BACKEND_DIR"
  ./.venv/bin/uvicorn main:app --reload --host 127.0.0.1 --port 8000
) &
backend_pid=$!

echo "Starting frontend on http://localhost:3000"
cd "$FRONTEND_DIR"
npm run dev
