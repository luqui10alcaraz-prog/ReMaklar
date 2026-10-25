#!/usr/bin/env python3
"""Verify original-code bitmap evidence, both hosts, regressions and backups.
SPDX-License-Identifier: MIT
PNG is only a lossless container conversion of the PPC-produced PPM bytes.
"""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import zlib
from macho_inventory import inventory

root=Path(__file__).resolve().parents[1]
native=root/'logs/runtime-native-005';cold=root/'logs/runtime-cold-006';linux=root/'logs/runtime-linux-006'
dest=root/'reports/runtime-006';dest.mkdir(exist_ok=True)
def sha(data):return hashlib.sha256(data).hexdigest()
def file_sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):digest.update(block)
    return digest.hexdigest()
def copy(source,name):shutil.copyfile(source,dest/name)
repo=root/'experiments/qemu-0.10.6';base='f8744f2a5146b78bf22f217ff18808844bd81460'
head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
assert not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'])
patch=subprocess.check_output(['git','-C',str(repo),'diff','--binary',base,head])
manifest=dict(base_commit=base,experimental_commit=head,branch='remaklar/0.06-runtime',patch_sha256=sha(patch))
(root/'patches/qemu-0.10.6/0005-runtime-quartz.patch').write_bytes(patch)
(root/'patches/qemu-0.10.6/runtime-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

expected={'objc-smoke':'Objective-C PPC OK\n','cf-smoke':'CoreFoundation PPC OK\n',
          'mach-runtime':'Mach runtime contracts OK\n','graphics-contracts':'Graphics boundary contracts OK\n',
          'ptrace-host':'request=c000 result=-1 errno=1\nrequest=b000 result=-1 errno=1\n'}
results=[]
for name,output in expected.items():
    for cohort in ['darwin','jaguar']:
        stem=name+'-'+cohort
        assert (native/(stem+'.status')).read_text().strip()=='status=0'
        assert (native/(stem+'.stdout')).read_bytes()==output.encode()
        errors=(native/(stem+'.stderr')).read_bytes()
        assert b'probe-main:' not in errors and b'unsupported' not in errors
        results.append(dict(program=name,cohort=cohort,exit=0))
for name,output in [('foundation','Foundation PPC OK\n'),('quartz','Quartz PPC bitmap OK\n')]:
    assert (native/(name+'.status')).read_text().strip()=='status=0'
    assert (native/(name+'.stdout')).read_bytes()==output.encode()
    assert b'unsupported' not in (native/(name+'.stderr')).read_bytes()
    results.append(dict(program=name,cohort='jaguar',exit=0))
for name in ['mach-native','graphics-native']:
    assert 'status=0' in (native/(name+'.txt')).read_text()
assert 'oracle_status=0' in (native/'ptrace-oracle.txt').read_text()
assert (native/'regression-status.txt').read_text().splitlines()==['baseline_status=0','utilities_status=0','filesystem_status=0']
assert (native/'baseline.txt').read_text().count('expected=')==13
assert 'cases=23 failed=0' in (native/'utilities.txt').read_text()
assert 'cases=11 failed=0 leftover=0' in (native/'filesystem.txt').read_text()
assert 'build_status=0' in (native/'build.txt').read_text()
linux_results=json.loads((linux/'results.json').read_text());assert len(linux_results)==12 and all(r['pass'] for r in linux_results)
for name,count in [('fixtures',11),('main-only',2),('dynamic',3)]:
    data=(root/('logs/regression-0.06/'+name+'.txt')).read_text()
    assert data.count('PASS ')==count and 'FAIL' not in data
    copy(root/('logs/regression-0.06/'+name+'.txt'),'linux-regression-'+name+'.txt')
assert 'cases=23 failed=0' in (root/'logs/regression-0.06/utilities.txt').read_text()
assert 'cases=11 failed=0 leftover=0' in (root/'logs/fs-linux-006/results.txt').read_text()
copy(root/'logs/regression-0.06/utilities.txt','linux-regression-utilities.txt')
copy(root/'logs/fs-linux-006/results.txt','linux-regression-filesystem.txt')
assert 'failed=0' in (cold/'status.txt').read_text() and (cold/'status.txt').read_text().count('status=0')==6

header=b'P6\n64 48\n255\n'
expected_pixels=b''.join(b'\xff\0\0' if 16<=x<48 and 12<=y<36 else b'\0\0\xff' for y in range(48) for x in range(64))
native_ppm=(native/'quartz.ppm').read_bytes()
assert native_ppm==header+expected_pixels
assert (linux/'quartz.ppm').read_bytes()==native_ppm==(cold/'quartz.ppm').read_bytes()
copy(native/'quartz.ppm','quartz-native.ppm');copy(linux/'quartz.ppm','quartz-linux.ppm');copy(cold/'quartz.ppm','quartz-cold.ppm')
def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
# Encode the ORIGINAL bytes, not the expected test oracle pixels.
pixels=native_ppm[len(header):]
scanlines=b''.join(b'\0'+pixels[y*192:(y+1)*192] for y in range(48))
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',64,48,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(scanlines))+chunk(b'IEND',b'')
(dest/'quartz-native.png').write_bytes(png)
for p in native.iterdir():
    if p.is_file() and p.suffix in ['.txt','.stdout','.stderr','.status','.md5']:
        copy(p,'native-'+p.name)
for p in cold.iterdir():
    if p.is_file():copy(p,'cold-'+p.name)
for name in ['quartz-jaguar','foundation-jaguar','objc-smoke-jaguar','cf-smoke-jaguar','mach-runtime-jaguar','graphics-contracts-jaguar']:
    for suffix in ['.stdout','.stderr']:copy(linux/(name+suffix),'linux-'+name+suffix)
copy(root/'logs/runtime-native-003/graphics-native.txt','native-initial-hostname-expectation.txt')
copy(root/'logs/runtime-native-001/quartz-build.txt','native-initial-subframework-link-error.txt')
copy(root/'logs/runtime-native-001/cf-smoke-build.txt','native-initial-missing-sdk-headers.txt')

old=json.loads((root/'reports/remaklar-0.05.json').read_text())
darwin_md5=(native/'darwin-originals.md5').read_text();jaguar_md5=(native/'jaguar-originals.md5').read_text()
for path,sample in old['samples'].items():
    data=(root/'research/samples-local'/path).read_bytes()
    assert sha(data)==sample['sha256'] and hashlib.md5(data).hexdigest() in darwin_md5
jaguar=root/'research/jaguar-local/Mac OS X Install Disc 1'
catalog=json.loads((root/'research/graphics-006/catalog.json').read_text())
for entry in catalog:
    data=(jaguar/entry['path'].lstrip('/')).read_bytes()
    assert sha(data)==entry['sha256'] and hashlib.md5(data).hexdigest() in jaguar_md5
owned=root/'build/runtime-006-owned';owned_hashes={}
for name in ['run06','objc-smoke','cf-smoke','mach-runtime','ptrace-host','graphics-contracts','quartz','foundation']:
    data=(owned/name).read_bytes();owned_hashes[name]=sha(data)
    if name!='ptrace-host':assert hashlib.md5(data).hexdigest() in (native/'owned.md5').read_text()
    image=inventory(data);assert image['cputype']==(7 if name=='run06' else 18)
backups={}
for version,name,key in [('0.03','darwin602-native-003-verified.qcow2','offline_snapshot_sha256'),
                         ('0.04','darwin602-utilities-004-verified.qcow2','offline_snapshot_sha256'),
                         ('0.05','darwin602-filesystem-005-verified.qcow2','snapshot_sha256')]:
    previous=json.loads((root/('reports/remaklar-'+version+'.json')).read_text())
    digest=file_sha(root/'vm'/name);assert digest==previous[key];backups[name]=digest
window=(native/'windowserver.stderr').read_text()
assert 'startup: entered original executable at 00002998' in window and 'unsupported Darwin syscall/trap 2' in window
registry=dict(checkpoint='0.06-runtime',previous='services-0.05.json',
    original_ppc_executed=['Object runtime and custom method dispatch','CoreFoundation string/array','Foundation NSArray/NSString/autorelease pool','CoreGraphics bitmap context and rectangle fills'],
    components=[dict(component='Window Manager / WindowServer',status='entered original executable; blocked at BSD fork(2)'),
                dict(component='AppKit',status='inspected only'),dict(component='IOGraphicsFamily / ATIRage128 kexts',status='inspected only; never loaded')],
    bridges=['ptrace private markers targeting PID 0: genuine EPERM','monotonic nanosecond timebase + mach_timebase_info 1/1',
             'private split-segment mappings; SYSTEM_REGION_BACKED is false','BSD writev/getlogin/sysctl hostname',
             'AF_UNIX connect re-rooted into guest files; datagram socket handles and IPv4 interface-query encoding'],
    partial_emulation=['receive/send/send-once rights, queue limits, port-set membership, dead-name notification registration',
                       'bootstrap lookup in empty guest service namespace returns UNKNOWN_SERVICE',
                       'shm_open non-create lookup in empty guest namespace returns ENOENT'],
    unsupported=['fork','notification delivery and destruction lifecycle','shared-memory creation/global sharing',
                 'general IPv4 communication','full Mach message delivery/runloop/threading','WindowServer service registration and framebuffer device bridging'])
(root/'research/services-0.06.json').write_text(json.dumps(registry,indent=2)+'\n')
report=dict(checkpoint='0.06-runtime',original_quartz_render_pass=True,source=manifest,
    media=json.loads((root/'research/graphics-006/media.json').read_text()),
    target='Darwin 6.0 i386 in QEMU; original PPC Jaguar 10.2 build 6C115 libraries',
    rendering=dict(kind='offscreen CGBitmapContext, not an Aqua desktop',width=64,height=48,
                   blue_pixels=2304,red_pixels=768,all_pixels_verified=True,
                   ppm_sha256=sha(native_ppm),cold_boot_identical=True,linux_identical=True,
                   png='lossless container conversion of PPC-produced RGB bytes'),
    native_cases=results,linux_cases=linux_results,native_oracles=3,
    previous_linux_checks=50,previous_native_checks=47,kernel_modified=False,
    windowserver=dict(exit=125,blocker='BSD fork syscall 2',entry='0x2998'),
    original_components=catalog,owned_binaries_sha256=owned_hashes,backups_preserved=backups,
    snapshot='vm/darwin602-runtime-006-verified.qcow2 (not distributed)',
    snapshot_sha256=file_sha(root/'vm/darwin602-runtime-006-verified.qcow2'),
    qcow2_check='No errors were found after clean halt',
    evidence={p.name:file_sha(p) for p in sorted(dest.iterdir()) if p.is_file()})
(root/'reports/remaklar-0.06.json').write_text(json.dumps(report,indent=2)+'\n')
print('Verified: original PPC Quartz output on Darwin i386, identical after cold boot and on Linux; all prior checks preserved')
