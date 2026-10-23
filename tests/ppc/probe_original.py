#!/usr/bin/env python3
"""Execute only the original true/false main body, not dyld/startup.
Verifies the complete instruction pattern and original _exit import relation.
SPDX-License-Identifier: MIT
"""
import hashlib
import json
import os
import struct
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'tools'))
from macho_inventory import inventory

exe = Path(os.environ.get('REMAKLAR_EXECUTOR', root / 'build/qemu-linux32/ppc-darwin-user/qemu-ppc'))
out = root / 'logs/original-main'
out.mkdir(parents=True, exist_ok=True)
results = []
for name, expected in [('true', 0), ('false', 1)]:
    original = root / 'research/samples-local/usr/bin' / name
    fat = original.read_bytes()
    report = inventory(fat)
    (out / (name + '.inventory.json')).write_text(json.dumps(report, indent=2))
    slice_info = next(s for s in report['slices'] if s['cputype'] == 18)
    data = fat[slice_info['offset']:slice_info['offset'] + slice_info['size']]
    ppc_report = slice_info['analysis']
    # Stripped _main: identify the complete simple main sequence and verify
    # its relative call resolves to the _exit stub via LC_DYSYMTAB, not a guess.
    exit_stub = next(s['address'] for s in ppc_report['stubs'] if s['symbol'] == '_exit')
    text = next(s for s in ppc_report['segments'] if s['name'] == '__TEXT')
    pattern = struct.pack('>4I', 0x7c0802a6, 0x38600000 | expected, 0x90010008, 0x9421ffb0)
    candidates = []
    for off in range(text['fileoff'], text['fileoff'] + text['filesize'] - 19, 4):
        if data[off:off + 16] != pattern:
            continue
        branch, = struct.unpack_from('>I', data, off + 16)
        disp = branch & 0x03fffffc
        if disp & 0x02000000:
            disp -= 0x04000000
        pc = text['vmaddr'] + off - text['fileoff']
        if branch & 0xfc000003 == 0x48000001 and pc + 16 + disp == exit_stub:
            candidates.append(pc)
    if len(candidates) != 1:
        raise RuntimeError(f'{name}: cannot uniquely identify main: {candidates}')
    entry = candidates[0]
    command = [str(exe), '--probe-main', f'{entry:x}', f'{exit_stub:x}', str(original)]
    run = subprocess.run(command, cwd=out, capture_output=True, timeout=10,
                         env={'PATH': os.defpath, 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC',
                              'REMAKLAR_TRACE': '1'})
    (out / (name + '.stdout')).write_bytes(run.stdout)
    (out / (name + '.stderr')).write_bytes(run.stderr)
    trace = out / 'remaklar-tcg.log'
    if trace.exists():
        trace.replace(out / (name + '.tcg.log'))
    ok = run.returncode == expected and not run.stdout and b'reached _exit bridge' in run.stderr
    results.append({'name': name, 'pass': ok, 'scope': 'main-only, native exit bridge, no dyld/startup',
                    'exit': run.returncode, 'main': hex(entry), 'exit_stub': hex(exit_stub),
                    'original_fat_sha256': hashlib.sha256(fat).hexdigest(),
                    'original_ppc_slice_sha256': hashlib.sha256(data).hexdigest(), 'command': command})
    print(('PASS' if ok else 'FAIL'), name, 'main-only', 'exit=' + str(run.returncode))
(out / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
sys.exit(0 if all(r['pass'] for r in results) else 1)
