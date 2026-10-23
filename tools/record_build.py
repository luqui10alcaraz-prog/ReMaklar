#!/usr/bin/env python3
"""Record actual build/test evidence without bundling binaries.
SPDX-License-Identifier: MIT
"""
import hashlib
import json
import platform
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
record = {
    'date': '2026-10-23',
    'qemu': json.loads((root / 'patches/qemu-0.10.6/manifest.json').read_text()),
    'host': platform.platform(),
    'gcc': subprocess.check_output(['gcc', '--version'], text=True).splitlines()[0],
    'executables': [],
    'fixture_results': json.loads((root / 'logs/ppc-fixtures/results.json').read_text()),
    'original_main_results': json.loads((root / 'logs/original-main/results.json').read_text()),
    'full_original_process_supported': False,
    'darwin6_host_validated': False
}
for directory in ['qemu-linux32', 'qemu-linux32-clean']:
    exe = root / 'build' / directory / 'ppc-darwin-user/qemu-ppc'
    record['executables'].append({'path': str(exe.relative_to(root)),
        'sha256': hashlib.sha256(exe.read_bytes()).hexdigest(), 'bytes': exe.stat().st_size,
        'format': subprocess.check_output(['file', '-b', str(exe)], text=True).strip()})
dest = root / 'reports'
dest.mkdir(exist_ok=True)
(dest / 'remaklar-0.01.json').write_text(json.dumps(record, indent=2) + '\n')
print('Recorded build hashes and test results in reports/remaklar-0.01.json')
