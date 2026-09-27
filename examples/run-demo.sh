#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO_DIR="$ROOT_DIR/examples/befund-pipeline-demo"
OUT_DIR="$DEMO_DIR/out"
BROKEN_JSON="$OUT_DIR/befund-broken.json"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

echo "== cortex-desk Befund-Pipeline-Demo =="
echo "Hinweis: Dies ist eine Pseudo-Engine mit ausschliesslich fiktiven Demo-Daten."
echo

echo "== Schritt 1: simulierte OCR =="
python3 "$DEMO_DIR/ocr_step.py" \
  "$DEMO_DIR/fixtures/scan-befund.txt" \
  "$OUT_DIR/ocr.json"
echo

echo "== Schritt 2: Extraktion =="
python3 "$DEMO_DIR/extract.py" \
  "$OUT_DIR/ocr.json" \
  "$OUT_DIR/befund.json"
echo

echo "== Schritt 3: Validierung PASS-Pfad =="
python3 "$DEMO_DIR/validate.py" "$OUT_DIR/befund.json"
echo

echo "== Schritt 4: Validierung FAIL-Pfad mit absichtlich defektem Feld =="
python3 - "$OUT_DIR/befund.json" "$BROKEN_JSON" <<'PY'
import json
import sys
from pathlib import Path

source = Path(sys.argv[1])
target = Path(sys.argv[2])
data = json.loads(source.read_text(encoding="utf-8"))
data["dokument"]["datum"] = "2026-99-99"
target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

set +e
python3 "$DEMO_DIR/validate.py" "$BROKEN_JSON"
status=$?
set -e

if [[ "$status" -eq 0 ]]; then
  echo "FAIL-Pfad hat unerwartet Exit-Code 0 geliefert." >&2
  exit 1
fi

echo "FAIL-Pfad erwartungsgemaess mit Exit-Code $status beendet."
echo
echo "Demo-Ausgabe liegt in: $OUT_DIR"

