from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
with tarfile.open('build/filelock011-96.tgz') as prior:
 members=[]
 for info in prior:
  data=prior.extractfile(info).read();name=info.name.replace('stage96','stage97')
  if info.name.endswith('darwin-kernel.c'):data=Path('build/qemu-011-source/darwin-user/remaklar/darwin-kernel.c').read_bytes().replace(b'\r\n',b'\n')
  if info.name.endswith('run.sh'):data=data.replace(b'96',b'97').replace(b'graphics011-build95/qemu-ppc',b'graphics011-build96/qemu-ppc').replace(b'leader_exit=125',b'leader_exit=1')
  members.append((name,data))
target=Path('build/lockerrors011-97.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-lockerrors97.txt').write_text('mount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/le97i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage97/run.sh\n')
