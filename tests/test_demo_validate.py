"""Coverage for examples/befund-pipeline-demo/validate.py.

Every rule the validator enforces gets one failing report and one passing
counterpart, so a dropped check turns a test red instead of silently
letting an implausible report through.
"""
from __future__ import annotations

from datetime import date, timedelta
import unittest

from _support import TempCase, load_script, run_script, valid_report

validate = load_script('validate.py')


class ParseIsoDate(unittest.TestCase):
    def test_valid_iso_date_is_returned(self):
        errors: list[str] = []
        self.assertEqual(validate.parse_iso_date('2026-04-15', 'f', errors), date(2026, 4, 15))
        self.assertEqual(errors, [])

    def test_missing_or_non_string_values_are_reported_as_mandatory(self):
        for value in [None, '', 20260415, ['2026-04-15'], {}]:
            with self.subTest(value=value):
                errors: list[str] = []
                self.assertIsNone(validate.parse_iso_date(value, 'feld', errors))
                self.assertEqual(errors, ['feld: Pflichtfeld fehlt oder ist leer'])

    def test_unparsable_strings_are_reported_as_format_errors(self):
        for value in ['2026-99-99', '15.04.2026', 'heute', '2026-04']:
            with self.subTest(value=value):
                errors: list[str] = []
                self.assertIsNone(validate.parse_iso_date(value, 'feld', errors))
                self.assertEqual(errors, ['feld: kein plausibles ISO-Datum YYYY-MM-DD'])


class RequirePath(unittest.TestCase):
    def test_nested_value_is_returned_without_errors(self):
        errors: list[str] = []
        data = {'a': {'b': 'wert'}}
        self.assertEqual(validate.require_path(data, 'a.b', errors), 'wert')
        self.assertEqual(errors, [])

    def test_absent_segment_is_reported_once(self):
        errors: list[str] = []
        self.assertIsNone(validate.require_path({'a': {}}, 'a.b', errors))
        self.assertEqual(errors, ['a.b: Pflichtfeld fehlt'])

    def test_non_dict_segment_is_reported_instead_of_raising(self):
        errors: list[str] = []
        self.assertIsNone(validate.require_path({'a': 'text'}, 'a.b', errors))
        self.assertEqual(errors, ['a.b: Pflichtfeld fehlt'])

    def test_empty_values_are_reported_but_still_returned(self):
        for empty in ['', None, []]:
            with self.subTest(empty=empty):
                errors: list[str] = []
                self.assertEqual(validate.require_path({'a': empty}, 'a', errors), empty)
                self.assertEqual(errors, ['a: Pflichtfeld ist leer'])


