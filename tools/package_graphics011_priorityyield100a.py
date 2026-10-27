from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
with tarfile.open('build/priorityyield011-100.tgz') as prior:
 members=[]
 for info in prior:
  data=prior.extractfile(info).read()
  if info.name.endswith('darwin-kernel.c'):data=Path('build/qemu-011-source/darwin-user/remaklar/darwin-kernel.c').read_bytes().replace(b'\r\n',b'\n')
  if info.name.endswith('run.sh'):data=data.replace(b'/exchange/swc100.tgz',b'/exchange/RUNS/swc100.tgz')
  members.append((info.name,data))
target=Path('build/priorityyield011-100a.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-priorityyield100a.txt').write_text('mount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/sy100i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage100/run.sh\n')
