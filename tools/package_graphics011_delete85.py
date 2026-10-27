from pathlib import Path
import ast,io,tarfile
from darwin6_tar import Darwin6TarInfo
tree=ast.parse(Path('tools/package_graphics011_utimes83.py').read_text())
script=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='script' for t in n.targets)))
script=script.replace('83','85').replace('utimes','delete').replace('graphics011-build81/qemu-ppc','graphics011-build83/qemu-ppc')
script=script.replace('gnutar czf /exchange/utim85.tgz graphics011-delete85-results graphics011-joint85;', 'paths=graphics011-delete85-results;if test -d graphics011-joint85;then paths="$paths graphics011-joint85";fi;gnutar czf /exchange/dele85.tgz $paths;')
joint=Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_text().replace('if(/^unsupported ','if(/^remaklar: / || /^unsupported ')
members=[('run.sh',script.encode()),('joint.pl',joint.encode()),('delete.c',Path('tests/ppc/delete011-runtime.c').read_bytes()),('darwin-kernel.c',Path('build/qemu-011-source/darwin-user/remaklar/darwin-kernel.c').read_bytes())]
target=Path('build/delete011-85.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage85/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-delete85.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/del85i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage85/run.sh\n')
print(target,target.stat().st_size)
