#!/usr/bin/env python3
"""Development probe of real dyld/startup. Records failure as well as success.
SPDX-License-Identifier: MIT
"""
import hashlib
import json
import os
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2]
exe = root / 'build/qemu-linux32/ppc-darwin-user/qemu-ppc'
guestroot = root / 'research/samples-local'
log = root / 'logs/dynamic'
log.mkdir(parents=True, exist_ok=True)
name = os.environ.get('REMAKLAR_PROGRAM', 'true')
assert name in ('true', 'false', 'echo')
program = guestroot / ('bin/echo' if name == 'echo' else 'usr/bin/' + name)
command = [str(exe), '--root', str(guestroot), str(program)]
if name == 'echo':
    command += ['ReMaklar', 'original', 'startup']
try:
    run = subprocess.run(command, capture_output=True, timeout=120, cwd=log,
        env={'PATH': os.defpath, 'LANG': 'C', 'TZ': 'UTC', 'REMAKLAR_TRACE': '1'})
    status = run.returncode
    stdout, stderr = run.stdout, run.stderr
except subprocess.TimeoutExpired as exc:
    status, stdout, stderr = 'timeout', exc.stdout or b'', exc.stderr or b''
(log / (name + '.stdout')).write_bytes(stdout)
(log / (name + '.stderr')).write_bytes(stderr)
trace = log / 'remaklar-tcg.log'
if trace.exists():
    trace.replace(log / (name + '.tcg.log'))
result = {'program': name, 'command': command, 'exit': status,
          'program_sha256': hashlib.sha256(program.read_bytes()).hexdigest(),
          'dyld_sha256': hashlib.sha256((guestroot / 'usr/lib/dyld').read_bytes()).hexdigest(),
          'host_uid': os.getuid(), 'scope': 'original dyld entry, no main override'}
(log / 'attempts').mkdir(exist_ok=True)
attempt = len(list((log / 'attempts').glob(name + '-*.json'))) + 1
stem = log / 'attempts' / f'{name}-{attempt:03d}'
stem.with_suffix('.stderr').write_bytes(stderr)
stem.with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
(log / (name + '.result.json')).write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
print(stderr.decode(errors='replace')[-5000:])
