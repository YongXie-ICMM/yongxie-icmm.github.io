#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-4000}"
SKIP_NPM="${SKIP_NPM:-0}"

echo "[1/3] Checking required tools..."
command -v ruby >/dev/null 2>&1 || { echo "Ruby is not installed."; exit 1; }
command -v bundle >/dev/null 2>&1 || { echo "Bundler is not installed."; exit 1; }

echo "[2/3] Installing Ruby dependencies (bundle install)..."
bundle install

if [[ "$SKIP_NPM" != "1" && -f "package.json" ]]; then
  if command -v npm >/dev/null 2>&1; then
    echo "[optional] Installing Node dependencies (npm install)..."
    npm install
  else
    echo "npm not found; skipping npm install."
  fi
fi

echo "[3/3] Starting local site at http://${HOST}:${PORT}"
bundle exec jekyll serve --host "$HOST" --port "$PORT" --livereload
