"""Coverage for tools/desk-sync.sh.

The script had no automated coverage although it decides whether a local
checkout is cloned, fast-forwarded or refused. Every test builds its own
synthetic git repositories inside a scratch directory and uses a ``file://``
remote, so nothing reaches the network and no real desk repo is touched.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

from _support import REPO, TempCase

SCRIPT = REPO / 'tools/desk-sync.sh'
BRANCH = 'desk-main'
GIT_ENV = {
    'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_SYSTEM': '/dev/null',
    'GIT_AUTHOR_NAME': 'Test', 'GIT_AUTHOR_EMAIL': 'test@example.invalid',
    'GIT_COMMITTER_NAME': 'Test', 'GIT_COMMITTER_EMAIL': 'test@example.invalid',
    'GIT_TERMINAL_PROMPT': '0', 'HOME': '/nonexistent-home-for-tests',
}


def git(*args, cwd: Path) -> str:
    result = subprocess.run(['git', *map(str, args)], cwd=cwd, capture_output=True,
                            text=True, env=GIT_ENV, check=True)
    return result.stdout.strip()


class DeskSyncScript(TempCase):
    def setUp(self):
        super().setUp()
        self.remote = self.tmp / 'remote'
        self.remote.mkdir()
        git('init', '-q', '--initial-branch', BRANCH, '.', cwd=self.remote)
        self.commit(self.remote, 'erste.txt', 'eins')
        self.local = self.tmp / 'nested/local'

    def commit(self, repo: Path, name: str, text: str) -> str:
        (repo / name).write_text(text, encoding='utf-8')
        git('add', name, cwd=repo)
        git('commit', '-q', '-m', 'synthetic ' + name, cwd=repo)
        return git('rev-parse', 'HEAD', cwd=repo)

    def config(self, url=None, local=None, branch=BRANCH, name='desk-sync.conf') -> Path:
        lines = []
        if url is not None:
            lines.append(f'DESK_REPO_URL="{url}"')
        if local is not None:
            lines.append(f'DESK_LOCAL_DIR="{local}"')
        if branch is not None:
            lines.append(f'DESK_BRANCH="{branch}"')
        path = self.tmp / name
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return path

    def full_config(self) -> Path:
        return self.config(url=self.remote.as_uri(), local=self.local)

    def sync(self, *args, config: Path | None = None) -> subprocess.CompletedProcess:
        argv = ['bash', str(SCRIPT), *map(str, args)]
        if config is not None:
            argv += ['--config', str(config)]
        return subprocess.run(argv, capture_output=True, text=True, env=GIT_ENV)

    # --- argument and configuration handling -----------------------------

    def test_help_prints_usage_and_exits_zero(self):
        for flag in ['-h', '--help']:
            with self.subTest(flag=flag):
                result = self.sync(flag)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('Usage: tools/desk-sync.sh', result.stdout)
                for key in ['DESK_REPO_URL', 'DESK_LOCAL_DIR', 'DESK_BRANCH']:
                    self.assertIn(key, result.stdout)

    def test_unknown_argument_exits_two_with_usage_on_stderr(self):
        result = self.sync('--fetch-everything')
        self.assertEqual(result.returncode, 2)
        self.assertIn('unbekanntes Argument: --fetch-everything', result.stderr)
        self.assertIn('Usage: tools/desk-sync.sh', result.stderr)

    def test_config_flag_without_value_exits_two(self):
        result = self.sync('--config')
        self.assertEqual(result.returncode, 2)
        self.assertIn('--config erwartet einen Pfad', result.stderr)

    def test_missing_config_file_exits_one_and_names_the_example(self):
        result = self.sync(config=self.tmp / 'absent.conf')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Konfiguration fehlt', result.stderr)
        self.assertIn('tools/desk-sync.conf.example', result.stderr)

    def test_each_required_key_is_enforced(self):
        cases = {
            'DESK_REPO_URL': self.config(local=self.local, name='no-url.conf'),
            'DESK_LOCAL_DIR': self.config(url=self.remote.as_uri(), name='no-dir.conf'),
            'DESK_BRANCH': self.config(url=self.remote.as_uri(), local=self.local,
                                       branch=None, name='no-branch.conf'),
        }
        for key, config in cases.items():
            with self.subTest(key=key):
                result = self.sync(config=config)
                self.assertEqual(result.returncode, 1)
                self.assertIn(f'Fehler: {key} ist in', result.stderr)
                self.assertFalse(self.local.exists())

    def test_empty_required_key_is_treated_as_unset(self):
        result = self.sync(config=self.config(url='', local=self.local, name='empty-url.conf'))
        self.assertEqual(result.returncode, 1)
        self.assertIn('DESK_REPO_URL ist in', result.stderr)

    # --- status mode ------------------------------------------------------

    def test_status_reports_configuration_and_missing_clone(self):
        result = self.sync('--status', config=self.full_config())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Remote: ' + self.remote.as_uri(), result.stdout)
        self.assertIn('Local:  ' + str(self.local), result.stdout)
        self.assertIn('Branch: ' + BRANCH, result.stdout)
        self.assertIn('Status: not cloned', result.stdout)
        self.assertFalse(self.local.exists())

    def test_status_on_existing_clone_reports_branch_without_contacting_remote(self):
        config = self.full_config()
        self.assertEqual(self.sync(config=config).returncode, 0)
        # Removing the remote proves --status neither fetches nor pulls.
        git('remote', 'remove', 'origin', cwd=self.local)
        result = self.sync('--status', config=config)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('## ' + BRANCH, result.stdout)

    # --- clone, fast-forward, refusal ------------------------------------

    def test_first_run_clones_the_requested_branch_and_creates_parents(self):
        self.assertFalse(self.local.parent.exists())
        result = self.sync(config=self.full_config())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.local / '.git').is_dir())
        self.assertEqual(git('rev-parse', '--abbrev-ref', 'HEAD', cwd=self.local), BRANCH)
        self.assertEqual(git('rev-parse', 'HEAD', cwd=self.local),
                         git('rev-parse', 'HEAD', cwd=self.remote))

    def test_second_run_without_remote_changes_reports_up_to_date(self):
        config = self.full_config()
        self.assertEqual(self.sync(config=config).returncode, 0)
        before = git('rev-parse', 'HEAD', cwd=self.local)
        result = self.sync(config=config)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Desk-Repo ist aktuell', result.stdout)
        self.assertEqual(git('rev-parse', 'HEAD', cwd=self.local), before)

    def test_behind_checkout_is_fast_forwarded(self):
        config = self.full_config()
        self.assertEqual(self.sync(config=config).returncode, 0)
        expected = self.commit(self.remote, 'zweite.txt', 'zwei')
        result = self.sync(config=config)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git('rev-parse', 'HEAD', cwd=self.local), expected)
        self.assertTrue((self.local / 'zweite.txt').is_file())

    def test_wrong_local_branch_is_refused_without_fetching(self):
        config = self.full_config()
        self.assertEqual(self.sync(config=config).returncode, 0)
        git('checkout', '-q', '-b', 'eigener-zweig', cwd=self.local)
        before = git('rev-parse', 'HEAD', cwd=self.local)
        result = self.sync(config=config)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Checkout ist auf Branch 'eigener-zweig'", result.stderr)
        self.assertIn(f"erwartet '{BRANCH}'", result.stderr)
        self.assertEqual(git('rev-parse', 'HEAD', cwd=self.local), before)

    def test_diverged_checkout_is_refused_and_left_untouched(self):
        config = self.full_config()
        self.assertEqual(self.sync(config=config).returncode, 0)
        local_head = self.commit(self.local, 'lokal.txt', 'lokal')
        self.commit(self.remote, 'entfernt.txt', 'entfernt')
        result = self.sync(config=config)
        self.assertEqual(result.returncode, 1)
        self.assertIn(f'lokaler Stand divergiert von origin/{BRANCH}', result.stderr)
        self.assertEqual(git('rev-parse', 'HEAD', cwd=self.local), local_head)
        self.assertFalse((self.local / 'entfernt.txt').exists())

    def test_ahead_only_checkout_is_also_refused(self):
        config = self.full_config()
        self.assertEqual(self.sync(config=config).returncode, 0)
        local_head = self.commit(self.local, 'lokal.txt', 'lokal')
        result = self.sync(config=config)
        self.assertEqual(result.returncode, 1)
        self.assertIn('divergiert', result.stderr)
        self.assertEqual(git('rev-parse', 'HEAD', cwd=self.local), local_head)

    def test_flag_order_does_not_matter(self):
        config = self.full_config()
        self.assertEqual(self.sync(config=config).returncode, 0)
        after = subprocess.run(['bash', str(SCRIPT), '--config', str(config), '--status'],
                               capture_output=True, text=True, env=GIT_ENV)
        self.assertEqual(after.returncode, 0, after.stderr)
        self.assertIn('Config: ' + str(config), after.stdout)
        self.assertIn('## ' + BRANCH, after.stdout)

    def test_missing_branch_on_remote_fails_the_clone(self):
        config = self.config(url=self.remote.as_uri(), local=self.local, branch='kein-zweig')
        result = self.sync(config=config)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.local / '.git').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
