"""Coverage for examples/befund-pipeline-demo/extract.py.

Two layers:

* the pure helpers (``collect_bullets``, ``first_value``, ``ICD_RE``,
  ``KEY_VALUE_RE``) where the parsing rules actually live, and
* ``main`` as a subprocess, which pins the artefact shape that
  ``validate.py`` consumes.
"""
from __future__ import annotations

import unittest

from _support import SYNTHETIC_SCAN, TempCase, load_script, run_script

extract = load_script('extract.py')


class CollectBullets(unittest.TestCase):
    def test_collects_only_bullets_under_the_requested_heading(self):
        lines = ['Diagnosen:', '- erste', '- zweite', 'Medikation:', '- ignoriert']
        self.assertEqual(extract.collect_bullets(lines, 'Diagnosen'), ['erste', 'zweite'])
        self.assertEqual(extract.collect_bullets(lines, 'Medikation'), ['ignoriert'])

    def test_bullets_before_the_heading_are_ignored(self):
        lines = ['- vorher', 'Diagnosen:', '- nachher']
        self.assertEqual(extract.collect_bullets(lines, 'Diagnosen'), ['nachher'])

    def test_unknown_heading_yields_empty_list(self):
        self.assertEqual(extract.collect_bullets(['Diagnosen:', '- a'], 'Allergien'), [])

    def test_next_heading_terminates_the_section(self):
        lines = ['Diagnosen:', '- a', 'Beurteilung:', '- b', 'Diagnosen:', '- c']
        self.assertEqual(extract.collect_bullets(lines, 'Diagnosen'), ['a'])

    def test_indentation_and_dash_padding_are_normalised(self):
        lines = ['   Diagnosen:   ', '  -   mit Abstand  ']
        self.assertEqual(extract.collect_bullets(lines, 'Diagnosen'), ['mit Abstand'])

    def test_non_bullet_body_lines_inside_a_section_are_skipped(self):
        lines = ['Diagnosen:', 'freier Text', '- a']
        self.assertEqual(extract.collect_bullets(lines, 'Diagnosen'), ['a'])


class FirstValue(unittest.TestCase):
    def test_first_non_empty_key_wins(self):
        meta = {'a': '', 'b': 'zweiter', 'c': 'dritter'}
        self.assertEqual(extract.first_value(meta, 'a', 'b', 'c'), 'zweiter')

    def test_missing_keys_yield_empty_string(self):
        self.assertEqual(extract.first_value({}, 'a', 'b'), '')
        self.assertEqual(extract.first_value({'a': ''}, 'a'), '')


class Patterns(unittest.TestCase):
    def test_icd_pattern_accepts_the_documented_shapes(self):
        for code in ['I10', 'K29.7', 'E11.9', 'A00.0', 'T88.AB', 'Z99']:
            with self.subTest(code=code):
                self.assertEqual(extract.ICD_RE.search('x ' + code + ' y').group(1), code)

    def test_icd_pattern_rejects_u_chapter_and_malformed_codes(self):
        for text in ['U07.1', 'K2', '1K9', 'KK29']:
            with self.subTest(text=text):
                self.assertIsNone(extract.ICD_RE.search(text))

    def test_key_value_pattern_captures_umlaut_keys(self):
        match = extract.KEY_VALUE_RE.match('Empfaengerrolle: Hausarztpraxis')
        self.assertEqual(match.group(1), 'Empfaengerrolle')
        self.assertEqual(match.group(2), 'Hausarztpraxis')
        self.assertIsNotNone(extract.KEY_VALUE_RE.match('Geburtsdatum: 1980-01-31'))

    def test_key_value_pattern_ignores_bullets_and_bare_headings(self):
        self.assertIsNone(extract.KEY_VALUE_RE.match('Diagnosen:'))
        self.assertIsNone(extract.KEY_VALUE_RE.match('- K29.7 Gastritis'))


