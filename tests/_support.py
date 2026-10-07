"""Shared helpers for the repository-level test suites.

The demo pipeline ships as standalone CLI scripts, not as an importable
package. Two access paths are therefore needed and both are exercised:

* ``load_script`` imports a script by path so pure helper functions
  (``collect_bullets``, ``require_path``, ...) can be tested directly.
* ``run_script`` executes the same file as a real subprocess so argv
  handling, stdout contract and exit codes are covered as the shell
  actually uses them.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
DEMO = REPO / 'examples/befund-pipeline-demo'


def load_script(name: str):
    """Import a demo script by path without registering it in sys.modules."""
    spec = importlib.util.spec_from_file_location('demo_' + Path(name).stem, DEMO / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_script(name: str, *args) -> subprocess.CompletedProcess:
    """Run a demo script the way run-demo.sh does: real argv, real exit code.

    ``tests/coverage.sh`` sets ``DEMO_COVERAGE=1`` so the child is started
    under coverage; the measured behaviour is identical either way.
    """
    prefix = [sys.executable, '-B']
    if os.environ.get('DEMO_COVERAGE') == '1':
        prefix += ['-m', 'coverage', 'run', '--parallel-mode', '--branch',
                   '--source=' + str(DEMO)]
    argv = [*prefix, str(DEMO / name), *map(str, args)]
    return subprocess.run(argv, cwd=REPO, capture_output=True, text=True,
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))


class TempCase(unittest.TestCase):
    """Test case with a private scratch directory inside the repo's .tmp."""

    def setUp(self):
        super().setUp()
        (REPO / '.tmp').mkdir(exist_ok=True)
        holder = tempfile.TemporaryDirectory(dir=REPO / '.tmp')
        self.addCleanup(holder.cleanup)
        self.tmp = Path(holder.name)

    def write_json(self, name: str, data) -> Path:
        path = self.tmp / name
        path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        return path

    def read_json(self, path: Path):
        return json.loads(Path(path).read_text(encoding='utf-8'))


# Synthetic scan text. Mirrors the shape of the shipped fixture but carries
# only invented values; no document from the real workflow is used here.
SYNTHETIC_SCAN = """SYNTHETISCHER TESTTEXT - KEIN ECHTER BEFUND

Absenderrolle: Testrolle Absender
Absendername: Testabsender Alpha
Empfaengerrolle: Testrolle Empfaenger
Empfaengername: Testempfaenger Beta

Dokumentdatum: 2026-04-15
Patient: Testperson Gamma
Geburtsdatum: 1980-01-31
Dokumenttyp: Befundbericht

Diagnosen:
- K29.7 Testdiagnose eins
- E11.9 Testdiagnose zwei
- I10 Testdiagnose drei

Medikation:
- Testwirkstoff A 500 mg
- Testwirkstoff B 5 mg

Beurteilung:
Keine weiteren Angaben.
"""


def valid_report() -> dict:
    """Smallest report that validate.py accepts; tests mutate single fields."""
    return {
        'demo_notice': 'Synthetischer Testdatensatz.',
        'rules_references': ['rules/CORE_RULES.md#D-002'],
        'dokument': {'typ': 'Befundbericht', 'datum': '2026-04-15',
                     'quelle': 'tests/synthetic', 'ocr_simulation': True,
                     'ocr_confidence': 0.5},
        'patient': {'name': 'Testperson Gamma', 'geburtsdatum': '1980-01-31'},
        'rollen': {'absender': {'rolle': 'Testrolle Absender', 'name': 'Testabsender Alpha'},
                   'empfaenger': {'rolle': 'Testrolle Empfaenger', 'name': 'Testempfaenger Beta'}},
        'diagnosen': [{'icd10': 'K29.7', 'text': 'Testdiagnose eins'}],
        'medikation': ['Testwirkstoff A 500 mg'],
    }
