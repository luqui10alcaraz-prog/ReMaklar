#!/usr/bin/env python3
"""Package final patched sources and own probes; never includes Apple binaries.
SPDX-License-Identifier: MIT
"""
import argparse
import io
from pathlib import Path
import tarfile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, required=True,
                    help='QEMU checkout with checkpoint 0.10-graphics applied')
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
source = args.source.resolve() / 'darwin-user/remaklar'
files = [(source / name, name) for name in
         ('darwin-kernel.c', 'mach-native.inc', 'bootstrap-main.c', 'bootstrap.h')]
for name in ('mach010-runtime', 'shm010-runtime', 'credentials010-runtime',
             'mmap010-runtime', 'iokit-cstring-runtime', 'iokit010-open-runtime',
             'clock010-runtime', 'framebuffer010-runtime'):
    files.append((root / 'tests/ppc' / (name + '.c'), name + '.c'))
files += [(root / 'tests/ppc/run_graphics_008.pl', 'probe.pl'),
          (root / 'tests/ppc/run_graphics_010_joint.pl', 'joint.pl'),
          (root / 'scripts/darwin6-graphics-010-reproduce.sh', 'run.sh')]
for path, _ in files:
    if not path.is_file():
        parser.error('Required source missing: ' + str(path))
if args.output.exists():
    parser.error('Output already exists: ' + str(args.output))
args.output.parent.mkdir(parents=True, exist_ok=True)
with tarfile.open(args.output, 'w:gz', format=tarfile.USTAR_FORMAT) as archive:
    for path, name in files:
        data = path.read_bytes().replace(b'\r\n', b'\n')
        entry = tarfile.TarInfo('graphics010-reproduce/' + name)
        entry.size = len(data)
        entry.mode = 0o644
        archive.addfile(entry, io.BytesIO(data))
print(args.output)
