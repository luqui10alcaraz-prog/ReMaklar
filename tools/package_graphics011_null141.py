"""Native bytes from consumed real keys, then original GUI with opaque nulls."""
from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
with tarfile.open('build/null011-138.tgz') as source:
 script=source.extractfile('graphics011-stage138/run.sh').read().decode().replace('138','141')
 joint=source.extractfile('graphics011-stage140/run.sh').read().decode().replace('140','143').replace('build138','build141')
with tarfile.open('build/build011-135.tgz') as source:
 runner=source.extractfile('graphics011-stage136/run.sh').read().decode().replace('136','142').replace('build135','build141').replace('build133','build138').replace('--mouse --tracking','--mouse --tracking --reused-null')
runner=runner.replace("grep -q '^leader_exit=8$'", "grep -q '^leader_exit=125$'")
members=[('graphics011-stage141/run.sh',script.encode()),('graphics011-stage141/hid.c',Path('tests/ppc/hid011-input-runtime.c').read_bytes()),('graphics011-stage142/run.sh',runner.encode()),('graphics011-stage143/run.sh',joint.encode()),('graphics011-stage143/joint.pl',Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_bytes())]
for name in ('darwin-kernel.c','live-regions.inc','typed-live.c','typed-live.h'):members.append(('graphics011-stage141/'+name,Path('build/qemu-011-source/darwin-user/remaklar/'+name).read_bytes()))
for kind in ('bits','tracking','key','mouse','auxmouse','shared','null'):
 name='typed-live-test.c' if kind=='shared' else ('hid-bits011-test.c' if kind=='bits' else 'hid-'+kind+'-fields011-test.c')
 members.append(('graphics011-stage141/'+kind+'.c',Path('tests/memory/'+name).read_bytes()))
target=Path('build/null011-141.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-null141.txt').write_text('\nmount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/n141i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage141/run.sh\n')
Path('build/guest011-joint143.txt').write_text('sh /var/tmp/graphics011-stage143/run.sh\n')
