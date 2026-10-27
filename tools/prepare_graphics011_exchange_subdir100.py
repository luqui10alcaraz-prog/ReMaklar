"""Preserve full FAT, then relocate one of our own transfer archives to RUNS."""
from pathlib import Path
import subprocess,shutil,hashlib,json
fat=Path('build/graphics011-storage88-exchange.img');backup=Path('build/graphics011-before-subdir100-exchange.img');saved=Path('build/exchange100-original-sw98i.tgz');check=Path('build/exchange100-relocated-sw98i.tgz');report=Path('reports/graphics-011/resume-validation/exchange100-relocation.json')
for p in [backup,saved,check,report]:assert not p.exists(),p
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
shutil.copy2(fat,backup);assert sha(fat)==sha(backup)
subprocess.run(['mcopy','-i',str(fat),'::/sw98i.tgz',str(saved)],check=True)
assert sha(saved)==sha(Path('build/threadswitch011-98.tgz'))
# Only this task's disposable transfer copy is removed; its exact bytes are
# already preserved both independently and in the complete FAT backup.
subprocess.run(['mdel','-i',str(fat),'::/sw98i.tgz'],check=True)
subprocess.run(['mmd','-i',str(fat),'::/RUNS'],check=True)
subprocess.run(['mcopy','-i',str(fat),str(saved),'::/RUNS/sw98i.tgz'],check=True)
subprocess.run(['mcopy','-i',str(fat),'::/RUNS/sw98i.tgz',str(check)],check=True);assert sha(saved)==sha(check)
report.write_text(json.dumps({'precondition':'VM at shell; FAT unmounted after failed missing input100 attempt','backup':str(backup),'backup_sha256':sha(backup),'relocated_from':'/sw98i.tgz','relocated_to':'/RUNS/sw98i.tgz','relocated_file_sha256':sha(check),'original_source':'build/threadswitch011-98.tgz','reason':'Fixed-size FAT16 root directory slots exhausted; preserve all file contents and use expandable subdirectory for subsequent transfers/results'},indent=2)+'\n')
print('Full FAT backup verified; own input98 archive relocated byte-for-byte; RUNS ready.')
