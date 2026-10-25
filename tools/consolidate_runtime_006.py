#!/usr/bin/env python3
"""Preserve 0.06 evidence without inventing the missing historical cold boot.
Unlike export_runtime_checkpoint.py, this does not require/claim a 0.06 snapshot.
SPDX-License-Identifier: MIT
"""
import hashlib
import json
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
dest = root / 'reports/runtime-006'
report = root / 'reports/remaklar-0.06.json'
if dest.exists() or report.exists():
    raise SystemExit('Refusing to replace existing evidence')
native = root / 'logs/runtime-native-005'
linux = root / 'logs/runtime-linux-006'
new = root / 'logs/native-007-session'
expected = {'objc-smoke': 'Objective-C PPC OK\n', 'cf-smoke': 'CoreFoundation PPC OK\n',
            'mach-runtime': 'Mach runtime contracts OK\n',
            'graphics-contracts': 'Graphics boundary contracts OK\n',
            'ptrace-host': 'request=c000 result=-1 errno=1\nrequest=b000 result=-1 errno=1\n'}
cases = [(name+'-'+cohort, value) for name, value in expected.items()
         for cohort in ['darwin', 'jaguar']]
cases += [('foundation', 'Foundation PPC OK\n'), ('quartz', 'Quartz PPC bitmap OK\n')]
for name, value in cases:
    assert (native/(name+'.status')).read_text().strip() == 'status=0'
    assert (native/(name+'.stdout')).read_text() == value
    stderr = (native/(name+'.stderr')).read_text()
    assert 'startup: entered original executable' in stderr
    assert 'unsupported' not in stderr and 'probe-main:' not in stderr
old_linux = json.loads((linux/'results.json').read_text())
assert len(old_linux) == 12 and all(r['pass'] for r in old_linux)
pixels = b'P6\n64 48\n255\n' + b''.join(
    b'\xff\0\0' if 16 <= x < 48 and 12 <= y < 36 else b'\0\0\xff'
    for y in range(48) for x in range(64))
assert (native/'quartz.ppm').read_bytes() == pixels == (linux/'quartz.ppm').read_bytes()
fixtures = json.loads((new/'fixtures-006/results.json').read_text())
assert len(fixtures) == 11 and all(r['pass'] for r in fixtures)
dynamic = json.loads((new/'dynamic-006/results.json').read_text())
dest.mkdir()
for label, folder in [('historical-darwin', native), ('historical-linux', linux)]:
    target = dest/label
    target.mkdir()
    for p in folder.iterdir():
        if p.is_file():
            shutil.copyfile(p, target/p.name)
for name in ['patch-verification.json', 'configure-006.txt', 'build-006.txt',
             'fixtures-006.txt', 'dynamic-006.txt']:
    shutil.copyfile(new/name, dest/name)
for name in ['fixtures-006', 'dynamic-006']:
    shutil.copytree(new/name, dest/name)
data = {
    'checkpoint': '0.06-runtime',
    'source': json.loads((root/'patches/qemu-0.10.6/runtime-manifest.json').read_text()),
    'reconstructed_tree': json.loads((new/'patch-verification.json').read_text()),
    'clean_linux_build': 'PASS',
    'new_fixtures': fixtures,
    'new_dynamic_runner': dynamic,
    'new_dynamic_status': 'PASS' if dynamic['pass'] else 'BLOCKED by low-address mapping on this host; runner records FAIL',
    'historical_runtime': {'classification': 'historical logs validated, not re-executed by this tool',
                           'darwin_cases': 12, 'linux_cases': 12, 'bitmap_all_pixels': True},
    'historical_cold_boot': 'NOT RUN: expected exported evidence absent',
    'snapshot_006': 'NOT RUN: expected verified snapshot absent',
    'windowserver': 'historical entry reached; FAIL unsupported fork syscall 2',
    'scope': 'PPC translation on Darwin/Linux i386; not native Jaguar frameworks',
    'files_sha256': {str(p.relative_to(dest)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in dest.rglob('*') if p.is_file()}
}
report.write_text(json.dumps(data, indent=2)+'\n')
print('0.06 source/build/fixture checkpoint preserved; cold boot and snapshot explicitly pending')
