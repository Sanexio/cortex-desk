"""Aggregate-only adapter. Never import the pipeline: imports can create archive files."""
from __future__ import annotations

import fcntl
import json
import math
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()
BASE = Path(__file__).resolve().parent
SKILL = Path(os.environ.get('TOSORT_SKILL_ROOT', Path.home() / 'Cortex/Desk/_skills/archiv-tosort'))
ARCHIVE = Path(os.environ.get('ARCHIV_ROOT', SKILL.parent.parent / 'ARCHIV'))
STATE = Path(os.environ.get('TOSORT_STATE_DIR', BASE / 'state'))
PYTHON = os.environ.get('TOSORT_PYTHON', sys.executable)
STATUSES = {'running', 'awaiting_review', 'failed', 'not_measurable'}
Thread = threading.Thread
STEPS = {'scan', 'hash', 'registers', 'learning', 'routing', 'review', None}


def utc():
    return datetime.now(timezone.utc).isoformat()


def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None or parsed.timestamp() > time.time() + 60:
            return None
        return parsed.astimezone(timezone.utc).isoformat()
    except (ValueError, OverflowError):
        return None


def measure(path, excluded=()):
    """Fail the entire pool on partial reads; never return paths or names."""
    result = {'count': None, 'oldest_age_seconds': None, 'status': 'not_measurable'}
    count, oldest = 0, None
    now = time.time()
    try:
        def walk(folder):
            nonlocal count, oldest
            if folder.is_symlink():
                raise OSError('link')
            with os.scandir(folder) as entries:
                for entry in entries:
                    if entry.name in {'.DS_Store', 'README.md', '_TRASH'} | set(excluded):
                        continue
                    info = entry.stat(follow_symlinks=False)
                    if stat.S_ISLNK(info.st_mode):
                        raise OSError('link')
                    if stat.S_ISDIR(info.st_mode):
                        walk(Path(entry.path))
                    elif stat.S_ISREG(info.st_mode):
                        if not math.isfinite(info.st_mtime) or info.st_mtime > now:
                            raise OSError('future timestamp')
                        count += 1
                        oldest = min(oldest, info.st_mtime) if oldest is not None else info.st_mtime
                    else:
                        raise OSError('unsupported entry')
        walk(path)
        return {'count': count, 'oldest_age_seconds': int(now - oldest) if oldest is not None else None,
                'status': 'measured'}
    except OSError:
        return result


def last_routing(root):
    """mtime of readable existing Routing_YYYYMMDD.csv, NOT proof of successful execution."""
    latest = None
    try:
        base = root / '_AI_META/TOSORT'
        if not base.is_dir() or base.is_symlink():
            return None
        for folder, dirs, files in os.walk(base, onerror=lambda exc: (_ for _ in ()).throw(exc), followlinks=False):
            if any((Path(folder) / d).is_symlink() for d in dirs):
                return None
            for name in files:
                if len(name) != 20 or not name.startswith('Routing_') or not name[8:16].isdigit() or not name.endswith('.csv'):
                    continue
                path = Path(folder) / name
                if path.is_symlink():
                    return None
                with path.open('rb') as handle:
                    handle.read(0)
                    modified = os.fstat(handle.fileno()).st_mtime
                if modified > time.time() or not math.isfinite(modified):
                    return None
                latest = max(latest, modified) if latest is not None else modified
        return datetime.fromtimestamp(latest, timezone.utc).isoformat() if latest is not None else None
    except (OSError, ValueError, OverflowError):
        return None


def run_state():
    unknown = {'status': 'not_measurable', 'step': None, 'started_at': None, 'finished_at': None}
    try:
        raw = json.loads((STATE / 'run.json').read_text())
        if not isinstance(raw, dict) or raw.get('status') not in STATUSES or raw.get('step') not in STEPS:
            return unknown
        start = timestamp(raw.get('started_at'))
        end = timestamp(raw.get('finished_at'))
        if not start or (raw['status'] != 'running' and not end):
            return unknown
        if raw['status'] == 'running':
            with (STATE / 'run.lock').open('r') as lock:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return unknown  # interrupted run; never assume success after restart
                except BlockingIOError:
                    pass
        return {'status': raw['status'], 'step': raw['step'], 'started_at': start, 'finished_at': end}
    except (OSError, ValueError, TypeError):
        return unknown


def enabled():
    return os.environ.get('TOSORT_ENABLE_RUN') == '1'


