"""Restore a complete lab checkpoint into fresh overlays, initially stopped.

Run under WSL from the repository root. Preserved files are only read.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shlex
import shutil
import socket
import subprocess
import time
import re

p = argparse.ArgumentParser()
p.add_argument('--from-label', required=True)
p.add_argument('--as-label', required=True)
p.add_argument('--port', required=True, type=int)
p.add_argument('--display', choices=('none', 'gtk'), default='none')
a = p.parse_args()
for label in (a.from_label, a.as_label):
    assert label.replace('-', '').isalnum()
assert 1024 <= a.port <= 65535
root = Path.cwd().resolve()
manifest = root / ('reports/graphics-011/resume-validation/%s-machine-checkpoint.json' % a.from_label)
record = json.loads(manifest.read_text())
cd_record = record.get('cdrom')
cdrom = root / (cd_record['file'] if cd_record else 'build/graphics009-recovery.iso')
if cd_record:
    assert cdrom.stat().st_size == cd_record['bytes'], cdrom
    with cdrom.open('rb') as f:
        assert hashlib.file_digest(f, 'sha256').hexdigest() == cd_record['sha256'], cdrom
out = root / ('logs/graphics-011-restore-%s' % a.as_label)
disk = root / ('vm/darwin602-graphics-011-%s-restored.qcow2' % a.as_label)
work = root / ('vm/graphics011-%s-restored-work.qcow2' % a.as_label)
fat = root / ('build/graphics011-%s-restored-exchange.img' % a.as_label)
for target in (out, disk, work, fat):
    assert not target.exists(), target
try:
    with socket.create_connection(('127.0.0.1', a.port), timeout=.2):
        raise RuntimeError('Monitor port is already in use')
except ConnectionRefusedError:
    pass
for name, expected in record['files'].items():
    source = root / name
    assert source.stat().st_size == expected['bytes'], source
    with source.open('rb') as f:
        assert hashlib.file_digest(f, 'sha256').hexdigest() == expected['sha256'], source
    print('VERIFIED', name, flush=True)

saved_root = root / ('vm/darwin602-graphics-011-%s-preserved.qcow2' % a.from_label)
saved_work = root / ('vm/graphics011-%s-work-preserved.qcow2' % a.from_label)
saved_fat = root / ('build/graphics011-%s-preserved-exchange.img' % a.from_label)
saved_ram = root / ('build/011-%s-machine-state.bin' % a.from_label)
out.mkdir()
for backing, target in ((saved_root, disk), (saved_work, work)):
    subprocess.run(['qemu-img', 'create', '-f', 'qcow2', '-F', 'qcow2',
                    '-b', str(backing), str(target)], check=True, timeout=30)
shutil.copy2(saved_fat, fat)
command = [
    'qemu-system-i386', '-machine', 'pc-i440fx-5.0', '-accel', 'tcg',
    '-cpu', 'pentium3', '-m', '512', '-smp', '1',
    '-drive', f'file={disk},format=qcow2,if=ide,index=0,cache=writethrough',
    '-drive', f'file={fat},format=raw,if=ide,index=1,cache=directsync',
    '-drive', f'file={cdrom},format=raw,media=cdrom,readonly=on,if=ide,index=2',
    '-drive', f'file={work},format=qcow2,if=ide,index=3,cache=writethrough',
    '-boot', 'c', '-nic', 'none', '-vga', 'std',
    '-display', ('gtk,gl=off,grab-on-hover=off' if a.display == 'gtk' else 'none'),
    '-name', 'ReMaklar 0.11 - ' + a.as_label,
    '-monitor', f'tcp:127.0.0.1:{a.port},server=on,wait=off',
    '-serial', f'file:{out}/serial.log', '-no-reboot', '-S',
    '-incoming', 'exec:cat ' + shlex.quote(str(saved_ram)),
]
command += record.get('hardware_extra_args', [])
(out / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
with (out / 'qemu.log').open('wb') as log:
    child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log,
                             stderr=log, start_new_session=True)
(out / 'pid').write_text(str(child.pid) + '\n')
for i in range(200):
    if child.poll() is not None:
        raise RuntimeError((out / 'qemu.log').read_text())
    try:
        s = socket.create_connection(('127.0.0.1', a.port), timeout=.2)
        break
    except OSError:
        time.sleep(.1)
else:
    raise RuntimeError('No monitor within 20 seconds; inspect recorded PID and logs')
s.settimeout(30)
def receive():
    data = b''
    while not data.endswith(b'(qemu) '):
        chunk = s.recv(65536)
        if not chunk:
            raise RuntimeError('Monitor disconnected')
        data += chunk
    return data.decode(errors='replace')
receive()
print('Esperando a que termine de cargarse la migracion...', flush=True)
deadline = time.monotonic() + 60
while time.monotonic() < deadline:
    if child.poll() is not None:
        raise RuntimeError((out / 'qemu.log').read_text())
    s.sendall(b'info status\n')
    status = receive()
    if 'VM status: paused' in status and 'inmigrate' not in status:
        break
    time.sleep(.2)
else:
    raise RuntimeError('La migracion no completo en 60 segundos; revisar el PID y los logs')
for command in ['screendump ' + json.dumps(str(out / 'restored.ppm')),
                'pmemsave 0xfd000000 3145728 ' + json.dumps(str(out / 'restored.vram'))]:
    s.sendall((command + '\n').encode())
    receive()
if record.get('mouse_device'):
    s.sendall(b'info mice\n')
    mice = receive()
    match = re.search(r'Mouse #(\d+): ' + re.escape(record['mouse_device']), mice)
    assert match, mice
    s.sendall(('mouse_set ' + match.group(1) + '\n').encode())
    receive()
s.close()
(out / 'initial-status.txt').write_text(status)
for saved, restored in [(root / ('build/011-%s-preserved.ppm' % a.from_label), out / 'restored.ppm'),
                         (root / ('build/011-%s-preserved-vram.bin' % a.from_label), out / 'restored.vram')]:
    assert restored.read_bytes() == saved.read_bytes(), 'La imagen restaurada no coincide: ' + str(restored)
print('Restored into fresh overlays, stopped. PID=%d monitor=%d' % (child.pid, a.port), flush=True)
