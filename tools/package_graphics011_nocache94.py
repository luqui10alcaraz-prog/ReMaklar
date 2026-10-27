from pathlib import Path
import ast,io,tarfile
from darwin6_tar import Darwin6TarInfo
tree=ast.parse(Path('tools/package_graphics011_openlock91.py').read_text())
script=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='script' for t in n.targets)))
script=script.replace('91','94').replace('openlock','nocache').replace('graphics011-build89/qemu-ppc','graphics011-build93/qemu-ppc').replace('/exchange/lock94.tgz','/exchange/noca94.tgz')
members=[('run.sh',script.encode()),('joint.pl',Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_bytes()),('nocache.c',Path('tests/ppc/nocache011-runtime.c').read_bytes()),('darwin-kernel.c',Path('build/qemu-011-source/darwin-user/remaklar/darwin-kernel.c').read_bytes())]
target=Path('build/nocache011-94.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage94/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-nocache94.txt').write_text('mount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/nc94i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage94/run.sh\n')
