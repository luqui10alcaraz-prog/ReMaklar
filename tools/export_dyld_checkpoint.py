#!/usr/bin/env python3
"""Export the committed dyld experiment and its verified checkpoint.
SPDX-License-Identifier: MIT
"""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
repo = root / 'experiments/qemu-0.10.6'
base = '8fedcc15ebe5ad48d831f97c8006ce50bbee04be'
head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
assert head != base, 'Commit the QEMU adaptation first'
patch = subprocess.check_output(['git', '-C', str(repo), 'diff', '--binary', base, head])
report = json.loads((root / 'logs/dynamic-regression/results.json').read_text())
assert report['pass'], 'Dynamic tests did not pass'
incremental = json.loads((root / 'reports/dyld-incremental.json').read_text())
assert incremental['pass']
static = json.loads((root / 'logs/ppc-fixtures/results.json').read_text())
assert len(static) == 11 and all(r['pass'] for r in static)
manifest = {'base_commit': base, 'experimental_commit': head,
            'branch': 'remaklar/0.02-dyld', 'patch_sha256': hashlib.sha256(patch).hexdigest()}
dest = root / 'patches/qemu-0.10.6'
(dest / '0002-dyld-startup.patch').write_bytes(patch)
(dest / 'dyld-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
report.update({'checkpoint': '0.02-dyld', 'source': manifest,
               'incremental_pass': incremental['pass'],
               'static_fixtures': static,
               'previous_main_only_regression': 'logs/regression-clean-0.02-console.txt',
               'scope': 'Linux i386 on WSL; root low-address lab; Darwin port pending',
               'sample_source': 'Apple Darwin 6.0.2 CD, not a verified retail Jaguar image'})
(root / 'reports/remaklar-dyld.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
