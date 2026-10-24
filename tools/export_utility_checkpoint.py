#!/usr/bin/env python3
"""Validate both hosts and export measured utility/service coverage.
SPDX-License-Identifier: MIT
"""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
dest = root / 'reports/utilities'
dest.mkdir(exist_ok=True)
def sha(data): return hashlib.sha256(data).hexdigest()
def copy(source, name): shutil.copyfile(root / source, dest / name)
repo = root / 'experiments/qemu-0.10.6'
commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
assert commit == 'f80cd4a91e77dbc132eb0d974003851847b3cd39'
assert not subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain'])
assert hashlib.md5((root/'build/darwin-runner-019').read_bytes()).hexdigest() in (root/'logs/utilities-native-runner-md5.txt').read_text()
previous_report = json.loads((root/'reports/remaklar-0.03.json').read_text())
assert sha((root/'vm/darwin602-native-003-verified.qcow2').read_bytes()) == previous_report['offline_snapshot_sha256']
assert sha((root/'build/darwin-runner-019').read_bytes()) == previous_report['native_executor_sha256']
native = root / 'logs/utilities-native-001'
linux = root / 'logs/utilities-linux-001'
assert 'baseline_status=0' in (native/'console.txt').read_text()
assert 'utilities_status=0' in (native/'console.txt').read_text()
baseline = (root/'logs/utilities-native-baseline-001.log').read_text()
assert 'failed=0' in baseline and baseline.count('expected=') == 13
dynamic = json.loads((root/'logs/utilities-linux-regression/dynamic/results.json').read_text())
assert dynamic['pass'] and len(dynamic['results']) == 3
for name, count in [('fixtures',11), ('main-only',2), ('dynamic',3)]:
    text = (root/('logs/utilities-linux-regression/'+name+'.console.txt')).read_text()
    assert text.count('PASS ') == count and 'FAIL' not in text
    copy('logs/utilities-linux-regression/'+name+'.console.txt', 'linux-regression-'+name+'.txt')
copy('logs/utilities-native-baseline-001.log', 'native-baseline.txt')
copy('logs/utilities-native-original-md5.log', 'native-original-md5.txt')
copy('logs/utilities-native-runner-md5.txt', 'native-runner-md5.txt')
for name in ['results.tsv','console.txt','host.txt','md5.txt']:
    shutil.copyfile(native/name, dest/('native-'+name))
shutil.copyfile(linux/'results.tsv', dest/'linux-results.tsv')
md5_text = (native/'md5.txt').read_text() + (root/'logs/utilities-native-original-md5.log').read_text()
samples = {}
for name in ['bin/echo','bin/cat','usr/bin/true','usr/bin/false','usr/lib/dyld',
             'usr/lib/libSystem.B.dylib','usr/lib/system/libmathCommon.A.dylib']:
    data = (root/'research/samples-local'/name).read_bytes()
    md5 = hashlib.md5(data).hexdigest()
    assert md5 in md5_text
    samples[name] = dict(sha256=sha(data), guest_verified_md5=md5)
    previous = root/'reports/remaklar-0.03.json'
    old = json.loads(previous.read_text())['samples']
    if name in old: assert old[name]['sha256'] == sha(data)
    else:
        inv = json.loads((root/'research/inventory'/(name.replace('/','_')+'.json')).read_text())
        assert inv['analysis']['sha256'] == sha(data)
vectors = (root/'build/utility-cases.tsv').read_text().splitlines()
def unhex(value): return b'' if value == '-' else bytes.fromhex(value)
results = []
observed = {}
for line in vectors:
    fields = line.split('\t'); name, program, status, entry, stdin, stdout, diagnostic = fields[:7]
    row = dict(case=name, program=program, expected_exit=int(status), original_entry='0x'+entry,
               argc=1+len(fields[7:]), argument_bytes=sum(len(unhex(v)) for v in fields[7:]),
               stdout_bytes=len(unhex(stdout)), stdout_sha256=sha(unhex(stdout)), hosts={})
    for host, folder in [('linux',linux),('darwin6',native)]:
        text = (folder/'results.tsv').read_text()
        assert re.search(r'^PASS\t'+re.escape(name)+r'\texit='+status+r' expected='+status+r'\t', text, re.M)
        output = (folder/(name+'.stdout')).read_bytes(); error = (folder/(name+'.stderr')).read_bytes()
        assert output == unhex(stdout) and unhex(diagnostic) in error
        assert error.count(('startup: entered original executable at '+entry).encode()) == 1
        assert not any(s in error for s in [b'unsupported',b'probe-main:',b'unhandled host'])
        row['hosts'][host] = {'pass': True, 'stderr_sha256': sha(error)}
        calls = sorted(set(int(n) for n in re.findall(rb'syscall pc=[0-9a-f]+ r0=(\d+)',error)))
        rpcs = sorted(set(int(n) for n in re.findall(rb'mach_rpc id=(\d+)',error)))
        for kind, numbers in [('trap',calls),('rpc',rpcs)]:
            for number in numbers:
                key = (kind,number)
                observed.setdefault(key, set()).add(name)
    results.append(row)
