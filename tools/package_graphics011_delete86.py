from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
with tarfile.open('build/delete011-85.tgz') as prior:
 members=[]
 for info in prior:
  data=prior.extractfile(info).read();name=info.name.replace('stage85','stage86')
  if info.name.endswith('darwin-kernel.c'):data=Path('build/qemu-011-source/darwin-user/remaklar/darwin-kernel.c').read_bytes().replace(b'\r\n',b'\n')
  if info.name.endswith('run.sh'):data=data.replace(b'85',b'86')
  members.append((name,data))
target=Path('build/delete011-86.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-delete86.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/del86i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage86/run.sh\n')
print(target,target.stat().st_size)
