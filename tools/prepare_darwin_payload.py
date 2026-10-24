#!/usr/bin/env python3
"""Package local sources and unchanged samples for an offline guest CD.
SPDX-License-Identifier: MIT
"""
import io
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

root = Path(__file__).resolve().parents[1]
out = root / 'build/darwin-payload'
out.mkdir(parents=True, exist_ok=True)
repo = root / 'experiments/qemu-0.10.6'
archive = subprocess.check_output(['git', '-C', str(repo), 'archive', '--format=tar',
                                   '--prefix=remaklar/experiments/qemu-0.10.6/', 'HEAD'])
changed = subprocess.check_output(['git', '-C', str(repo), 'diff', '--name-only', '-z', 'HEAD']).decode().split('\0')
changed += subprocess.check_output(['git', '-C', str(repo), 'ls-files', '--others', '--exclude-standard', '-z']).decode().split('\0')
samples = ['usr/bin/true', 'usr/bin/false', 'bin/echo', 'bin/cat', 'bin/ls', 'bin/pwd', 'usr/lib/dyld',
           'usr/lib/libSystem.B.dylib', 'usr/lib/system/libmathCommon.A.dylib', 'usr/lib/libobjc.A.dylib',
           'System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation']
with tarfile.open(out / 'source.tgz', 'w:gz', format=tarfile.GNU_FORMAT) as dest:
    with tarfile.open(fileobj=io.BytesIO(archive)) as src:
        for entry in src:
            dest.addfile(entry, src.extractfile(entry) if entry.isfile() else None)
    for name in sorted(set(changed) - {''}):
        if not (repo / name).is_file():
            raise ValueError('Payload overlay does not support deleted paths: ' + name)
        dest.add(repo / name, arcname='remaklar/experiments/qemu-0.10.6/' + name)
    for folder in ['scripts', 'tests/ppc']:
        for path in (root / folder).iterdir():
            if path.is_file():
                dest.add(path, arcname='remaklar/' + path.relative_to(root).as_posix())
    for name in samples:
        dest.add(root / 'research/samples-local' / name,
                 arcname='remaklar/research/samples-local/' + name)
    for path in (root / 'build/fixtures').glob('*.macho'):
        dest.add(path, arcname='remaklar/build/fixtures/' + path.name)
    dest.add(root / 'build/utility-cases.tsv', arcname='remaklar/build/utility-cases.tsv')
    for name in ['filesystem-probe.macho', 'objc-runtime-probe.macho']:
        dest.add(root / 'build' / name, arcname='remaklar/build/' + name)
    dest.add(root / 'research/samples-local/fixtures',
             arcname='remaklar/research/samples-local/fixtures')
manifest = {'qemu_commit': subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip(),
            'qemu_working_overlay': sorted(set(changed) - {''}),
            'qemu_diff_sha256': hashlib.sha256(subprocess.check_output(['git', '-C', str(repo), 'diff', '--binary', 'HEAD'])).hexdigest(),
            'source_tgz_sha256': hashlib.sha256((out / 'source.tgz').read_bytes()).hexdigest(),
            'samples': {s: hashlib.sha256((root / 'research/samples-local' / s).read_bytes()).hexdigest() for s in samples}}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
