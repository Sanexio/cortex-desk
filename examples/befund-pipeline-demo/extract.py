#!/usr/bin/env python3
"""Extract structured demo data from the simulated OCR payload."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ICD_RE = re.compile(r"\b([A-TV-Z][0-9]{2}(?:\.[0-9A-Z]{1,2})?)\b")
KEY_VALUE_RE = re.compile(r"^([A-Za-zÄÖÜäöüß]+(?:rolle|name|datum|typ)?):\s*(.+)$")


def collect_bullets(lines: list[str], heading: str) -> list[str]:
    items: list[str] = []
    active = False
    for raw_line in lines:
        line = raw_line.strip()
        if line == f"{heading}:":
            active = True
            continue
        if active and line.endswith(":") and not line.startswith("-"):
            break
        if active and line.startswith("-"):
            items.append(line[1:].strip())
    return items


def first_value(meta: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = meta.get(key)
        if value:
            return value
    return ""


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: extract.py <ocr-json> <befund-json>", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    ocr_payload = json.loads(input_path.read_text(encoding="utf-8"))
    text = ocr_payload.get("text", "")
    lines = text.splitlines()

    meta: dict[str, str] = {}
    for line in lines:
        match = KEY_VALUE_RE.match(line.strip())
        if match:
            key = match.group(1).lower()
            meta[key] = match.group(2).strip()

    diagnosis_lines = collect_bullets(lines, "Diagnosen")
    diagnoses = []
    for item in diagnosis_lines:
        match = ICD_RE.search(item)
        if not match:
            continue
        code = match.group(1)
        diagnoses.append(
            {
                "icd10": code,
                "text": item.replace(code, "", 1).strip(" -"),
            }
        )

    medication = collect_bullets(lines, "Medikation")
    befund = {
        "demo_notice": "Pseudo-Engine-Ausgabe mit ausschliesslich fiktiven Daten.",
        "rules_references": [
            "rules/CORE_RULES.md#D-002",
            "rules/CORE_RULES.md#D-008",
            "rules/WORKFLOW.md#Teil-2-Generischer-Verarbeitungsgang",
        ],
        "dokument": {
            "typ": first_value(meta, "dokumenttyp"),
            "datum": first_value(meta, "dokumentdatum"),
            "quelle": ocr_payload.get("source", ""),
            "ocr_simulation": bool(ocr_payload.get("simulation")),
            "ocr_confidence": ocr_payload.get("confidence"),
        },
        "patient": {
            "name": first_value(meta, "patient"),
            "geburtsdatum": first_value(meta, "geburtsdatum"),
        },
        "rollen": {
            "absender": {
                "rolle": first_value(meta, "absenderrolle"),
                "name": first_value(meta, "absendername"),
            },
            "empfaenger": {
                "rolle": first_value(meta, "empfaengerrolle"),
                "name": first_value(meta, "empfaengername"),
            },
        },
        "diagnosen": diagnoses,
        "medikation": medication,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(befund, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("Extraktion: PASS")
    print(f"Diagnosen: {len(diagnoses)}")
    print(f"Medikation: {len(medication)}")
    print(f"Ziel: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