class ValidateCli(TempCase):
    def check(self, report):
        path = self.write_json('befund.json', report)
        result = run_script('validate.py', path)
        return result.returncode, result.stdout

    def assert_fails_with(self, report, fragment):
        code, stdout = self.check(report)
        self.assertEqual(code, 1, stdout)
        self.assertIn('Validierung: FAIL', stdout)
        self.assertIn(fragment, stdout)

    def test_wrong_argument_count_exits_two(self):
        for args in ([], [self.tmp / 'a.json', self.tmp / 'b.json']):
            with self.subTest(args=args):
                result = run_script('validate.py', *args)
                self.assertEqual(result.returncode, 2)
                self.assertIn('Usage: validate.py', result.stderr)

    def test_well_formed_report_passes(self):
        code, stdout = self.check(valid_report())
        self.assertEqual(code, 0, stdout)
        self.assertIn('Validierung: PASS', stdout)
        self.assertIn('- Pflichtfelder vorhanden', stdout)
        self.assertIn('- ICD-10-Formate plausibel', stdout)
        self.assertIn('- Datumsfelder plausibel', stdout)
        self.assertIn('Regelbezug: rules/CORE_RULES.md, rules/WORKFLOW.md', stdout)

    def test_each_mandatory_path_is_enforced(self):
        paths = ['demo_notice', 'dokument.typ', 'dokument.datum', 'patient.name',
                 'patient.geburtsdatum', 'rollen.absender.rolle', 'rollen.empfaenger.rolle']
        for path in paths:
            with self.subTest(path=path):
                report = valid_report()
                node = report
                *parents, leaf = path.split('.')
                for part in parents:
                    node = node[part]
                del node[leaf]
                self.assert_fails_with(report, path + ': Pflichtfeld fehlt')

    def test_empty_mandatory_field_is_rejected(self):
        report = valid_report()
        report['rollen']['absender']['rolle'] = ''
        self.assert_fails_with(report, 'rollen.absender.rolle: Pflichtfeld ist leer')

    def test_future_document_date_is_rejected(self):
        report = valid_report()
        report['dokument']['datum'] = (date.today() + timedelta(days=1)).isoformat()
        self.assert_fails_with(report, 'dokument.datum: Datum liegt in der Zukunft')

    def test_today_is_still_accepted(self):
        report = valid_report()
        report['dokument']['datum'] = date.today().isoformat()
        self.assertEqual(self.check(report)[0], 0)

    def test_birth_date_must_precede_the_document_date(self):
        for birth in ['2026-04-15', '2026-04-16']:
            with self.subTest(birth=birth):
                report = valid_report()
                report['patient']['geburtsdatum'] = birth
                self.assert_fails_with(
                    report, 'patient.geburtsdatum: muss vor dem Dokumentdatum liegen')

    def test_unparsable_dates_skip_the_ordering_check(self):
        report = valid_report()
        report['dokument']['datum'] = '2026-99-99'
        code, stdout = self.check(report)
        self.assertEqual(code, 1)
        self.assertIn('dokument.datum: kein plausibles ISO-Datum YYYY-MM-DD', stdout)
        self.assertNotIn('muss vor dem Dokumentdatum liegen', stdout)

    def test_simulation_flag_must_be_exactly_true(self):
        for flag in [False, None, 'true', 1, 'ja']:
            with self.subTest(flag=flag):
                report = valid_report()
                report['dokument']['ocr_simulation'] = flag
                self.assert_fails_with(
                    report,
                    'dokument.ocr_simulation: Demo muss als Simulation markiert sein')

    def test_missing_simulation_flag_is_rejected(self):
        report = valid_report()
        del report['dokument']['ocr_simulation']
        self.assert_fails_with(
            report, 'dokument.ocr_simulation: Demo muss als Simulation markiert sein')

    def test_at_least_one_diagnosis_is_required(self):
        for diagnoses in [[], None, 'K29.7', {}]:
            with self.subTest(diagnoses=diagnoses):
                report = valid_report()
                report['diagnosen'] = diagnoses
                self.assert_fails_with(
                    report, 'diagnosen: mindestens eine Diagnose erforderlich')

    def test_invalid_icd_codes_are_reported_per_index(self):
        report = valid_report()
        report['diagnosen'] = [{'icd10': 'K29.7', 'text': 'ok'},
                               {'icd10': 'U07.1', 'text': 'ausserhalb'},
                               {'icd10': 'K2', 'text': 'zu kurz'},
                               {'icd10': 7, 'text': 'kein String'}]
        code, stdout = self.check(report)
        self.assertEqual(code, 1)
        self.assertNotIn('diagnosen[1].icd10', stdout)
        for index in (2, 3, 4):
            self.assertIn(f'diagnosen[{index}].icd10: ungueltiges ICD-10-Format', stdout)

    def test_icd_code_must_match_the_whole_field(self):
        report = valid_report()
        report['diagnosen'] = [{'icd10': 'K29.7 Gastritis', 'text': 'Code mit Text'}]
        self.assert_fails_with(report, 'diagnosen[1].icd10: ungueltiges ICD-10-Format')

    def test_diagnosis_text_is_mandatory(self):
        report = valid_report()
        report['diagnosen'] = [{'icd10': 'K29.7'}, {'icd10': 'I10', 'text': ''}]
        code, stdout = self.check(report)
        self.assertEqual(code, 1)
        self.assertIn('diagnosen[1].text: Pflichtfeld fehlt', stdout)
        self.assertIn('diagnosen[2].text: Pflichtfeld fehlt', stdout)

    def test_non_dict_diagnosis_entry_is_reported_twice_not_raised(self):
        report = valid_report()
        report['diagnosen'] = ['K29.7 Gastritis']
        code, stdout = self.check(report)
        self.assertEqual(code, 1)
        self.assertIn('diagnosen[1].icd10: ungueltiges ICD-10-Format', stdout)
        self.assertIn('diagnosen[1].text: Pflichtfeld fehlt', stdout)

    def test_rules_reference_is_mandatory(self):
        for value in [[], '', None]:
            with self.subTest(value=value):
                report = valid_report()
                report['rules_references'] = value
                self.assert_fails_with(report, 'rules_references: Bezug auf rules/ fehlt')
        report = valid_report()
        del report['rules_references']
        self.assert_fails_with(report, 'rules_references: Bezug auf rules/ fehlt')

    def test_all_errors_are_reported_in_one_run(self):
        code, stdout = self.check({'diagnosen': [{'icd10': 'nope'}]})
        self.assertEqual(code, 1)
        self.assertIn('demo_notice: Pflichtfeld fehlt', stdout)
        self.assertIn('dokument.typ: Pflichtfeld fehlt', stdout)
        self.assertIn('diagnosen[1].icd10: ungueltiges ICD-10-Format', stdout)
        self.assertIn('rules_references: Bezug auf rules/ fehlt', stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