class ExtractCli(TempCase):
    def extract_from(self, text: str, **payload):
        source = self.write_json('ocr.json', dict(
            {'text': text, 'source': 'tests/synthetic', 'simulation': True,
             'confidence': 0.5}, **payload))
        target = self.tmp / 'out/befund.json'
        result = run_script('extract.py', source, target)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.read_json(target), result.stdout

    def test_wrong_argument_count_exits_two(self):
        result = run_script('extract.py', self.tmp / 'only-one.json')
        self.assertEqual(result.returncode, 2)
        self.assertIn('Usage: extract.py', result.stderr)

    def test_full_report_shape_from_synthetic_scan(self):
        report, stdout = self.extract_from(SYNTHETIC_SCAN)
        self.assertEqual(report['dokument']['typ'], 'Befundbericht')
        self.assertEqual(report['dokument']['datum'], '2026-04-15')
        self.assertEqual(report['dokument']['quelle'], 'tests/synthetic')
        self.assertIs(report['dokument']['ocr_simulation'], True)
        self.assertEqual(report['dokument']['ocr_confidence'], 0.5)
        self.assertEqual(report['patient'],
                         {'name': 'Testperson Gamma', 'geburtsdatum': '1980-01-31'})
        self.assertEqual(report['rollen']['absender'],
                         {'rolle': 'Testrolle Absender', 'name': 'Testabsender Alpha'})
        self.assertEqual(report['rollen']['empfaenger'],
                         {'rolle': 'Testrolle Empfaenger', 'name': 'Testempfaenger Beta'})
        self.assertEqual(report['medikation'],
                         ['Testwirkstoff A 500 mg', 'Testwirkstoff B 5 mg'])
        self.assertIn('rules/CORE_RULES.md#D-002', report['rules_references'])
        self.assertIn('Diagnosen: 3', stdout)
        self.assertIn('Medikation: 2', stdout)

    def test_diagnosis_text_has_the_code_removed_once(self):
        report, _ = self.extract_from('Diagnosen:\n- I10 Hypertonie, auch I10 genannt\n')
        self.assertEqual(report['diagnosen'],
                         [{'icd10': 'I10', 'text': 'Hypertonie, auch I10 genannt'}])

    def test_separator_dashes_left_behind_by_the_code_are_trimmed(self):
        report, _ = self.extract_from('Diagnosen:\n- K29.7 - Testdiagnose mit Trennstrich -\n')
        self.assertEqual(report['diagnosen'],
                         [{'icd10': 'K29.7', 'text': 'Testdiagnose mit Trennstrich'}])

    def test_bullets_without_icd_code_are_dropped(self):
        report, stdout = self.extract_from(
            'Diagnosen:\n- K29.7 bleibt\n- ohne Code\n- U07.1 nicht im Bereich\n')
        self.assertEqual([d['icd10'] for d in report['diagnosen']], ['K29.7'])
        self.assertIn('Diagnosen: 1', stdout)

    def test_missing_metadata_becomes_empty_string_not_none(self):
        report, _ = self.extract_from('Diagnosen:\n- I10 nur eine Diagnose\n')
        self.assertEqual(report['patient']['name'], '')
        self.assertEqual(report['dokument']['typ'], '')
        self.assertEqual(report['rollen']['empfaenger']['rolle'], '')

    def test_absent_ocr_keys_degrade_without_crashing(self):
        source = self.write_json('bare.json', {})
        target = self.tmp / 'befund.json'
        self.assertEqual(run_script('extract.py', source, target).returncode, 0)
        report = self.read_json(target)
        self.assertEqual(report['dokument']['quelle'], '')
        self.assertIs(report['dokument']['ocr_simulation'], False)
        self.assertIsNone(report['dokument']['ocr_confidence'])
        self.assertEqual(report['diagnosen'], [])

    def test_output_directory_is_created_and_file_ends_with_newline(self):
        _, _ = self.extract_from(SYNTHETIC_SCAN)
        raw = (self.tmp / 'out/befund.json').read_text(encoding='utf-8')
        self.assertTrue(raw.endswith('\n'))

    def test_umlauts_are_written_unescaped(self):
        self.extract_from('Dokumenttyp: Überweisung\nDiagnosen:\n- I10 Test\n')
        self.assertIn('Überweisung', (self.tmp / 'out/befund.json').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
