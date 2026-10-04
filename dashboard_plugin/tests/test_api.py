import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tosort_api', BASE / 'plugin_api.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class PluginTests(unittest.TestCase):
    def setUp(self):
        (BASE / '.tmp').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=BASE / '.tmp')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.archive = self.root / 'archive'
        self.inbox = self.archive / 'TOSORT'
        self.inbox.mkdir(parents=True)
        self.skill = self.root / 'skill'
        (self.skill / 'scripts').mkdir(parents=True)
        for name in ['archiv_index.py', 'tosort_route.py', 'downloads_liste.py', 'lern_diff.py']:
            (self.skill / 'scripts' / name).write_text('# fixture')
        self.logs = self.archive / '_AI_META/ARCHIV_INDEX/logs'
        self.logs.mkdir(parents=True)
        self.patches = [patch.object(api, 'ARCHIVE', self.archive), patch.object(api, 'SKILL', self.skill),
                        patch.object(api, 'STATE', self.root / 'state'), patch.object(Path, 'home', return_value=self.root),
                        patch.dict(os.environ, {'TOSORT_ENABLE_RUN': '1'})]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)
        app = FastAPI()
        app.include_router(api.router, prefix='/api/plugins/tosort')
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def post(self, **kwargs):
        return self.client.post('/api/plugins/tosort/lauf', headers={'X-TOSORT-Action': 'start'}, **kwargs)

    def test_empty_vs_missing(self):
        self.assertEqual(api.measure(self.inbox)['count'], 0)
        self.assertIsNone(api.measure(self.root / 'absent')['count'])

    def test_counts_age_exclusions_and_privacy(self):
        for name in ['PATIENT_SECRET.pdf', 'README.md', '.DS_Store', '_KLAEREN/private.txt', 'batch/second.pdf']:
            p = self.inbox / name
            p.parent.mkdir(exist_ok=True)
            p.write_text('SECRET_CONTENT')
            os.utime(p, (1000, 1000))
        result = self.client.get('/api/plugins/tosort/status').json()
        self.assertEqual(result['pools']['inbox']['count'], 2)
        self.assertEqual(result['pools']['clarification']['count'], 1)
        self.assertGreater(result['pools']['inbox']['oldest_age_seconds'], 86400)
        self.assertNotIn('SECRET', json.dumps(result))
        self.assertNotIn(str(self.root), json.dumps(result))

    def test_partial_read_fails_closed(self):
        with patch.object(api.os, 'scandir', side_effect=PermissionError('SECRET')):
            self.assertEqual(api.measure(self.inbox)['status'], 'not_measurable')

    def test_symlink_fails_closed(self):
        (self.inbox / 'link').symlink_to(self.root)
        self.assertIsNone(api.measure(self.inbox)['count'])

    def test_future_mtime_fails_closed(self):
        p = self.inbox / 'x'
        p.touch()
        os.utime(p, (9999999999, 9999999999))
        self.assertIsNone(api.measure(self.inbox)['count'])

    def test_existing_routing_timestamp_only(self):
        p = self.archive / '_AI_META/TOSORT/run/Routing_20261004.csv'
        p.parent.mkdir(parents=True)
        p.write_text('PATIENT_SECRET')
        os.utime(p, (1700000000, 1700000000))
        self.assertEqual(api.last_routing(self.archive), '2023-11-14T22:13:20+00:00')
        self.assertEqual(api.run_state()['status'], 'not_measurable')

    def test_corrupt_state_and_allowlist(self):
        api.STATE.mkdir()
        p = api.STATE / 'run.json'
        for raw in ['broken', '[]', '{"status":"PATIENT_SECRET"}']:
            p.write_text(raw)
            self.assertEqual(api.run_state()['status'], 'not_measurable')
        p.write_text(json.dumps({'status': 'failed', 'step': 'routing', 'started_at': api.utc(),
                                 'finished_at': api.utc(), 'stdout': 'PATIENT_SECRET'}))
        self.assertNotIn('SECRET', json.dumps(api.run_state()))

    def test_restart_running_is_unknown(self):
        api.STATE.mkdir()
        api.save_state({'status': 'running', 'step': 'routing', 'started_at': api.utc(), 'finished_at': None})
        (api.STATE / 'run.lock').touch()
        self.assertEqual(api.run_state()['status'], 'not_measurable')

    def test_disabled_and_csrf(self):
        with patch.dict(os.environ, {'TOSORT_ENABLE_RUN': '0'}):
            self.assertEqual(self.post().status_code, 403)
        self.assertEqual(self.client.post('/api/plugins/tosort/lauf').status_code, 403)
        self.assertEqual(self.client.post('/api/plugins/tosort/lauf', headers={
            'X-TOSORT-Action': 'start', 'Sec-Fetch-Site': 'cross-site'}).status_code, 403)

    def test_external_writer_blocks(self):
        (self.logs / '.archiv_index_writer.lock').write_text('123')
        with patch.object(api.subprocess, 'run') as run:
            self.assertEqual(self.post().status_code, 409)
            run.assert_not_called()

    def test_unavailable_input_and_script(self):
        self.inbox.rmdir()
        self.assertEqual(self.post().status_code, 503)
        self.inbox.mkdir()
        (self.skill / 'scripts/tosort_route.py').unlink()
        self.assertEqual(self.post().status_code, 503)

    def test_accepted_duplicate_and_worker_success(self):
        with patch.object(api, 'Thread') as thread:
            result = self.post()
            self.assertEqual(result.status_code, 202)
            self.assertEqual(api.run_state()['status'], 'running')
            self.assertEqual(self.post().status_code, 409)
            args = thread.call_args.kwargs['args']
            with patch.object(api.subprocess, 'run') as run:
                api.worker(*args)
                self.assertEqual(run.call_count, 5)
                for call in run.call_args_list:
                    self.assertEqual(call.kwargs['stdout'], subprocess.DEVNULL)
                    self.assertEqual(call.kwargs['stderr'], subprocess.DEVNULL)
            self.assertEqual(api.run_state()['status'], 'awaiting_review')
            self.assertFalse((self.logs / '.archiv_index_writer.lock').exists())

    def test_worker_failure_stops_and_redacts(self):
        with patch.object(api, 'Thread') as thread:
            self.assertEqual(self.post().status_code, 202)
            with patch.object(api.subprocess, 'run', side_effect=RuntimeError('PATIENT_SECRET')) as run:
                api.worker(*thread.call_args.kwargs['args'])
                self.assertEqual(run.call_count, 1)
            self.assertEqual(api.run_state()['status'], 'failed')
            self.assertNotIn('SECRET', (api.STATE / 'run.json').read_text())

    def test_real_subprocesses_with_synthetic_scripts(self):
        script = "import os, pathlib, sys\nwith (pathlib.Path(os.environ['ARCHIV_ROOT']) / 'calls.txt').open('a') as f: f.write(pathlib.Path(__file__).name + '\\n')\nprint('PATIENT_SECRET', file=sys.stderr)\n"
        for p in (self.skill / 'scripts').glob('*.py'):
            p.write_text(script)
        with patch.object(api, 'Thread') as thread:
            self.assertEqual(self.post().status_code, 202)
            api.worker(*thread.call_args.kwargs['args'])
        self.assertEqual(api.run_state()['status'], 'awaiting_review')
        self.assertEqual((self.archive / 'calls.txt').read_text().splitlines(),
                         ['archiv_index.py'] * 3 + ['tosort_route.py', 'downloads_liste.py'])
        self.assertNotIn('SECRET', (api.STATE / 'run.json').read_text())

    def test_command_contract_and_learning(self):
        cmds = api.commands('fixture')
        self.assertEqual([step for step, _ in cmds], ['scan', 'hash', 'registers', 'routing', 'review'])
        self.assertIn('--personenbezug', cmds[-1][1])
        self.assertNotIn('tosort_execute.py', str(cmds))
        (self.root / 'Downloads').mkdir()
        (self.root / 'Downloads/TOSORT_Umbenennung_fixture.csv').touch()
        self.assertIn('learning', [step for step, _ in api.commands('fixture')])


if __name__ == '__main__':
    unittest.main(verbosity=2)
