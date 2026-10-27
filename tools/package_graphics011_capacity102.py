from pathlib import Path
import ast,io,tarfile
from darwin6_tar import Darwin6TarInfo
tree=ast.parse(Path('tools/package_graphics011_threadswitch99.py').read_text())
script=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='script' for t in n.targets)))
script=script.replace('99','102').replace('threadswitch','capacity').replace('graphics011-build98/qemu-ppc','graphics011-build101/qemu-ppc').replace('graphics011-build97/qemu-ppc','graphics011-build100/qemu-ppc').replace('leader_exit=1$','leader_exit=125$').replace('/exchange/swch102.tgz','/exchange/RUNS/cap102.tgz')
script=script.replace('echo probes_completed', '''gcc2 -no-cpp-precomp -arch ppc "$p/stress.c" -o "$out/names-stress-ppc" > "$out/names-stress-build.txt" 2>&1
perl "$probe" "$out/names-stress" "$exe" --root /var/tmp/jaguar "$out/names-stress-ppc"
grep -q '^leader_exit=0$' "$out/names-stress.status"
grep -q '^timeout=0$' "$out/names-stress.status"
echo probes_completed''')
members=[('run.sh',script.encode()),('joint.pl',Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_bytes()),('capacity.c',Path('tests/ppc/capacity011-runtime.c').read_bytes()),('stress.c',Path('tests/ppc/rename-stress011-runtime.c').read_bytes())]
target=Path('build/capacity011-102.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage102/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-capacity102.txt').write_text('mount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/cp102i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage102/run.sh\n')
