#!/usr/bin/env bash
# Runs both test suites with coverage instrumentation and prints one report
# per language. Requirements: python3 with fastapi, httpx and coverage; node; npm.
#
#   bash tests/coverage.sh
#
# tools/desk-sync.sh is exercised by tests/test_desk_sync.py but cannot be
# measured by either tool; its tests are verified by mutation instead.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export PYTHONDONTWRITEBYTECODE=1
# Makes the demo-script subprocesses report their own coverage.
export DEMO_COVERAGE=1

echo "== Python =="
python3 -B -m coverage erase
python3 -B -m coverage run --parallel-mode --branch --source=dashboard_plugin,examples \
  -m unittest discover -s dashboard_plugin/tests -t dashboard_plugin/tests
python3 -B -m coverage run --parallel-mode --branch --source=dashboard_plugin,examples \
  -m unittest discover -s tests -t tests
python3 -B -m coverage combine
python3 -B -m coverage report -m --omit='*/tests/*'

echo
echo "== Node =="
npm ci --prefix dashboard_plugin --cache .tmp/npm-cache --no-audit --no-fund >/dev/null
node dashboard_plugin/build.mjs
cd dashboard_plugin
node --experimental-test-coverage --test tests/dom.test.cjs tests/render.test.cjs
