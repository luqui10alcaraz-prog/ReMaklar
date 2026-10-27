"""Retry native setup with an explicit real mount-point directory."""
from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
target=Path('build/setup011-129.tgz');assert not target.exists()
with tarfile.open('build/setup011-127.tgz') as source,tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as dest:
 for m in source.getmembers():
  if not m.name.startswith('graphics011-stage127/'):continue
  data=source.extractfile(m).read()
  if m.name.endswith('/run.sh'):
   data=data.replace(b'127',b'129').replace(b'"$out/mount-devfs" /var/tmp/jaguar/dev',b'mkdir -p /var/tmp/jaguar/dev\n"$out/mount-devfs" /var/tmp/jaguar/dev')
  info=Darwin6TarInfo(m.name.replace('stage127/','stage129/'));info.size=len(data);dest.addfile(info,io.BytesIO(data))
Path('build/guest011-setup129.txt').write_text('\nmount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/s129i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage129/run.sh\n')
