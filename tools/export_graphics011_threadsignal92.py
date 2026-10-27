from pathlib import Path
import difflib,hashlib,json,shutil,subprocess
base=Path('build/011-native-open-locks-patch-check');src=Path('build/qemu-011-source')
prior=json.loads(Path('patches/qemu-0.10.6/graphics-011-native-open-locks-manifest.json').read_text());rows={};parts=[]
for name in prior['files']:
 a=(base/name).read_bytes().replace(b'\r\n',b'\n');b=(src/name).read_bytes().replace(b'\r\n',b'\n')
 parts+=difflib.unified_diff(a.decode().splitlines(True),b.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name)
 rows[name]={'base_sha256':hashlib.sha256(a).hexdigest(),'sha256':hashlib.sha256(b).hexdigest()}
patch=Path('patches/qemu-0.10.6/0030-native-pthread-exit-signals.patch');assert not patch.exists();patch.write_bytes(''.join(parts).encode())
dest=Path('build/011-native-pthread-exit-signals-patch-check');assert not dest.exists();shutil.copytree(base,dest)
with patch.open('rb') as f:
 r=subprocess.run(['wsl','patch','-d',dest.as_posix(),'-p1'],stdin=f,capture_output=True);assert r.returncode==0,r.stdout+r.stderr
for name,row in rows.items():assert hashlib.sha256((dest/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==row['sha256'],name
Path('patches/qemu-0.10.6/graphics-011-native-pthread-exit-signals-manifest.json').write_text(json.dumps({'dependency':'0029-native-open-locks.patch','patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'files':rows,'status':'Probe92 native/PPC original pthread creation, blocked locked-open, cross-thread close, original pthread exit/join pass; previous executor91 fails on private syscall331. Joint92 reaches genuine cache write and missing fsync95.'},indent=2)+'\n')
Path('reports/graphics-011/resume-validation/native-pthread-exit-signals-patch-reproduction.txt').write_text('\n'.join('MATCH '+name for name in rows)+'\n')
print(patch,len(rows),'source files reproduced')
