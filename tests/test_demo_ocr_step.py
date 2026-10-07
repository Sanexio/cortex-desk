"""Coverage for examples/befund-pipeline-demo/ocr_step.py.

The step is a stub engine, but it owns two contracts the rest of the demo
relies on: the payload must be marked as a simulation, and the recorded
source must stay a repo-relative path so generated artefacts cannot leak
local user paths (the reason the hard-coded prefix exists).
"""
from __future__ import annotations

from datetime import datetime
import json
import unittest

from _support import SYNTHETIC_SCAN, TempCase, run_script


class OcrStepCli(TempCase):
    def scan(self, text: str = SYNTHETIC_SCAN, name: str = 'scan-synthetic.txt'):
        path = self.tmp / name
        path.write_text(text, encoding='utf-8')
        return path

    def test_wrong_argument_count_exits_two(self):
        for args in ([], [str(self.tmp / 'a.txt')],
                     [str(self.tmp / 'a.txt'), str(self.tmp / 'b.json'), 'extra']):
            with self.subTest(args=args):
                result = run_script('ocr_step.py', *args)
                self.assertEqual(result.returncode, 2)
                self.assertIn('Usage: ocr_step.py', result.stderr)
                self.assertEqual(result.stdout, '')

    def test_payload_marks_simulation_and_keeps_source_repo_relative(self):
        source = self.scan()
        target = self.tmp / 'nested/deep/ocr.json'
        result = run_script('ocr_step.py', source, target)
        self.assertEqual(result.returncode, 0, result.stderr)

        payload = self.read_json(target)
        self.assertIs(payload['simulation'], True)
        self.assertEqual(payload['engine'], 'cortex-desk-example-pseudo-ocr')
        self.assertEqual(payload['source'],
                         'examples/befund-pipeline-demo/fixtures/scan-synthetic.txt')
        # The absolute input path must not survive into the artefact.
        self.assertNotIn(str(self.tmp), json.dumps(payload))
        self.assertNotIn(str(source.parent), payload['source'])

    def test_text_is_copied_verbatim_including_umlauts(self):
        text = 'Zeile mit Umlauten: ÄÖÜ äöü ß\nZweite Zeile\n'
        target = self.tmp / 'ocr.json'
        self.assertEqual(run_script('ocr_step.py', self.scan(text), target).returncode, 0)
        self.assertEqual(self.read_json(target)['text'], text)

    def test_confidence_and_timestamp_are_machine_readable(self):
        target = self.tmp / 'ocr.json'
        run_script('ocr_step.py', self.scan(), target)
        payload = self.read_json(target)
        self.assertEqual(payload['confidence'], 0.973)
        stamp = datetime.fromisoformat(payload['created_at'])
        self.assertIsNotNone(stamp.tzinfo)

    def test_output_directory_is_created_on_demand(self):
        target = self.tmp / 'does/not/exist/ocr.json'
        self.assertFalse(target.parent.exists())
        self.assertEqual(run_script('ocr_step.py', self.scan(), target).returncode, 0)
        self.assertTrue(target.is_file())

    def test_stdout_reports_pass_and_target(self):
        target = self.tmp / 'ocr.json'
        stdout = run_script('ocr_step.py', self.scan(), target).stdout
        self.assertIn('OCR-Simulation: PASS', stdout)
        self.assertIn('Confidence: 0.973', stdout)
        self.assertIn(str(target), stdout)

    def test_missing_input_file_is_not_swallowed(self):
        result = run_script('ocr_step.py', self.tmp / 'absent.txt', self.tmp / 'ocr.json')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.tmp / 'ocr.json').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
