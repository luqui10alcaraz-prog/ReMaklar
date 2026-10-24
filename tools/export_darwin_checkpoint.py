#!/usr/bin/env python3
"""Export the committed Darwin port and measured evidence (no Apple binaries).
SPDX-License-Identifier: MIT
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
repo = root / 'experiments/qemu-0.10.6'
base = 'df60a2e0f20ccbeb9c37868b23cdf1f4f2edcedf'
head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
assert not subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain'])
patch = subprocess.check_output(['git', '-C', str(repo), 'diff', '--binary', base, head])
manifest = dict(base_commit=base, experimental_commit=head, branch='remaklar/0.03-darwin6',
                patch_sha256=hashlib.sha256(patch).hexdigest())
dest = root / 'patches/qemu-0.10.6'
(dest / '0003-darwin6-i386.patch').write_bytes(patch)
(dest / 'darwin6-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
evidence = root / 'reports/darwin6'
evidence.mkdir(exist_ok=True)
names = ['compiler-compat.log', 'configure-019.log', 'build-019.log', 'tests-019.log',
         'true-019.stderr', 'false-019.stderr', 'sample-md5.log',
         'executor-load-commands.log', 'trace-019.log', 'trace-019.status',
         'tests-016.log', 'tests-017.log', 'tests-018.log', 'true-trace-017.log',
         'tests-coldboot.log']
for name in names:
    source = root / 'logs/darwin6' / name
    assert source.is_file(), source
    shutil.copyfile(source, evidence / name)
for name in ['linux-final-static-0.03-console.txt', 'linux-final-dynamic-0.03-console.txt']:
    shutil.copyfile(root / 'logs' / name, evidence / name)
native = (evidence / 'tests-019.log').read_text()
assert 'failed=0' in native and 'true exit=0 expected=0' in native and 'false exit=1 expected=1' in native
assert 'failed=0' in (evidence / 'tests-coldboot.log').read_text()
samples = {}
for relative in ['usr/bin/true', 'usr/bin/false', 'usr/lib/dyld', 'usr/lib/libSystem.B.dylib',
                 'usr/lib/system/libmathCommon.A.dylib']:
    data = (root / 'research/samples-local' / relative).read_bytes()
    digest = hashlib.md5(data).hexdigest()
    assert digest in (evidence / 'sample-md5.log').read_text()
    samples[relative] = dict(sha256=hashlib.sha256(data).hexdigest(), guest_verified_md5=digest)
report = dict(checkpoint='0.03-darwin6', native_pass=True, source=manifest,
              host='Darwin 6.0 i386, installed from Darwin 6.0.2 CD; QEMU pentium3',
              compiler='gcc2 -no-cpp-precomp (GCC 2.95.2)', clean_native_build=19,
              cold_boot_repeat_pass=True,
              offline_snapshot='vm/darwin602-native-003-verified.qcow2 (not distributed)',
              offline_snapshot_sha256='24b64365b67a7fd1d038e5d0b51d3bd82c1d70bda8a5a58cee416cd8186b4ee7',
              qcow2_check='No errors were found on the image after final halt',
              fixtures=11, true_exit=0, false_exit=1, original_entry='0x195c',
              kernel_modified=False, samples=samples,
              sample_source='Apple Darwin 6.0.2 CD; not verified retail Jaguar',
              native_executor_sha256=hashlib.sha256((root/'build/darwin-runner-019').read_bytes()).hexdigest(),
              linux_regression='13 static/main-only and 3 dynamic checks passed',
              limits=['single-user laboratory', 'guest signals and general threading not implemented',
                      'legacy host SMC recovery restricted to verified TCG MOV stores',
                      'unsupported host faults fail with 126; no general application compatibility claim'],
              evidence={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(evidence.iterdir()) if p.is_file()})
(root/'reports/remaklar-0.03.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(manifest, indent=2))
