#!/usr/bin/env python3
"""Validate the structured demo report with small plausibility checks."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path


ICD_RE = re.compile(r"^[A-TV-Z][0-9]{2}(?:\.[0-9A-Z]{1,2})?$")


def parse_iso_date(value: object, field: str, errors: list[str]) -> date | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{field}: Pflichtfeld fehlt oder ist leer")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{field}: kein plausibles ISO-Datum YYYY-MM-DD")
        return None


def require_path(data: dict, path: str, errors: list[str]) -> object:
    current: object = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            errors.append(f"{path}: Pflichtfeld fehlt")
            return None
        current = current[part]
    if current in ("", None, []):
        errors.append(f"{path}: Pflichtfeld ist leer")
    return current


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate.py <befund-json>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []

    for required in (
        "demo_notice",
        "dokument.typ",
        "dokument.datum",
        "patient.name",
        "patient.geburtsdatum",
        "rollen.absender.rolle",
        "rollen.empfaenger.rolle",
    ):
        require_path(data, required, errors)

    document_date = parse_iso_date(data.get("dokument", {}).get("datum"), "dokument.datum", errors)
    birth_date = parse_iso_date(data.get("patient", {}).get("geburtsdatum"), "patient.geburtsdatum", errors)

    if document_date and document_date > date.today():
        errors.append("dokument.datum: Datum liegt in der Zukunft")
    if birth_date and document_date and birth_date >= document_date:
        errors.append("patient.geburtsdatum: muss vor dem Dokumentdatum liegen")

    if data.get("dokument", {}).get("ocr_simulation") is not True:
        errors.append("dokument.ocr_simulation: Demo muss als Simulation markiert sein")

    diagnoses = data.get("diagnosen")
    if not isinstance(diagnoses, list) or not diagnoses:
        errors.append("diagnosen: mindestens eine Diagnose erforderlich")
    else:
        for index, diagnosis in enumerate(diagnoses, start=1):
            code = diagnosis.get("icd10") if isinstance(diagnosis, dict) else None
            if not isinstance(code, str) or not ICD_RE.match(code):
                errors.append(f"diagnosen[{index}].icd10: ungueltiges ICD-10-Format")
            if not isinstance(diagnosis, dict) or not diagnosis.get("text"):
                errors.append(f"diagnosen[{index}].text: Pflichtfeld fehlt")

    if not data.get("rules_references"):
        errors.append("rules_references: Bezug auf rules/ fehlt")

    print(f"Validierung: {'FAIL' if errors else 'PASS'}")
    print(f"Datei: {path}")
    print("Regelbezug: rules/CORE_RULES.md, rules/WORKFLOW.md")
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1

    print("- Pflichtfelder vorhanden")
    print("- ICD-10-Formate plausibel")
    print("- Datumsfelder plausibel")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

