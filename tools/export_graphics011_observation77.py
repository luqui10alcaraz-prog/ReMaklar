from pathlib import Path
import hashlib,json,difflib,subprocess,shutil
base=Path('build/011-ppc-startup-observation-patch-check');src=Path('build/qemu-011-source');prior=json.loads(Path('patches/qemu-0.10.6/graphics-011-ppc-startup-observation-manifest.json').read_text());rows={};parts=[]
for name in prior['files']:
 a=(base/name).read_bytes().replace(b'\r\n',b'\n');b=(src/name).read_bytes().replace(b'\r\n',b'\n');parts+=difflib.unified_diff(a.decode().splitlines(True),b.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name);rows[name]={'base_sha256':hashlib.sha256(a).hexdigest(),'sha256':hashlib.sha256(b).hexdigest()}
patch=Path('patches/qemu-0.10.6/0024-bounded-path-and-nib-observation.patch');assert not patch.exists();patch.write_bytes(''.join(parts).encode())
dest=Path('build/011-observation77-patch-check');assert not dest.exists();shutil.copytree(base,dest)
with patch.open('rb') as f:r=subprocess.run(['wsl','patch','-d',dest.as_posix(),'-p1'],stdin=f,capture_output=True);assert r.returncode==0,r.stdout+r.stderr
for name,row in rows.items():assert hashlib.sha256((dest/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==row['sha256'],name
Path('patches/qemu-0.10.6/graphics-011-observation77-manifest.json').write_text(json.dumps({'dependency':'0023-ppc-startup-observation.patch','patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'files':rows,'status':'Diagnostics only; run77 original nib path found, realpath failed at guest /var; no successful result synthesized'},indent=2)+'\n')
Path('reports/graphics-011/resume-validation/observation77-patch-reproduction.txt').write_text('\n'.join('MATCH '+name for name in rows)+'\n');print('Reproduced',len(rows),'source files.')
