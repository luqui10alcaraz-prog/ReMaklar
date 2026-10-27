"""Finish native preferences with the actual CF ABI; devfs is already mounted."""
from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
with tarfile.open('build/setup011-127.tgz') as source:
 script=source.extractfile('graphics011-stage127/run.sh').read().decode().replace('127','130')
script='\n'.join(line for line in script.split('\n') if 'mount-devfs' not in line)
members=[('run.sh',script.encode()),('preferences.c',Path('tests/native/hid-preferences011.c').read_bytes()),('names.c',Path('tests/ppc/registry-name011-runtime.c').read_bytes())]
target=Path('build/setup011-130.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage130/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-setup130.txt').write_text('\nmount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/s130i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage130/run.sh\n')
