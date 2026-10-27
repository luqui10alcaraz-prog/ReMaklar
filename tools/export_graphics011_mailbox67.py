"""Export isolated, verifiable deltas over 0021; never commit or push."""
from pathlib import Path
import difflib,hashlib,json,shutil,subprocess
base=Path('build/011-vmcopy-patch-check');src=Path('build/qemu-011-source')
prior=json.loads(Path('patches/qemu-0.10.6/graphics-011-vmcopy-manifest.json').read_text())
names=list(prior['files'])
for number,title,changed in [(22,'mailbox-lifecycle',['darwin-user/remaklar/remote-maps.inc']),(23,'ppc-startup-observation',['darwin-user/qemu.h','darwin-user/remaklar/bootstrap-main.c','darwin-user/remaklar/darwin-kernel.c'])]:
 patch=Path('patches/qemu-0.10.6/%04d-%s.patch'%(number,title));assert not patch.exists()
 parts=[];rows={}
 for name in names:
  old=(base/name).read_bytes().replace(b'\r\n',b'\n');new=(src/name).read_bytes().replace(b'\r\n',b'\n') if name in changed else old
  parts+=difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name)
  rows[name]={'base_sha256':hashlib.sha256(old).hexdigest(),'sha256':hashlib.sha256(new).hexdigest()}
 patch.write_bytes(''.join(parts).encode())
 dest=Path('build/011-%s-patch-check'%title);assert not dest.exists();shutil.copytree(base,dest)
 with patch.open('rb') as f:r=subprocess.run(['wsl','patch','-d',dest.as_posix(),'-p1'],stdin=f,capture_output=True);assert r.returncode==0,r.stdout+r.stderr
 for name,row in rows.items():assert hashlib.sha256((dest/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==row['sha256'],name
 manifest={'dependency':'0021-real-kernel-vm-copy.patch' if number==22 else '0022-mailbox-lifecycle.patch','patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'files':rows,'status':'run67 lifecycle and 17 translated probes passed; joint67 completes cleanup; original Installer still exits 1 in NSApplicationMain' if number==22 else 'Diagnostics only: bounded original PPC exit backtrace; opt-in AppKit observation breakpoints'}
 Path('patches/qemu-0.10.6/graphics-011-%s-manifest.json'%title).write_text(json.dumps(manifest,indent=2)+'\n')
 Path('reports/graphics-011/resume-validation/%s-patch-reproduction.txt'%title).write_text('\n'.join('MATCH '+name for name in names)+'\n');base=dest
 print(patch,len(rows),'sources reproduced')
