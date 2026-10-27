"""Preserve a stopped 512MB lab VM and all disks, refusing any overwrite."""
from pathlib import Path
import argparse,socket,time,shutil,json,hashlib,subprocess
p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--port',type=int,required=True);p.add_argument('--root',type=Path,required=True);p.add_argument('--fat',type=Path,required=True);p.add_argument('--work-raw','--work',dest='work_raw',type=Path,required=True);p.add_argument('--work-format',choices=('raw','qcow2'),default='raw');p.add_argument('--compress-work',action='store_true');p.add_argument('--cdrom',type=Path,default=Path('build/graphics009-recovery.iso'));p.add_argument('--usb-mouse',action='store_true');p.add_argument('--ohci-mouse',action='store_true');p.add_argument('--work-device',default='/dev/disk1s1');p.add_argument('--exchange-device',default='/dev/disk2');p.add_argument('--mouse-device');p.add_argument('--reason',required=True);a=p.parse_args();assert a.label.replace('-','').isalnum();assert not(a.usb_mouse and a.ohci_mouse)
ram=Path('build/011-%s-machine-state.bin'%a.label);vram=Path('build/011-%s-preserved-vram.bin'%a.label);screen=Path('build/011-%s-preserved.ppm'%a.label)
root=Path('vm/darwin602-graphics-011-%s-preserved.qcow2'%a.label);fat=Path('build/graphics011-%s-preserved-exchange.img'%a.label);work=Path('vm/graphics011-%s-work-preserved.qcow2'%a.label);manifest=Path('reports/graphics-011/resume-validation/%s-machine-checkpoint.json'%a.label)
for f in [ram,vram,screen,root,fat,work,manifest]:assert not f.exists(),f
for f in [a.root,a.fat,a.work_raw,a.cdrom]:assert f.is_file(),f
s=socket.create_connection(('127.0.0.1',a.port),timeout=5);s.settimeout(30)
def recv():
 b=b''
 while not b.endswith(b'(qemu) '):
  c=s.recv(65536)
  if not c:raise RuntimeError('monitor disconnected')
  b+=c
 return b.decode(errors='replace')
def cmd(c):s.sendall((c+'\n').encode());return recv()
recv();cmd('stop');cmd('screendump '+screen.as_posix());cmd('pmemsave 0xfd000000 3145728 '+vram.as_posix());cmd('migrate "exec:cat > %s"'%ram.as_posix())
for i in range(120):
 status=cmd('info migrate')
 if 'Migration status: completed' in status:break
 if 'failed' in status:raise RuntimeError(status)
 time.sleep(.25)
else:raise RuntimeError('Migration remains active; leave stopped')
s.close();shutil.copy2(a.root,root);shutil.copy2(a.fat,fat)
# -U is only used to read a source disk with the VM stopped and migration complete.
subprocess.run(['qemu-img','convert','-U','-f',a.work_format,'-O','qcow2','-S','4096']+(['-c'] if a.compress_work else [])+[str(a.work_raw),str(work)],check=True,timeout=120)
files=[ram,vram,screen,root,fat,work];record={'reason':a.reason,'monitor':a.port,'state':'stopped after complete migration; RAM includes guest filesystem cache and live kernel ports/locks','source_disks':{'root':str(a.root),'fat':str(a.fat),'work':str(a.work_raw)},'guest_mounts':{'root':'/dev/disk0s2','work':'/dev/disk1s1 on /var/tmp','exchange':'/dev/disk2 on /exchange'},'files':{str(f):{'bytes':f.stat().st_size,'sha256':hashlib.file_digest(f.open('rb'),'sha256').hexdigest()} for f in files}}
with a.cdrom.open('rb') as f:cd_hash=hashlib.file_digest(f,'sha256').hexdigest()
record['cdrom']={'file':str(a.cdrom),'bytes':a.cdrom.stat().st_size,'sha256':cd_hash}
record['guest_mounts']['work']=a.work_device+' on /var/tmp'
record['guest_mounts']['exchange']=a.exchange_device+' on /exchange'
record['hardware_extra_args']=['-device','pci-ohci,id=ohci','-device','usb-mouse,bus=ohci.0'] if a.ohci_mouse else (['-usb','-device','usb-mouse'] if a.usb_mouse else [])
record['mouse_device']=a.mouse_device
manifest.write_text(json.dumps(record,indent=2)+'\n');print('Preserved',manifest,'VM remains stopped.',flush=True)
