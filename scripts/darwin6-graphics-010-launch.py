#!/usr/bin/env python3
"""Launch the preserved 0.10 graphics overlay under the existing WSL QEMU.

Requires a cleanly halted copy of the development overlay, rebased to the
unchanged Darwin base, and a separate copy of the FAT exchange image.
Does not create, overwrite, rebase, or install disk images.
SPDX-License-Identifier: MIT
"""
from pathlib import Path
import socket
import subprocess
import time

root = Path(__file__).resolve().parents[1]
disk = root / 'vm/darwin602-graphics-010-overlay.qcow2'
exchange = root / 'build/graphics010-exchange.img'
cdrom = root / 'build/graphics009-recovery.iso'
for path in (disk, exchange, cdrom):
    if not path.is_file():
        raise SystemExit('Required preserved image missing: ' + str(path))
try:
    with socket.create_connection(('127.0.0.1', 4444), timeout=0.2):
        raise SystemExit('Monitor 4444 is already in use; existing VM left alone.')
except OSError:
    pass
logdir = root / 'logs/graphics-010'
logdir.mkdir(parents=True, exist_ok=True)
args = ['qemu-system-i386', '-machine', 'pc-i440fx-5.0', '-accel', 'tcg',
        '-cpu', 'pentium3', '-m', '128', '-smp', '1',
        '-drive', f'file={disk},format=qcow2,if=ide,index=0,cache=writethrough',
        '-drive', f'file={exchange},format=raw,if=ide,index=1,cache=directsync',
        '-drive', f'file={cdrom},format=raw,media=cdrom,readonly=on,if=ide,index=2',
        '-boot', 'c', '-nic', 'none', '-vga', 'std', '-display', 'none',
        '-monitor', 'tcp:127.0.0.1:4444,server=on,wait=off',
        '-serial', f'file:{logdir}/graphics-boot-serial.log', '-no-reboot']
(logdir / 'graphics-launch.command').write_text('\n'.join(args) + '\n')
with (logdir / 'graphics-boot-vm.log').open('ab') as output:
    process = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=output,
                               stderr=output, start_new_session=True)
(logdir / 'graphics-vm.pid').write_text(str(process.pid) + '\n')
print('QEMU PID', process.pid, flush=True)
for attempt in range(100):
    try:
        connection = socket.create_connection(('127.0.0.1', 4444), timeout=0.2)
        break
    except OSError:
        if process.poll() is not None:
            raise SystemExit('QEMU exited; inspect graphics-boot-vm.log')
        time.sleep(0.1)
else:
    raise SystemExit('Monitor unavailable; VM retained for inspection.')
with connection:
    connection.settimeout(0.1)
    for index in range(20):
        connection.sendall(b'sendkey spc 50\n')
        time.sleep(0.15)
        try:
            connection.recv(65536)
        except socket.timeout:
            pass
print('Inspect boot prompt, then type documented VESA boot arguments.', flush=True)
process.wait()
