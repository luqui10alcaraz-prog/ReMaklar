#!/usr/bin/env python3
"""Read-only media fingerprinting and optional offline HFS+ extraction with 7z.
No installation and no original executable modification. SPDX-License-Identifier: MIT
Run under WSL, where HFS symlinks can be represented correctly.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import struct
import subprocess
import tarfile
from macho_inventory import inventory

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--cd1',type=Path,default=root/'media/Mac OS X Jaguar Install CD.iso')
parser.add_argument('--cd2',type=Path,default=root/'media/Mac OS X Jaguar Install CD 2.iso')
parser.add_argument('--extract',action='store_true')
args=parser.parse_args()
output=root/'research/graphics-006';output.mkdir(exist_ok=True)
logs=root/'logs';logs.mkdir(exist_ok=True)
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while True:
            chunk=f.read(1048576)
            if not chunk:break
            h.update(chunk)
    return h.hexdigest()
media={}
for name,path in [('cd1',args.cd1),('cd2',args.cd2)]:
    media[name]=dict(filename=path.name,size=path.stat().st_size,sha256=digest(path))
listing=subprocess.check_output(['7z','l','-slt',str(args.cd1)],text=True)
(logs/'jaguar-cd1-listing.txt').write_text(listing)
paths=re.findall(r'^Path = (.+)$',listing,re.M)
version_path=next(p for p in paths if p.endswith('/System/Library/CoreServices/SystemVersion.plist'))
volume=version_path.split('/System/')[0]
media['cd1']['volume']=volume
media['cd1']['format']='Apple partition map / HFS+, detected by 7z'
media['components_in_listing']={term:[p for p in paths if term in p] for term in
    ['WindowServer','Window Manager','CoreGraphics.framework','Foundation.framework','AppKit.framework','Extensions.mkext']}
(output/'media.json').write_text(json.dumps(media,indent=2)+'\n')
if not args.extract:
    print(json.dumps({k:v for k,v in media.items() if k!='components_in_listing'},indent=2));raise SystemExit(0)
destination=root/'research/jaguar-local';destination.mkdir(exist_ok=True)
selected=['System/Library/Frameworks','System/Library/PrivateFrameworks','usr/lib',
          'System/Library/CoreServices/WindowServer','System/Library/CoreServices/SystemVersion.plist',
          'System/Library/ColorSync','System/Library/CoreServices/CharacterSets',
          'private/etc','etc','private/tmp','tmp']
run=subprocess.run(['7z','x','-y','-o'+str(destination),str(args.cd1)]+[volume+'/'+p for p in selected],
                   stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
(logs/'jaguar-extraction-repro.txt').write_text(run.stdout)
errors=[line for line in run.stdout.splitlines() if line.startswith('ERROR:')]
if any('Dangerous' not in line for line in errors) or run.returncode not in (0,1,2):
    raise RuntimeError('Extraction error; inspect logs/jaguar-extraction-repro.txt')
# 7z refuses some absolute/escaping symlinks. Keep the refusal explicit; this
# is an incomplete offline tree, not proof that every install-CD file exists.
media['rejected_links']=errors
guest=destination/volume
version=plistlib.loads((guest/'System/Library/CoreServices/SystemVersion.plist').read_bytes())
media['system_version']={key:version[key] for key in ['ProductName','ProductVersion','ProductBuildVersion']}
rows=[];catalog=[];closure=[]
interesting={'CoreGraphics','Window Manager','AppKit','Foundation','CoreFoundation','libobjc.A.dylib','libSystem.B.dylib'}
for base,dirs,files in os.walk(guest):
    for name in files:
        path=Path(base)/name
        if path.is_symlink():continue
        with path.open('rb') as f:header=f.read(28)
        if header[:4]!=b'\xfe\xed\xfa\xce':continue
        count,size=struct.unpack_from('>II',header,16)
        with path.open('rb') as f:commands=f.read(28+size)
        off=28;identity=None;dependencies=[]
        for i in range(count):
            command,length=struct.unpack_from('>II',commands,off)
            if command in (12,13):
                string_offset=struct.unpack_from('>I',commands,off+8)[0]
                value=commands[off+string_offset:off+length].split(b'\0')[0].decode()
                if command==13:identity=value
                else:dependencies.append(value)
            off+=length
        relative='/'+path.relative_to(guest).as_posix()
        if identity:
            rows.append((identity,relative));closure.append(dict(path=relative,install_name=identity,dependencies=dependencies,sha256=digest(path)))
        if name in interesting:
            data=path.read_bytes();analysis=inventory(data)
            # N_PBUD (0xc) is still an import in these prebound Jaguar binaries.
            analysis['imports']=[s['name'] for s in analysis['symbols'] if not s['type']&0xe0 and s['type']&14 in (0,12)]
            (output/(name.replace(' ','_')+'.json')).write_text(json.dumps(analysis,indent=2)+'\n')
            catalog.append(dict(path=relative,sha256=hashlib.sha256(data).hexdigest(),size=len(data),
                                dependencies=dependencies,cputype=analysis['cputype'],entry=analysis['entry'],version=analysis.get('current_version')))
(guest/'remaklar-link-map.tsv').write_text(''.join(a+'\t'+b+'\n' for a,b in rows))
(output/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
(output/'library-closure.json').write_text(json.dumps(closure,indent=2)+'\n')
(output/'media.json').write_text(json.dumps(media,indent=2)+'\n')
with tarfile.open(root/'build/jaguar-006.tgz','w:gz',format=tarfile.GNU_FORMAT) as tar:
    def original_inputs_only(entry):
        # Never seed a test VM with a previous run's rendered output.
        if entry.name.startswith('jaguar/private/tmp/'): return None
        return entry
    tar.add(guest,arcname='jaguar',filter=original_inputs_only)
print('Prepared',len(rows),'original dylibs for offline testing; see rejected links and media fingerprint')
