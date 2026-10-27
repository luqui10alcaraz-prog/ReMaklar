from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
with tarfile.open('build/input011-115.tgz') as tar:
 script=tar.extractfile('graphics011-stage115/run.sh').read().decode().replace('115','118')
 runner=tar.extractfile('graphics011-stage116/run.sh').read().decode().replace('116','119').replace('input115-results','input118-results')
target=Path('build/input011-118.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in [('graphics011-stage118/run.sh',script.encode()),('graphics011-stage118/hid.c',Path('tests/ppc/hid011-input-runtime.c').read_bytes()),('graphics011-stage119/run.sh',runner.encode())]:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-input118.txt').write_text('\nmount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/in118i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage118/run.sh\n')