assert len(results) == 23
for name in ['echo-long','echo-empty-between','cat-file-large','cat-missing-continues','cat-number']:
    for host, folder in [('linux',linux),('native',native)]:
        shutil.copyfile(folder/(name+'.stderr'), dest/(host+'-'+name+'.stderr'))
names = {1:'exit',3:'read',4:'write',5:'open',6:'close',20:'getpid/getppid',24:'getuid/geteuid',
         25:'geteuid',43:'getegid',47:'getgid/getegid',188:'stat',189:'fstat',190:'lstat',
         202:'sysctl',296:'load_shared_file query',327:'issetugid',32753:'thread self set',
         32754:'thread self get',32755:'processor facility query',
         4294967270:'mach_reply_port',4294967269:'mach_thread_self',4294967268:'mach_task_self',
         4294967267:'mach_host_self',4294967265:'mach_msg_trap',4294967264:'mach_msg_overwrite_trap',
         4294967253:'map_fd'}
rpcs = {200:'host_info',202:'host_page_size',206:'host_get_clock_service',3204:'mach_port_allocate',
        3206:'mach_port_deallocate',3404:'mach_ports_lookup',3409:'task_get_special_port',
        3616:'thread_policy',3800:'vm_region',3801:'vm_allocate',3802:'vm_deallocate',
        3803:'vm_protect',3812:'vm_map'}
services = []
for (kind,number), cases in sorted(observed.items()):
    name = (names if kind == 'trap' else rpcs)[number]
    provider = 'mach-process-emulation'
    if kind == 'trap' and number in [1,3,4,5,6,20,24,25,43,47,188,189,190,327]: provider='bsd-host-bridge'
    if (kind=='rpc' and number in [3800,3801,3802,3803,3812]) or number==4294967253: provider='host-vm-bridge'
    if kind=='trap' and number in [202,296]: provider='process-model-substitution'
    services.append(dict(kind=kind, number=number, name=name, provider=provider,
                         status='observed in passing cases; limited implemented subset', cases=sorted(cases)))
registry = dict(schema_version=1, checkpoint='0.04-utilities', services=services,
    components=[dict(name=n,provider='original-ppc-on-qemu-tcg',native_replacement=False)
                for n in ['echo','cat','dyld','libSystem.B.dylib','libmathCommon.A.dylib']],
    libc_behavior=[dict(functions=['printf','stdio buffering/flush'], evidence='echo byte-exact cases',
                        coverage='black-box behavior plus source/imports; no per-function entry instrumentation'),
                   dict(functions=['open','read','write','close','fstat'], evidence='cat files/redirected stdin and syscall traces',
                        coverage='tested byte I/O paths, not every flag/error'),
                   dict(functions=['getopt','fopen','fprintf','warn'], evidence='cat -n, missing and continuation cases',
                        coverage='source/import-supported behavior, not exhaustive function coverage')],
    unimplemented=['general PPC Unix signals','multiple guest threads','arbitrary Mach RPC/services',
                   'general open flags/file creation','guest-relative cwd/root isolation','native x86 Jaguar library replacements'])
(root/'research/services-0.04.json').write_text(json.dumps(registry,indent=2)+'\n')
report = dict(checkpoint='0.04-utilities',pass_=True,runtime_commit=commit,runtime_modified=False,
              samples=samples, cases=results, utility_cases_each_host=23,
              preserved_native_checks=13,preserved_linux_checks=16,kernel_modified=False,
              native_executor_sha256=sha((root/'build/darwin-runner-019').read_bytes()),
              linux_executor_sha256=sha((root/'build/qemu-linux32-0.03/ppc-darwin-user/qemu-ppc').read_bytes()),
              vector_sha256=sha((root/'build/utility-cases.tsv').read_bytes()),
              backup_003_unchanged_sha256=sha((root/'vm/darwin602-native-003-verified.qcow2').read_bytes()),
              sample_source='Apple Darwin 6.0.2 CD; not compared with retail Jaguar',
              evidence={p.name:sha(p.read_bytes()) for p in sorted(dest.iterdir()) if p.is_file()})
report['pass'] = report.pop('pass_')
report['offline_snapshot'] = 'vm/darwin602-utilities-004-verified.qcow2 (not distributed)'
report['offline_snapshot_sha256'] = sha((root/'vm/darwin602-utilities-004-verified.qcow2').read_bytes())
report['qcow2_check'] = 'No errors were found on the image after clean halt'
report['payload_manifest'] = json.loads((root/'build/darwin-payload/manifest.json').read_text())
(root/'reports/remaklar-0.04.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: 23 utility cases per host, 13 native and 16 Linux baseline checks; originals verified')
