#!/usr/bin/env python3
"""Package Jaguar Installer's static Mach-O closure from existing local inputs.
Does not replace originals or download components. SPDX-License-Identifier: MIT
"""
import hashlib
import json
from pathlib import Path
import struct
import tarfile

root=Path(__file__).resolve().parents[1]
bases=[root/'build/jaguar-installer-008/Mac OS X Install Disc 1',
       root/'build/jaguar-deps-008/Mac OS X Install Disc 1',
       root/'research/jaguar-local/Mac OS X Install Disc 1']
pending=['/Applications/Utilities/Installer.app/Contents/MacOS/Installer']
seen=set();found={};missing=[]
while pending:
    name=pending.pop()
    if name in seen:continue
    seen.add(name)
    path=next((p for base in bases if (p:=base/name.lstrip('/')).is_file()),None)
    if path is None:missing.append(name);continue
    with path.open('rb') as f:
        header=f.read(28)
        if len(header)<28 or header[:4]!=b'\xfe\xed\xfa\xce':
            raise ValueError('Not an original PPC Mach-O: '+str(path))
        _,cpu,_,kind,count,size,_=struct.unpack('>7I',header)
        assert cpu==18
        commands=f.read(size)
    deps=[];offset=0
    for _ in range(count):
        cmd,length=struct.unpack_from('>2I',commands,offset)
        if cmd in (12,14):
            noff=struct.unpack_from('>I',commands,offset+8)[0]
            dep=commands[offset+noff:offset+length].split(b'\0')[0].decode()
            deps.append(dep);pending.append(dep)
        offset+=length
    found[name]={'source':str(path.relative_to(root)), 'cputype':cpu,'dependencies':deps,
                 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
out=root/'build/graphics008-library-closure'
out.mkdir(exist_ok=False)
(out/'manifest.json').write_text(json.dumps({'files':found,'missing':missing},indent=2)+'\n')
(out/'paths.txt').write_text(''.join(name.lstrip('/')+'\n' for name in sorted(found)))
with tarfile.open(out/'originals.tgz','w:gz',format=tarfile.GNU_FORMAT) as archive:
    for name,info in sorted(found.items()):archive.add(root/info['source'],arcname=name.lstrip('/'),recursive=False)
print('Original PPC images:',len(found),'missing:',missing)
