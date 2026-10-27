from pathlib import Path
import difflib,hashlib,json,shutil,subprocess
base=Path('build/011-observation77-patch-check');src=Path('build/qemu-011-source');prior=json.loads(Path('patches/qemu-0.10.6/graphics-011-observation77-manifest.json').read_text());names=list(prior['files'])
for number,title,changed,dependency in [(25,'growing-explicit-mach-names',['darwin-user/remaklar/mach-native.inc','darwin-user/remaklar/darwin-kernel.c'],'0024-bounded-path-and-nib-observation.patch'),(26,'bounded-error-tracing',['darwin-user/remaklar/bootstrap-main.c'],'0025-growing-explicit-mach-names.patch')]:
 patch=Path('patches/qemu-0.10.6/%04d-%s.patch'%(number,title));assert not patch.exists();parts=[];rows={}
 for name in names:
  a=(base/name).read_bytes().replace(b'\r\n',b'\n');b=(src/name).read_bytes().replace(b'\r\n',b'\n') if name in changed else a
  parts+=difflib.unified_diff(a.decode().splitlines(True),b.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name);rows[name]={'base_sha256':hashlib.sha256(a).hexdigest(),'sha256':hashlib.sha256(b).hexdigest()}
 patch.write_bytes(''.join(parts).encode());dest=Path('build/011-%s-patch-check'%title);assert not dest.exists();shutil.copytree(base,dest)
 with patch.open('rb') as f:r=subprocess.run(['wsl','patch','-d',dest.as_posix(),'-p1'],stdin=f,capture_output=True);assert r.returncode==0,r.stdout+r.stderr
 for name,row in rows.items():assert hashlib.sha256((dest/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==row['sha256'],name
 Path('patches/qemu-0.10.6/graphics-011-%s-manifest.json'%title).write_text(json.dumps({'dependency':dependency,'patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'files':rows,'status':'run81 native/PPC 256 concurrent explicit names, delivery collision destroy/reuse x2 and 17 accumulated translated probes pass; original Installer window pending' if number==25 else 'Diagnostic only: fatal errors have a stable prefix; opt-in suppression of TLS-only trace noise; Mach/BSD operations still traced'},indent=2)+'\n')
 Path('reports/graphics-011/resume-validation/%s-patch-reproduction.txt'%title).write_text('\n'.join('MATCH '+name for name in rows)+'\n');base=dest;print(patch,len(rows),'source files reproduced')
