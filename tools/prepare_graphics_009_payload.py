#!/usr/bin/env python3
"""Package the 0.09 runtime, callers and preserved local regression inputs.
SPDX-License-Identifier: MIT
"""
import argparse
from pathlib import Path
import tarfile
p=argparse.ArgumentParser();p.add_argument('output',type=Path);args=p.parse_args()
if args.output.exists():raise SystemExit('Refusing to replace existing payload')
root=Path(__file__).resolve().parents[1]
files={n:root/'build/qemu-009-source/darwin-user/remaklar'/n for n in ['darwin-kernel.c','bootstrap-main.c','bootstrap.h']}
files.update({n:root/'tests/ppc'/n for n in ['signals-runtime.c','statfs-runtime.c','iokit-open-runtime.c','getattrlist-runtime.c','graphics-system-runtime.c','process-runtime.c','access-runtime.c','exec-runtime.c','iokit-runtime.c','run_graphics_008.pl','run_utilities.pl','run_filesystem.pl']})
files.update({'native/'+n:root/'tests/native-i386'/n for n in ['objc.m','cf.c','images.h']})
files.update({n:root/'build'/n for n in ['utility-cases.tsv','filesystem-probe.macho']})
files['samples']=root/'research/samples-local'
files['run.sh']=root/'scripts/darwin6-graphics-009-followup.sh'
with tarfile.open(args.output,'w:gz',format=tarfile.USTAR_FORMAT) as t:
    for n,path in files.items():t.add(path,arcname='graphics009-followup/'+n)
print(args.output)
