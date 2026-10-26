"""Export the ongoing 0.11 delta without overwriting verified checkpoints."""
from pathlib import Path
import difflib, hashlib, json
root=Path(__file__).resolve().parents[1]
patchdir=root/'patches/qemu-0.10.6'
prior=json.loads((patchdir/'graphics-011-progress-manifest.json').read_text())
base=root/'build/011-progress-patch-check'
current=root/'build/qemu-011-source'
parts=[];manifest={}
for name,record in prior['files'].items():
 old=(base/name).read_bytes().replace(b'\r\n',b'\n')
 assert hashlib.sha256(old).hexdigest()==record['sha256'],name
 new=(current/name).read_bytes().replace(b'\r\n',b'\n')
 parts+=difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name)
 manifest[name]={'base_sha256':record['sha256'],'sha256':hashlib.sha256(new).hexdigest()}
p=patchdir/'0012-mach-receive-trailers.patch'
p.write_bytes(''.join(parts).encode())
(patchdir/'graphics-011-trailer-manifest.json').write_text(json.dumps({'dependency':'0011-live-framebuffer-thread-progress.patch','dependency_sha256':hashlib.sha256((patchdir/'0011-live-framebuffer-thread-progress.patch').read_bytes()).hexdigest(),'patch_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':manifest,'status':'run37 trailer candidate: original Installer GUI not yet verified'},indent=2)+'\n')
print(p.name,p.stat().st_size,'bytes')
