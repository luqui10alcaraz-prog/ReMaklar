"""Stage selected laboratory evidence; keep VM/media/raw dumps local."""
from pathlib import Path
import argparse,json,subprocess
p=argparse.ArgumentParser();p.add_argument('--stage',action='store_true');a=p.parse_args()
names=subprocess.check_output(['git','ls-files','--others','--ignored','--exclude-standard','-z','reports/graphics-011']).decode().split('\0')
extensions={'.json','.txt','.stdout','.stderr','.status','.command','.md','.csv'}
screens={
 'reports/graphics-011/capacity102/verified/verified-window.png',
 'reports/graphics-011/capacity102/restored-verification/verified-window.png',
 'reports/graphics-011/joint134/captures/1793076709806847518.png',
 'reports/graphics-011/joint134/captures/1793076731754132378.png',
}
selected=[]
for name in names:
 if not name:continue
 f=Path(name)
 if f.name=='registers.txt':continue
 if (f.suffix in extensions and f.stat().st_size<=5000000) or name in screens:selected.append(name)
manifest=Path('reports/graphics-011/resume-validation/publication-20261027.json')
assert not manifest.exists()
record={'date':'2026-10-27','checkpoint':'input141-publication','source_patch':48,'native_executor_md5':'8ea0af3748c5c6dbe19be84f4db5e9c3','verified':['authentic Installer window102 and independent restore','physical VESA pointer displacement134','native/PPC actual key, pointer, click, auxiliary and tracking events123/136','native dup2 and ENXIO comparisons131/133','build141: seven native memory tests and initialized kernel-null oracle'], 'pending':['actual consumed-key null payload probes142','original GUI joint143 with executor141','independent restore of input141-publication','Installer installation flow remains blocked'], 'published_new_evidence_files':len(selected),'published_new_evidence_bytes':sum(Path(n).stat().st_size for n in selected),'local_only':'Original media, RAM, VM disks, FAT exchange files, compiled executables and raw framebuffer dumps are preserved locally and excluded from this commit.'}
if a.stage:
 manifest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');selected.append(manifest.as_posix())
 listing=Path('build/publication141-paths.nul');listing.write_bytes(('\0'.join(selected)+'\0').encode())
 subprocess.run(['git','add','-f','--pathspec-from-file='+listing.as_posix(),'--pathspec-file-nul'],check=True)
print(json.dumps(record,indent=2))
