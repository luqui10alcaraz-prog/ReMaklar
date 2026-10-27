"""Apply numbered graphics deltas to a new copy; never alter the source base."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,os
last=max(int(f.name[:4]) for f in Path('patches/qemu-0.10.6').glob('[0-9][0-9][0-9][0-9]-*.patch'))
p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--dest',type=Path,required=True);p.add_argument('--after',type=int,default=21);p.add_argument('--through',type=int,default=last);args=p.parse_args()
assert args.base.is_dir() and not args.dest.exists();assert 8<=args.after<args.through<=last
patches=[]
for number in range(args.after+1,args.through+1):
 matches=list(Path('patches/qemu-0.10.6').glob('%04d-*.patch'%number));assert len(matches)==1,matches;patches+=matches
manifest_matches=[]
for f in Path('patches/qemu-0.10.6').glob('*manifest.json'):
 m=json.loads(f.read_text())
 if m.get('patch_sha256')==hashlib.sha256(patches[-1].read_bytes()).hexdigest():manifest_matches.append((f,m))
assert len(manifest_matches)==1,manifest_matches
shutil.copytree(args.base,args.dest)
for patch in patches:
 command=(['wsl'] if os.name=='nt' else [])+['patch','-d',args.dest.as_posix(),'-p1']
 r=subprocess.run(command,input=patch.read_bytes(),capture_output=True,timeout=30)
 if r.returncode:raise RuntimeError((r.stdout+r.stderr).decode(errors='replace'))
 print('APPLIED',patch.name)
for name,row in manifest_matches[0][1]['files'].items():
 actual=hashlib.sha256((args.dest/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest();assert actual==row['sha256'],name;print('MATCH',name)
print('VERIFIED',manifest_matches[0][0])
