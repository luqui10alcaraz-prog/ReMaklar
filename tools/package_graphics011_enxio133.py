"""Verify native ENXIO propagation, then prepare the next bounded GUI run."""
from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
with tarfile.open('build/dup011-131.tgz') as source:
 script=source.extractfile('graphics011-stage131/run.sh').read().decode().replace('131','133').replace('dup2','tty').replace('dup133','enxio133').replace('graphics011-build122/qemu-ppc','graphics011-build131/qemu-ppc')
 joint=source.extractfile('graphics011-stage132/run.sh').read().decode().replace('132','134').replace('build131','build133')
members=[('graphics011-stage133/run.sh',script.encode()),('graphics011-stage133/tty.c',Path('tests/ppc/tty-enxio011-runtime.c').read_bytes()),('graphics011-stage133/darwin-kernel.c',Path('build/qemu-011-source/darwin-user/remaklar/darwin-kernel.c').read_bytes()),('graphics011-stage134/run.sh',joint.encode()),('graphics011-stage134/joint.pl',Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_bytes())]
target=Path('build/enxio011-133.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-enxio133.txt').write_text('\nmount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/e133i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage133/run.sh\n')
Path('build/guest011-joint134.txt').write_text('sh /var/tmp/graphics011-stage134/run.sh\n')
