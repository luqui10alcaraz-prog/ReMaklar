"""Cold boot new overlays; keep the native IOHID panic clone stopped."""
from pathlib import Path
import argparse,json,shutil,socket,subprocess,time
p=argparse.ArgumentParser();p.add_argument('--retry-failed-launch',action='store_true');opt=p.parse_args()
root=Path.cwd().resolve();out=root/'logs/graphics-011-usb126'
if not opt.retry_failed_launch:out.mkdir(exist_ok=False)
args=json.loads((root/'logs/graphics-011-usb121/command.json').read_text())
for source,target in [('vm/darwin602-graphics-011-usb121.qcow2','vm/darwin602-graphics-011-usb126.qcow2'),('vm/graphics011-usb121-work.qcow2','vm/graphics011-usb126-work.qcow2')]:
 if not opt.retry_failed_launch:
  assert not (root/target).exists()
  subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(root/source),str(root/target)],check=True,timeout=30)
fat=root/'build/graphics011-usb126-exchange.img'
if not opt.retry_failed_launch:
 assert not fat.exists();shutil.copy2(root/'build/graphics011-usb121-exchange.img',fat)
args=[x.replace('usb121','usb126').replace(':4453,',':4454,') for x in args]
if not opt.retry_failed_launch:(out/'command.json').write_text(json.dumps(args,indent=2)+'\n')
index=1
while (out/('launch%d.log'%index)).exists():index+=1
logpath=out/('launch%d.log'%index)
with logpath.open('xb') as log:p=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
(out/('pid-launch%d'%index)).write_text(str(p.pid));print('New OHCI recovery clone PID',p.pid,flush=True)
for i in range(100):
 if p.poll() is not None:raise RuntimeError(logpath.read_text())
 try:s=socket.create_connection(('127.0.0.1',4454),timeout=.2);break
 except OSError:time.sleep(.1)
else:raise RuntimeError('Monitor unavailable')
s.settimeout(.1)
for i in range(40):
 s.sendall(b'sendkey spc 30\n');time.sleep(.2)
 try:s.recv(65536)
 except socket.timeout:pass
s.close();print('Boot prompt: inspect before VESA boot flags.',flush=True)
