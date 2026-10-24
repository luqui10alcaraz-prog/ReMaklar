#!/usr/bin/env python3
"""Export measured filesystem coverage and a deliberately blocked ObjC probe.
SPDX-License-Identifier: MIT
"""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from macho_inventory import inventory

root=Path(__file__).resolve().parents[1]
native=root/'logs/fs-native-004'; linux=root/'logs/fs-linux-001'
dest=root/'reports/filesystem';dest.mkdir(exist_ok=True)
sha=lambda data:hashlib.sha256(data).hexdigest()
repo=root/'experiments/qemu-0.10.6'
base='f80cd4a91e77dbc132eb0d974003851847b3cd39'
head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
assert not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'])
patch=subprocess.check_output(['git','-C',str(repo),'diff','--binary',base,head])
manifest=dict(base_commit=base,experimental_commit=head,branch='remaklar/0.05-filesystem',patch_sha256=sha(patch))
(root/'patches/qemu-0.10.6/0004-filesystem.patch').write_bytes(patch)
(root/'patches/qemu-0.10.6/filesystem-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
assert (native/'final-status.txt').read_text().strip()=='baseline=0 utilities=0 filesystem=0'
assert 'build_status=0' in (native/'build.txt').read_text()
for folder in [native/'filesystem',linux]:
    text=(folder/'results.txt').read_text()
    assert 'cases=11 failed=0 leftover=0' in text and text.count('PASS ')==11
assert 'cases=23 failed=0' in (native/'utilities.txt').read_text()
assert 'failed=0' in (native/'baseline.txt').read_text()
regression=root/'logs/regression-0.05'
for name,count in [('fixtures',11),('main-only',2),('dynamic',3)]:
    text=(regression/(name+'.txt')).read_text()
    assert text.count('PASS ')==count and 'FAIL' not in text
    shutil.copyfile(regression/(name+'.txt'),dest/('linux-'+name+'.txt'))
assert 'cases=23 failed=0' in (regression/'utilities.txt').read_text()
shutil.copyfile(regression/'utilities.txt',dest/'linux-utilities.txt')
for name in ['build.txt','configure.txt','host.txt','baseline.txt','filesystem.txt','utilities.txt',
             'final-status.txt','original-md5.txt','runner-md5.txt','objc-compiler.txt',
             'objc-image.txt','objc-real-status.txt','objc-real.stderr','objc-real.stdout']:
    shutil.copyfile(native/name,dest/('native-'+name))
shutil.copyfile(root/'logs/fs-native-001/filesystem.txt',dest/'native-initial-expectation-failure.txt')
shutil.copyfile(root/'logs/fs-native-001/filesystem/ls-link.stdout',dest/'native-initial-symlink-metadata.txt')
observed={};results=[]
for case in [l.split()[1] for l in (linux/'results.txt').read_text().splitlines() if l.startswith('PASS ')]:
    row={'case':case,'hosts':{}}
    for host,folder in [('linux',linux),('darwin6',native/'filesystem')]:
        stdout=(folder/(case+'.stdout')).read_bytes();stderr=(folder/(case+'.stderr')).read_bytes()
        row['hosts'][host]=dict(stdout_sha256=sha(stdout),stdout_bytes=len(stdout),stderr_sha256=sha(stderr))
        assert b'unsupported' not in stderr and b'unhandled host' not in stderr
        for number in set(int(n) for n in re.findall(rb'syscall pc=[0-9a-f]+ r0=(\d+)',stderr)):
            observed.setdefault(number,set()).add(case)
        if case in ['filesystem-probe','ls-metadata','ls-link','ls-many','pwd-nested','ls-missing']:
            shutil.copyfile(folder/(case+'.stderr'),dest/(host+'-'+case+'.stderr'))
            shutil.copyfile(folder/(case+'.stdout'),dest/(host+'-'+case+'.stdout'))
    results.append(row)
payload=json.loads((root/'build/darwin-payload/manifest.json').read_text())
md5text=(native/'original-md5.txt').read_text();samples={}
old=json.loads((root/'reports/remaklar-0.04.json').read_text())
for path,expected in payload['samples'].items():
    data=(root/'research/samples-local'/path).read_bytes()
    assert sha(data)==expected
    md5=hashlib.md5(data).hexdigest();assert md5 in md5text
    if path in old['samples']:assert expected==old['samples'][path]['sha256']
    samples[path]=dict(sha256=expected,guest_verified_md5=md5)
backups={}
for previous,filename,key in [('0.03','darwin602-native-003-verified.qcow2','offline_snapshot_sha256'),
                              ('0.04','darwin602-utilities-004-verified.qcow2','offline_snapshot_sha256')]:
    saved=json.loads((root/('reports/remaklar-'+previous+'.json')).read_text())
    digest=sha((root/'vm'/filename).read_bytes());assert digest==saved[key];backups[filename]=digest
own=(root/'build/objc-smoke-ppc-final').read_bytes();own_image=inventory(own)
assert own_image['cputype']==18 and any(d['path']=='/usr/lib/libobjc.A.dylib' for d in own_image['dependencies'])
assert 'compiler_status=0' in (native/'objc-compiler.txt').read_text()
assert 'runtime_probe_status=125' in (native/'objc-real-status.txt').read_text()
for log in [native/'objc-real.stderr',root/'logs/objc-real-linux-001.stderr']:
    text=log.read_text()
    assert 'r0=26 r3=0000c000' in text and 'unsupported Darwin syscall/trap 26' in text
    assert ('startup: entered original executable at %08x'%own_image['entry']) in text
shutil.copyfile(root/'logs/objc-real-linux-001.stderr',dest/'linux-objc-real.stderr')
(root/'research/inventory/own_objc_smoke.json').write_text(json.dumps(own_image,indent=2)+'\n')
services={10:'unlink',12:'chdir',13:'fchdir',15:'chmod',54:'ioctl terminal subset',58:'readlink',60:'umask',
          92:'fcntl descriptor flags',116:'gettimeofday',128:'rename',136:'mkdir',137:'rmdir',
          158:'fstatfs guest profile',196:'getdirentries',199:'lseek'}
registry=dict(checkpoint='0.05-filesystem',previous='services-0.04.json',
    additional_services=[dict(number=n,name=name,provider='filesystem-profile-emulation' if n==158 else 'bsd-host-bridge',
        cases=sorted(observed.get(n,[])),status='tested subset') for n,name in services.items()],
    original_ppc=['ls','pwd','fts/getcwd/stdio in libSystem','dyld','echo','cat'],
    shared_bridges=['virtual descriptor table including write','bounded path normalization and virtual cwd',
                    'PPC32 big-endian stat/dirent/timeval encoding','TCG cache unprotection before bridge writes'],
    blocked=[dict(number=26,name='ptrace',request='0xc000',status='not implemented',evidence='compiled ObjC probe on both hosts')],
    limits=['lexical cwd model; full symlink-directory resolution not implemented',
            'directory lseek supports rewind only; cursors are process-local',
            'fstatfs is a synthetic non-union guest profile backed by host capacity',
            'termios only returns ENOTTY for nonterminals; terminal settings unsupported',
            'no complete fcntl/open flags, locking, threading, signals or Mach service coverage'])
(root/'research/services-0.05.json').write_text(json.dumps(registry,indent=2)+'\n')
report=dict(checkpoint='0.05-filesystem',filesystem_pass=True,source=manifest,
    filesystem_cases_each_host=11,prior_utility_cases_each_host=23,linux_prior_regressions=16,
    native_prior_regressions=13,results=results,samples=samples,
    kernel_modified=False,backups_preserved=backups,
    snapshot='vm/darwin602-filesystem-005-verified.qcow2 (not distributed)',
    snapshot_sha256=sha((root/'vm/darwin602-filesystem-005-verified.qcow2').read_bytes()),
    qcow2_check='No errors were found on the image after clean halt',
    native_executor_sha256=sha((root/'build/darwin-runner-005').read_bytes()),
    objc=dict(compiler='Darwin gcc2 -no-cpp-precomp -arch ppc -lobjc',compiler_pass=True,
        program_sha256=sha(own),entry=hex(own_image['entry']),execution_pass=False,exit=125,
        blocker='Darwin syscall 26 ptrace request 0xc000',note='original dyld/CRT/libs; no main or syscall bypass'),
    evidence={p.name:sha(p.read_bytes()) for p in sorted(dest.iterdir()) if p.is_file()})
(root/'reports/remaklar-0.05.json').write_text(json.dumps(report,indent=2)+'\n')
print('Verified filesystem + all regressions on both hosts; Objective-C compiled, execution blocked at ptrace(0xc000)')
