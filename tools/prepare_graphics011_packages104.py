"""Build a read-only data CD containing complete, original Jaguar packages."""
from pathlib import Path
import hashlib,json,stat,subprocess,tempfile

iso=Path('build/packages011-104.iso');manifest=Path('reports/graphics-011/resume-validation/packages104-original-cd-manifest.json')
assert not iso.exists() and not manifest.exists()
source=Path('media/Mac OS X Jaguar Install CD.iso')
prefix='Mac OS X Install Disc 1/System/Installation/Packages'
temp=Path(tempfile.mkdtemp(prefix='remaklar-packages104-'))
report=Path('reports/graphics-011/packages104');report.mkdir(exist_ok=False)
listing=subprocess.run(['7z','l','-slt',str(source),prefix+'/*'],capture_output=True,check=True,timeout=30)
(report/'source-listing.txt').write_bytes(listing.stdout)
print('Extracting complete original package trees into',temp,flush=True)
r=subprocess.run(['7z','x','-y','-o'+str(temp),str(source),prefix+'/*'],capture_output=True,check=True,timeout=120)
(report/'extraction.txt').write_bytes(r.stdout+r.stderr)
tree=temp/prefix;rows=[]
for path in sorted(tree.rglob('*')):
 mode=stat.S_IMODE(path.lstat().st_mode)
 row={'path':path.relative_to(tree).as_posix(),'mode':oct(mode)}
 if path.is_symlink():row.update(type='symlink',target=path.readlink().as_posix())
 elif path.is_file():
  with path.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
  row.update(type='file',bytes=path.stat().st_size,sha256=sha)
 else:row.update(type='directory')
 rows.append(row)
print('Original tree:',len(rows),'entries;',sum(r.get('bytes',0) for r in rows),'bytes. Building ISO.',flush=True)
subprocess.run(['genisoimage','-quiet','-R','-J','-input-charset','utf-8','-V','JAGUARPKGS104','-o',str(iso),'-graft-points','Packages='+str(tree)],check=True,timeout=60)
with iso.open('rb') as f:iso_sha=hashlib.file_digest(f,'sha256').hexdigest()
with source.open('rb') as f:source_sha=hashlib.file_digest(f,'sha256').hexdigest()
manifest.write_text(json.dumps({'original_cd':str(source),'original_cd_sha256':source_sha,'source_prefix':prefix,'extracted_tree':str(tree),'data_iso':str(iso),'data_iso_sha256':iso_sha,'entries':rows},indent=2)+'\n')
print('Prepared',iso,iso.stat().st_size,'bytes. Original package contents unchanged.',flush=True)
