from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
with tarfile.open('build/input011-105.tgz') as tar:script=tar.extractfile('graphics011-stage105/run.sh').read().decode().replace('105','106')
script=script.replace('test ! -e /var/tmp/jaguar/System/Installation/Packages\nln -s ../../Volumes/CD104/Packages /var/tmp/jaguar/System/Installation/Packages','test -L /var/tmp/jaguar/System/Installation/Packages\nreadlink /var/tmp/jaguar/System/Installation/Packages > "$out/packages-link.txt"')
target=Path('build/input011-106.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in [('run.sh',script.encode()),('hid.c',Path('tests/ppc/hid011-input-runtime.c').read_bytes())]:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage106/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-input106.txt').write_text('\nmount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/in106i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage106/run.sh\n')
