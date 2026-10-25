#!/usr/bin/env python3
"""Replay the guest-built PPC runtime/graphics callers on Linux; exact outputs.
SPDX-License-Identifier: MIT
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import sys
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'tools'))
from macho_inventory import inventory
exe=Path(os.environ.get('REMAKLAR_EXECUTOR',root/'build/qemu-linux32-0.06/ppc-darwin-user/qemu-ppc'))
owned=root/'build/runtime-006-owned';logs=root/'logs/runtime-linux-006';logs.mkdir(exist_ok=True)
cohorts={'darwin':root/'research/samples-local','jaguar':root/'research/jaguar-local/Mac OS X Install Disc 1'}
outputs={'objc-smoke':b'Objective-C PPC OK\n','cf-smoke':b'CoreFoundation PPC OK\n',
         'mach-runtime':b'Mach runtime contracts OK\n','graphics-contracts':b'Graphics boundary contracts OK\n',
         'ptrace-host':b'request=c000 result=-1 errno=1\nrequest=b000 result=-1 errno=1\n',
         'foundation':b'Foundation PPC OK\n','quartz':b'Quartz PPC bitmap OK\n'}
cases=[(name,cohort) for name in ['objc-smoke','cf-smoke','mach-runtime','ptrace-host','graphics-contracts'] for cohort in cohorts]
cases += [('foundation','jaguar'),('quartz','jaguar')]
results=[]
for name,cohort in cases:
    image=owned/name;guest=cohorts[cohort];entry=inventory(image.read_bytes())['entry']
    args=[str(exe),'--root',str(guest),str(image)]
    if name=='quartz':
        (guest/'private/tmp/quartz.ppm').unlink(missing_ok=True)
        args.append('/tmp/quartz.ppm')
    with tempfile.TemporaryDirectory(prefix='remaklar-runtime-') as cwd:
        run=subprocess.run(args,capture_output=True,cwd=cwd,timeout=120,
            env={'PATH':os.defpath,'LANG':'C','LC_ALL':'C','TZ':'UTC'})
    stem=name+'-'+cohort
    (logs/(stem+'.stdout')).write_bytes(run.stdout);(logs/(stem+'.stderr')).write_bytes(run.stderr)
    checks=dict(exit=run.returncode==0,stdout=run.stdout==outputs[name],
        original_entry=run.stderr.count(('startup: entered original executable at %08x'%entry).encode())==1,
        no_bypass=b'probe-main:' not in run.stderr,no_unhandled=b'unsupported' not in run.stderr and b'unhandled host' not in run.stderr)
    if name=='quartz':
        data=(guest/'private/tmp/quartz.ppm').read_bytes();header=b'P6\n64 48\n255\n'
        pixels=b''.join((b'\xff\0\0' if 16<=x<48 and 12<=y<36 else b'\0\0\xff') for y in range(48) for x in range(64))
        checks['all_pixels']=data==header+pixels
        (logs/'quartz.ppm').write_bytes(data)
    result=dict(program=name,cohort=cohort,exit=run.returncode,entry=hex(entry),checks=checks)
    result['pass']=all(checks.values());results.append(result)
    print(('PASS' if result['pass'] else 'FAIL'),stem,checks,flush=True)
(logs/'results.json').write_text(json.dumps(results,indent=2)+'\n')
sys.exit(0 if all(r['pass'] for r in results) else 1)
