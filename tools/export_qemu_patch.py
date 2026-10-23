#!/usr/bin/env python3
"""Export only the committed QEMU adaptation, preserving bytes/newlines.
SPDX-License-Identifier: MIT
"""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
repo = root / 'experiments/qemu-0.10.6'
base = '9eab386edbf8cf002a731f8204a156f243a47a57'
head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
patch = subprocess.check_output(['git', '-C', str(repo), 'diff', '--binary', base, head])
dest = root / 'patches/qemu-0.10.6'
dest.mkdir(parents=True, exist_ok=True)
(dest / '0001-remaklar-0.01.patch').write_bytes(patch)
manifest = {'upstream': 'https://github.com/qemu/qemu.git', 'tag': 'v0.10.6',
            'base_commit': base, 'experimental_commit': head,
            'patch_sha256': hashlib.sha256(patch).hexdigest()}
(dest / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
