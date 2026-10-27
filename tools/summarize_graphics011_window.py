"""Freeze the evidence index for the authentic Installer window in trial102."""
from pathlib import Path
import hashlib
import json
import re

base = Path('reports/graphics-011/capacity102')
out = base / 'verified/authenticity.json'
assert not out.exists()
def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

direct = json.loads(Path('reports/graphics-011/resume-validation/upl66-machine-checkpoint.json').read_text())
direct_check = {name: sha(name) == expected['sha256']
                for name, expected in direct['files'].items()}
assert all(direct_check.values())
recheck = Path('reports/graphics-011/resume-validation/direct66-after-window102-hash-recheck.json')
assert not recheck.exists()
recheck.write_text(json.dumps(direct_check, indent=2) + '\n')

manifest_path = Path('patches/qemu-0.10.6/graphics-011-growing-native-capability-exports-manifest.json')
manifest = json.loads(manifest_path.read_text())
source_check = {name: hashlib.sha256((Path('build/qemu-011-source') / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == row['sha256']
                for name, row in manifest['files'].items()}
assert all(source_check.values())
assert sha('patches/qemu-0.10.6/0038-growing-native-capability-exports.patch') == manifest['patch_sha256']
installer = Path('build/jaguar-installer-008/Mac OS X Install Disc 1/Applications/Utilities/Installer.app/Contents/MacOS/Installer')
installer_md5 = hashlib.md5(installer.read_bytes()).hexdigest()
assert installer_md5 == '1496d181829e74bd60de5fd3f9222185'

frame = json.loads((base / 'verified/framebuffer-verification.json').read_text())
restored = json.loads((base / 'restored-verification/framebuffer-verification.json').read_text())
for key in ('ppm_sha256', 'vram_sha256', 'rgb_sha256'):
    assert frame[key] == restored[key]
assert frame['different_pixels_whole_frame'] == restored['different_pixels_whole_frame'] == 0
processes = json.loads((base / 'window-evidence/processes.json').read_text())
for pid in (2523, 2528, 2533, 2535):
    assert any(row['pid'] == pid and row['xstat'] == 0 and row['task'] != '0x0' for row in processes)
installer_log = base / 'window-evidence/2535-fd2.txt'
server_log = base / 'window-evidence/2528-fd2.txt'
traces = {str(installer_log): installer_log.read_text(), str(server_log): server_log.read_text()}
events = {}
for filename, content in traces.items():
    events[filename] = [{'line': n, 'text': line} for n, line in enumerate(content.splitlines(), 1)
                        if re.search(r'\bid=(29206|29306|29210|29310)\b|guest open .*?(objects\.nib|background\.tif)', line)]
assert any('send id=29206' in row['text'] for row in events[str(installer_log)])
assert any('id=29206' in row['text'] and 'receive port=' in row['text'] for row in events[str(server_log)])
assert any('send id=29306' in row['text'] for row in events[str(server_log)])
acceptance = (base / 'probes1/2484-fd1.txt').read_text()
assert '+ echo probes_completed' in acceptance
assert '+ perl /var/tmp/graphics011-stage102/joint.pl' in acceptance
for filename in [installer_log, server_log, base / 'window-evidence/dir-ats.stderr', base / 'window-evidence/dir-pbs.stderr']:
    assert not re.search(r'^(remaklar: |unsupported |unverified |invalid )', filename.read_text(), re.M), filename
evidence = [installer_log, server_log, base / 'window-evidence/dir-ats.stderr',
            base / 'window-evidence/dir-pbs.stderr', base / 'window-evidence/dir-processes.txt',
            base / 'window-evidence/processes.json', base / 'probes1/2484-fd1.txt',
            base / 'verified/verified-window.png', base / 'verified/framebuffer-verification.json',
            base / 'restored-verification/framebuffer-verification.json',
            base / 'verified/original-CGSCreateWindow-disassembly.txt',
            base / 'verified/original-CGSOrderWindow-disassembly.txt',
            Path('reports/graphics-011/storage88/storage88-complete/original-md5.txt'),
            Path('reports/graphics-011/resume-validation/chain21-through38-reproduction.txt'),
            Path('reports/graphics-011/resume-validation/window102-first-machine-checkpoint.json'),
            Path('reports/graphics-011/resume-validation/window102-painted-machine-checkpoint.json')]
result = {
    'objective': 'First authentic original Jaguar Installer window on original Darwin 6 i386 VESA',
    'result': 'ACHIEVED: original Install window, Authorization page with rejection text and original buttons',
    'visible_text': ['Installer', 'Install', 'Authorization', 'This software cannot be installed on this computer.', 'Go Back', 'Close'],
    'scope': 'First window verified. No installation success or full Installer workflow claimed. Reason for application rejection not established.',
    'original_kernel_md5': '56da829d60b6b4353c25cca8b060b5f8',
    'original_installer_md5': installer_md5,
    'runtime_executor': '/var/tmp/graphics011-build101/qemu-ppc',
    'source_manifest': str(manifest_path), 'source_files_match': source_check,
    'services': {'ATS': 2523, 'WindowServer': 2528, 'pbs': 2533, 'Installer': 2535},
    'framebuffer': frame,
    'restored_checkpoint_identical': True,
    'paused_monitors': {'original_trial102': 4449, 'restored_verification': 4450, 'original_direct66': 4444},
    'direct66_checkpoint_unchanged': direct_check,
    'regression102': {
        'native_and_ppc_capacity': 'PASS, identical stdout; checked by set -e shell before joint launch',
        'previous_executor_negative': 'Expected exit125 at fixed capability ceiling',
        'explicit_names_256_regression': 'PASS exit0/timeout0 before joint launch',
        'acceptance_evidence': str(base / 'probes1/2484-fd1.txt'),
        'joint_trial': 'Paused with live original services and authentic window, before harness cleanup; not claimed completed/exported',
    },
    'trace_events': events,
    'evidence_sha256': {str(path): sha(path) for path in evidence},
}
out.write_text(json.dumps(result, indent=2) + '\n')
print('Verified direct66 unchanged, 18 source hashes, live processes, real CGS request/reply traces, pixel equality and independent checkpoint restore.')
print(out)
