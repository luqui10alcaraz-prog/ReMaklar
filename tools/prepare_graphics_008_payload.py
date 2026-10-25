#!/usr/bin/env python3
"""Package only 0.08 changed sources, tests and local original-media inputs.
SPDX-License-Identifier: MIT
"""
from pathlib import Path
import tarfile
import sys

root=Path(__file__).resolve().parents[1]
source=root/'build/qemu-008-source/darwin-user/remaklar'
closure=root/'build/graphics008-library-closure'
archive=Path(sys.argv[1]) if len(sys.argv)>1 else root/'build/graphics008-final.tgz'
if archive.exists():raise SystemExit('Refusing to replace existing payload')
files={name:source/name for name in ['darwin-kernel.c','bootstrap-main.c','bootstrap.h']}
files.update({name:root/'tests/ppc'/name for name in ['exec-runtime.c','iokit-runtime.c','process-runtime.c','access-runtime.c','run_graphics_008.pl']})
files.update({'run.sh':root/'scripts/darwin6-graphics-008-final.sh',
              'libraries.tgz':closure/'originals.tgz','library-paths.txt':closure/'paths.txt',
              'installer-originals.tgz':root/'build/installer-originals-008.tgz'})
with tarfile.open(archive,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
    for name,path in files.items():tar.add(path,arcname='graphics008-final/'+name)
print(archive)
