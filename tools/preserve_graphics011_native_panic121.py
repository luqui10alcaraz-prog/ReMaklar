"""Freeze native USB panic state before releasing its disk locks."""
from pathlib import Path
import hashlib,json,socket,time
state=Path('build/011-usb121-native-panic-state.bin.gz');assert not state.exists()
s=socket.create_connection(('127.0.0.1',4453),timeout=5);s.settimeout(30)
def recv():
 b=b''
 while not b.endswith(b'(qemu) '):
  c=s.recv(65536)
  if not c:raise RuntimeError('monitor disconnected')
  b+=c
 return b.decode(errors='replace')
def cmd(c):s.sendall((c+'\n').encode());return recv()
recv();cmd('stop');cmd('migrate "exec:gzip -1 > %s"'%state.as_posix())
for i in range(240):
 status=cmd('info migrate')
 if 'Migration status: completed' in status:break
 if 'failed' in status:raise RuntimeError(status)
 time.sleep(.25)
else:raise RuntimeError('Migration timeout; leave stopped')
s.sendall(b'quit\n');s.close()
paths=[state,Path('vm/darwin602-graphics-011-usb121.qcow2'),Path('vm/graphics011-usb121-work.qcow2'),Path('build/graphics011-usb121-exchange.img'),Path('build/usb121-native-hang.png'),Path('build/usb121-iohidfamily-loaded.bin')]
record={'result':'native kernel panic, not translator execution','native_pid':146,'trap':0,'eip':'0x31a1866f','module':'original IOHIDFamily 1.2 loaded at 0x31a04000','operation':'IOHIDSystem enableEvents selector1, native i386 regression','ram_compression':'gzip; decompress to QEMU migration input','source_command':'logs/graphics-011-usb121/command.json','files':{str(p):{'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()} for p in paths}}
out=Path('reports/graphics-011/resume-validation/usb121-native-panic-preserved.json');assert not out.exists();out.write_text(json.dumps(record,indent=2)+'\n');print(out,flush=True)
