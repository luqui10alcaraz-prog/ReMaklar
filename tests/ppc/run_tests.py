#!/usr/bin/env python3
"""Run each PPC fixture in a separate, time-limited host process.
SPDX-License-Identifier: MIT
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
exe = Path(os.environ.get('REMAKLAR_EXECUTOR', root / 'build/qemu-linux32/ppc-darwin-user/qemu-ppc'))
logdir = Path(os.environ.get('REMAKLAR_FIXTURE_LOGDIR', root / 'logs/ppc-fixtures'))
logdir.mkdir(parents=True, exist_ok=True)
manifest = json.loads((root / 'build/fixtures/manifest.json').read_text())
results = []
for case in manifest:
    name = case['name']
    image = root / 'build/fixtures' / (name + '.macho')
    run = subprocess.run([str(exe), str(image)], cwd=logdir, timeout=10,
                         env={'PATH': os.defpath, 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC',
                              'REMAKLAR_TRACE': '1'}, capture_output=True)
    (logdir / (name + '.stdout')).write_bytes(run.stdout)
    (logdir / (name + '.stderr')).write_bytes(run.stderr)
    trace = logdir / 'remaklar-tcg.log'
    if trace.exists():
        trace.replace(logdir / (name + '.tcg.log'))
    ok = (run.returncode == case['exit'] and run.stdout == case['stdout'].encode()
          and case['stderr_contains'].encode() in run.stderr)
    results.append({'name': name, 'pass': ok, 'exit': run.returncode,
                    'sha256': hashlib.sha256(image.read_bytes()).hexdigest()})
    print(('PASS' if ok else 'FAIL'), name, 'exit=' + str(run.returncode))
(logdir / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
sys.exit(0 if all(r['pass'] for r in results) else 1)
