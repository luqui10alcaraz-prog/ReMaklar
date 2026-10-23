#!/usr/bin/env python3
"""Assert original dyld/startup and BSD exit, without a main/exit bridge.
SPDX-License-Identifier: MIT
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'tools'))
from macho_inventory import inventory

exe = Path(os.environ.get('REMAKLAR_EXECUTOR', root / 'build/qemu-linux32/ppc-darwin-user/qemu-ppc'))
guest = root / 'research/samples-local'
logs = Path(os.environ.get('REMAKLAR_DYNAMIC_LOGDIR', root / 'logs/dynamic-regression'))
logs.mkdir(parents=True, exist_ok=True)
paths = ['usr/bin/true', 'usr/bin/false', 'usr/lib/dyld',
         'usr/lib/libSystem.B.dylib', 'usr/lib/system/libmathCommon.A.dylib']
hashes = {p: hashlib.sha256((guest / p).read_bytes()).hexdigest() for p in paths}
results = []
for name, expected in [('true', 0), ('false', 1)]:
    image = guest / 'usr/bin' / name
    ppc = next(s['analysis'] for s in inventory(image.read_bytes())['slices'] if s['cputype'] == 18)
    entry = ppc['entry']
    command = [str(exe), '--root', str(guest), str(image)]
    # Write TCG traces on Linux storage, then copy once to the Windows workspace.
    with tempfile.TemporaryDirectory(prefix='remaklar-tcg-') as work:
        try:
            run = subprocess.run(command, capture_output=True, timeout=120, cwd=work,
                                 env={'PATH': os.defpath, 'LANG': 'C', 'TZ': 'UTC', 'REMAKLAR_TRACE': '1'})
            status, stdout, stderr = run.returncode, run.stdout, run.stderr
        except subprocess.TimeoutExpired as err:
            status, stdout, stderr = 'timeout', err.stdout or b'', err.stderr or b''
        trace = Path(work) / 'remaklar-tcg.log'
        if trace.exists():
            shutil.copyfile(trace, logs / (name + '.tcg.log'))
    (logs / (name + '.stdout')).write_bytes(stdout)
    (logs / (name + '.stderr')).write_bytes(stderr)
    checks = {
        'exit': status == expected,
        'stdout_empty': stdout == b'',
        'original_entry': stderr.count(f'startup: entered original executable at {entry:08x}'.encode()) == 1,
        'no_main_bridge': b'probe-main:' not in stderr,
        'bsd_exit': any(b' r0=1 ' in line for line in stderr.splitlines()),
        'libsystem_loaded': b'guest open ' + str(guest / 'usr/lib/libSystem.B.dylib').encode() in stderr,
        'math_loaded': b'guest open ' + str(guest / 'usr/lib/system/libmathCommon.A.dylib').encode() in stderr,
        'no_unsupported': b'unsupported' not in stderr,
    }
    results.append({'program': name, 'command': command, 'entry': hex(entry),
                    'exit': status, 'checks': checks, 'pass': all(checks.values())})
    print(('PASS' if all(checks.values()) else 'FAIL'), name, status, checks)
unchanged = hashes == {p: hashlib.sha256((guest / p).read_bytes()).hexdigest() for p in paths}
with tempfile.TemporaryDirectory(prefix='remaklar-no-dyld-') as empty_root:
    missing = subprocess.run([str(exe), '--root', empty_root, str(guest / 'usr/bin/true')],
                             capture_output=True, cwd=logs, timeout=10)
    (logs / 'missing-dyld.stderr').write_bytes(missing.stderr)
    missing_ok = missing.returncode != 0 and b'startup: entered' not in missing.stderr
    results.append({'program': 'missing-dyld', 'exit': missing.returncode, 'pass': missing_ok})
    print('PASS' if missing_ok else 'FAIL', 'missing-dyld')
report = {'host_uid': os.getuid(), 'executor_sha256': hashlib.sha256(exe.read_bytes()).hexdigest(),
          'inputs_sha256': hashes, 'inputs_unchanged': unchanged, 'results': results,
          'pass': unchanged and all(r['pass'] for r in results)}
(logs / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
sys.exit(0 if report['pass'] else 1)
