#!/usr/bin/env python3
"""Simulated OCR step for the cortex-desk examples."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: ocr_step.py <input-txt> <output-json>", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    text = input_path.read_text(encoding="utf-8")

    payload = {
        "engine": "cortex-desk-example-pseudo-ocr",
        "simulation": True,
        # Repo-relativer Pfad statt absolutem Maschinenpfad — generierte
        # Artefakte duerfen keine lokalen Nutzerpfade leaken (Review 26.07.).
        "source": "examples/befund-pipeline-demo/fixtures/" + input_path.name,
        "confidence": 0.973,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "text": text,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("OCR-Simulation: PASS")
    print(f"Quelle: {input_path}")
    print(f"Confidence: {payload['confidence']:.3f} (fiktiv)")
    print(f"Ziel: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