@router.get('/status')
def status():
    return {'pools': {
        'inbox': measure(ARCHIVE / 'TOSORT', {'_KLAEREN'}),
        'clarification': measure(ARCHIVE / 'TOSORT/_KLAEREN'),
        'review': measure(ARCHIVE / '_AI_META/TOSORT_REVIEW'),
    }, 'last_routing_at': last_routing(ARCHIVE), 'run': run_state(), 'can_start': enabled()}


@router.get('/lauf/status')
def lauf_status():
    return run_state()


def save_state(data):
    target = STATE / ('run-' + uuid.uuid4().hex + '.tmp')
    target.write_text(json.dumps(data), encoding='utf-8')
    target.replace(STATE / 'run.json')


def commands(run_id):
    scripts = SKILL / 'scripts'
    def cmd(name, *args):
        return [PYTHON, '-B', str(scripts / name), *map(str, args)]
    sequence = [('scan', cmd('archiv_index.py', 'scan')),
                ('hash', cmd('archiv_index.py', 'hash')),
                ('registers', cmd('archiv_index.py', 'registers'))]
    # Delegate optional learning selection entirely to the existing helper.
    if list((Path.home() / 'Downloads').glob('TOSORT_Umbenennung_*.csv')):
        sequence.append(('learning', cmd('lern_diff.py')))
    stamp = datetime.now().strftime('%Y%m%d')
    out = ARCHIVE / '_AI_META/TOSORT' / (stamp + '_Routing_Dashboard_' + run_id)
    sequence += [('routing', cmd('tosort_route.py', '--input', ARCHIVE / 'TOSORT', '--out', out)),
                 ('review', cmd('downloads_liste.py', '--routing', out / ('Routing_' + stamp + '.csv'),
                                '--datum', stamp, '--neue-generation', '--personenbezug', '--lauf', 'Dashboard_' + run_id))]
    return sequence


def worker(lock, writer_lock, data, sequence):
    try:
        env = dict(os.environ, ARCHIV_ROOT=str(ARCHIVE), PYTHONDONTWRITEBYTECODE='1')
        for step, argv in sequence:
            data['step'] = step
            save_state(data)
            # No capture/logging: output can contain patient data and source paths.
            subprocess.run(argv, cwd=SKILL, env=env, stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        data['status'] = 'awaiting_review'
    except Exception:
        data['status'] = 'failed'
    finally:
        data['finished_at'] = utc()
        try:
            save_state(data)
        finally:
            writer_lock.unlink(missing_ok=True)
            lock.close()


@router.post('/lauf', status_code=202)
def start(request: Request):
    if not enabled():
        raise HTTPException(403, 'Laufstart nicht aktiviert')
    # The host supplies authentication. Require a same-origin custom header too.
    if request.headers.get('x-tosort-action') != 'start' or request.headers.get('sec-fetch-site') == 'cross-site':
        raise HTTPException(403, 'Laufstart nicht erlaubt')
    lock = None
    writer_lock = ARCHIVE / '_AI_META/ARCHIV_INDEX/logs/.archiv_index_writer.lock'
    owns_writer = False
    try:
        if measure(ARCHIVE / 'TOSORT', {'_KLAEREN'})['status'] != 'measured':
            raise HTTPException(503, 'Eingang nicht messbar')
        sequence = commands(uuid.uuid4().hex)
        if not all(Path(argv[2]).is_file() for _, argv in sequence):
            raise HTTPException(503, 'Pipeline nicht verfügbar')
        STATE.mkdir(parents=True, exist_ok=True)
        lock = (STATE / 'run.lock').open('a+')
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise HTTPException(409, 'Lauf bereits aktiv') from None
        # Same PID-file protocol as index_tick/ocr_drain. Stale locks require review.
        try:
            fd = os.open(writer_lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            raise HTTPException(409, 'Archiv-Writer gesperrt') from None
        owns_writer = True
        with os.fdopen(fd, 'w') as handle:
            handle.write(str(os.getpid()))
        data = {'status': 'running', 'step': None, 'started_at': utc(), 'finished_at': None}
        save_state(data)
        thread = Thread(target=worker, args=(lock, writer_lock, data.copy(), sequence), daemon=False)
        thread.start()
        return data
    except Exception as exc:
        if owns_writer:
            writer_lock.unlink(missing_ok=True)
        if lock:
            lock.close()
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(503, 'Laufstart nicht verfügbar') from None
