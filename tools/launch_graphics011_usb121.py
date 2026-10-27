"""New cold-boot overlays, native supported OHCI and USB HID mouse."""
from pathlib import Path
import json,shutil,socket,subprocess,time
root=Path.cwd().resolve();label='input120-kextunload'
assert (root/('reports/graphics-011/resume-validation/'+label+'-machine-checkpoint.json')).is_file()
out=root/'logs/graphics-011-usb121';out.mkdir(exist_ok=False)
disk=root/'vm/darwin602-graphics-011-usb121.qcow2';work=root/'vm/graphics011-usb121-work.qcow2';fat=root/'build/graphics011-usb121-exchange.img'
for path in (disk,work,fat):assert not path.exists()
for backing,target in [(root/('vm/darwin602-graphics-011-'+label+'-preserved.qcow2'),disk),(root/('vm/graphics011-'+label+'-work-preserved.qcow2'),work)]:
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(backing),str(target)],check=True,timeout=30)
shutil.copy2(root/('build/graphics011-'+label+'-preserved-exchange.img'),fat)
args=['qemu-system-i386','-machine','pc-i440fx-5.0','-accel','tcg','-cpu','pentium3','-m','512','-smp','1',
 '-drive',f'file={disk},format=qcow2,if=ide,index=0,cache=writethrough',
 '-drive',f'file={fat},format=raw,if=ide,index=1,cache=directsync',
 '-drive',f'file={root}/build/packages011-104.iso,format=raw,media=cdrom,readonly=on,if=ide,index=2',
 '-drive',f'file={work},format=qcow2,if=ide,index=3,cache=writethrough',
 '-device','pci-ohci,id=ohci','-device','usb-mouse,bus=ohci.0',
 '-boot','c','-nic','none','-vga','std','-display','none','-monitor','tcp:127.0.0.1:4453,server=on,wait=off','-serial',f'file:{out}/serial.log','-no-reboot']
(out/'command.json').write_text(json.dumps(args,indent=2)+'\n')
with (out/'qemu.log').open('wb') as log:p=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
(out/'pid').write_text(str(p.pid));print('New OHCI/native USB mouse clone, PID',p.pid,flush=True)
for i in range(100):
 if p.poll() is not None:raise RuntimeError((out/'qemu.log').read_text())
 try:s=socket.create_connection(('127.0.0.1',4453),timeout=.2);break
 except OSError:time.sleep(.1)
else:raise RuntimeError('Monitor unavailable')
s.settimeout(.1)
for i in range(40):
 s.sendall(b'sendkey spc 30\n');time.sleep(.2)
 try:s.recv(65536)
 except socket.timeout:pass
s.close();print('Boot prompt; inspect before original VESA arguments.',flush=True)
