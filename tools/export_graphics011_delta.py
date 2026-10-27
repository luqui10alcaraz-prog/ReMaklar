"""Export and reproduce one minimal numbered delta over an immutable source base."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,os
p=argparse.ArgumentParser();p.add_argument('--number',type=int,required=True);p.add_argument('--title',required=True);p.add_argument('--base',type=Path,required=True);p.add_argument('--prior-manifest',type=Path,required=True);p.add_argument('--dependency',required=True);p.add_argument('--status',required=True);a=p.parse_args()
assert a.title.replace('-','').isalnum();src=Path('build/qemu-011-source');rows={};parts=[]
prior=json.loads(a.prior_manifest.read_text())
for name in prior['files']:
 old=(a.base/name).read_bytes().replace(b'\r\n',b'\n');new=(src/name).read_bytes().replace(b'\r\n',b'\n')
 parts+=difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name)
 rows[name]={'base_sha256':hashlib.sha256(old).hexdigest(),'sha256':hashlib.sha256(new).hexdigest()}
assert parts,'No source delta'
patch=Path('patches/qemu-0.10.6/%04d-%s.patch'%(a.number,a.title));manifest=Path('patches/qemu-0.10.6/graphics-011-%s-manifest.json'%a.title);dest=Path('build/011-%s-patch-check'%a.title)
assert not patch.exists() and not dest.exists() and not manifest.exists();patch.write_bytes(''.join(parts).encode());shutil.copytree(a.base,dest)
command=(['wsl'] if os.name=='nt' else [])+['patch','-d',dest.as_posix(),'-p1']
r=subprocess.run(command,input=patch.read_bytes(),capture_output=True,timeout=30);assert r.returncode==0,r.stdout+r.stderr
for name,row in rows.items():assert hashlib.sha256((dest/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==row['sha256'],name
manifest.write_text(json.dumps({'dependency':a.dependency,'patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'files':rows,'status':a.status},indent=2)+'\n')
Path('reports/graphics-011/resume-validation/%s-patch-reproduction.txt'%a.title).write_text('\n'.join('MATCH '+name for name in rows)+'\n')
print(patch,len(rows),'source files reproduced')
