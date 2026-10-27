"""Build patch43 and compare actual USB HID input on the cold-boot clone."""
from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
with tarfile.open('build/build011-113.tgz') as tar:
 script=tar.extractfile('graphics011-stage113/run.sh').read().decode().replace('113','122')
script=script.replace('/dev/disk2 /exchange','/dev/disk1 /exchange')
script=script.replace('for kind in key mouse;','for kind in key mouse auxmouse;')
script=script.replace('build_and_names_completed','build43_and_names_completed')
with tarfile.open('build/input011-118.tgz') as tar:
 runner=tar.extractfile('graphics011-stage119/run.sh').read().decode()
runner=runner.replace('119','123').replace('/dev/disk2 /exchange','/dev/disk1 /exchange')
runner=runner.replace('graphics011-input118-results','graphics011-build122-results')
runner=runner.replace('graphics011-build112/qemu-ppc','graphics011-build113/qemu-ppc').replace('j) perl "$probe" "$out/probe" /var/tmp/graphics011-build113/qemu-ppc','j) perl "$probe" "$out/probe" /var/tmp/graphics011-build122/qemu-ppc')
members=[('graphics011-stage122/run.sh',script.encode()),('graphics011-stage123/run.sh',runner.encode()),('graphics011-stage122/hid.c',Path('tests/ppc/hid011-input-runtime.c').read_bytes()),('graphics011-stage122/names.c',Path('tests/ppc/registry-name011-runtime.c').read_bytes())]
for kind in ('key','mouse','auxmouse'):
 members.append(('graphics011-stage122/hid-'+kind+'-fields.c',Path('tests/memory/hid-'+kind+'-fields011-test.c').read_bytes()))
for name in ['darwin-kernel.c','live-regions.inc','typed-live.c','typed-live.h']:
 members.append(('graphics011-stage122/'+name,Path('build/qemu-011-source/darwin-user/remaklar/'+name).read_bytes()))
target=Path('build/build011-122.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-build122.txt').write_text('\nmount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/b122i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage122/run.sh\n')
