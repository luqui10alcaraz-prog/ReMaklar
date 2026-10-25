#!/usr/bin/env python3
"""Inspect two original kexts from Essentials' odc-cpio payload; never install/load.
SPDX-License-Identifier: MIT
"""
import gzip
import hashlib
import json
from pathlib import Path
import plistlib
import subprocess
from macho_inventory import inventory

root=Path(__file__).resolve().parents[1]
base=root/'research/jaguar-local/package-analysis'
member='Mac OS X Install Disc 1/System/Installation/Packages/Essentials.pkg/Contents/Archive.pax.gz'
archive=base/member
if not archive.is_file():
    run=subprocess.run(['7z','x','-y','-o'+str(base),str(root/'media/Mac OS X Jaguar Install CD.iso'),member],
                       stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    (root/'logs/jaguar-essentials-extraction.txt').write_text(run.stdout)
    if run.returncode not in (0,1):raise RuntimeError('Essentials extraction failed')
out=root/'research/jaguar-local/driver-package'
with gzip.open(archive,'rb') as source:
    while True:
        header=source.read(76)
        if not header:break
        if header[:6]!=b'070707':raise ValueError('Expected old ASCII cpio, not tar')
        length=int(header[65:76],8);name_length=int(header[59:65],8)
        name=source.read(name_length).rstrip(b'\0').decode()
        if name=='TRAILER!!!':break
        selected=any(component in name for component in ['IOGraphicsFamily.kext','ATIRage128.kext'])
        if selected:
            parts=Path(name).parts
            if '..' in parts or Path(name).is_absolute():raise ValueError('Invalid member path')
            data=source.read(length)
            if int(header[18:24],8)&0o170000==0o100000:
                path=out.joinpath(*parts);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        else:
            while length:
                chunk=source.read(min(length,1048576))
                if not chunk:raise ValueError('Truncated cpio')
                length-=len(chunk)
report=[]
for name in ['IOGraphicsFamily','ATIRage128']:
    folder=out/'System/Library/Extensions'/(name+'.kext')/'Contents'
    data=(folder/'MacOS'/name).read_bytes();image=inventory(data)
    info=plistlib.loads((folder/'Info.plist').read_bytes())
    report.append(dict(component=name,cputype=image.get('cputype'),slices=[s['cputype'] for s in image.get('slices',[])],
                       filetype=image.get('filetype'),sha256=hashlib.sha256(data).hexdigest(),
                       bundle_id=info.get('CFBundleIdentifier'),dependencies=info.get('OSBundleLibraries'),
                       personalities=info.get('IOKitPersonalities'),status='inspected only, never loaded'))
(root/'research/graphics-006/drivers.json').write_text(json.dumps(report,indent=2)+'\n')
print('Inspected original PPC kexts without loading them')
