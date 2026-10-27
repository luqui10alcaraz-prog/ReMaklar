from pathlib import Path
import ast,hashlib,io,tarfile
from darwin6_tar import Darwin6TarInfo
tree=ast.parse(Path('tools/package_graphics011_input104.py').read_text())
script=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='script' for t in n.targets))).replace('104','105')
md5=hashlib.md5(Path('build/osinstall104-original/Mac OS X Install Disc 1/System/Installation/Packages/OSInstall.mpkg/Contents/Info.plist').read_bytes()).hexdigest()
script=script.replace('for arch in i386 ppc;do', '''mkdir -p /var/tmp/jaguar/Volumes/CD104 /var/tmp/jaguar/System/Installation
mount -t cd9660 /dev/disk3s0 /var/tmp/jaguar/Volumes/CD104
test ! -e /var/tmp/jaguar/System/Installation/Packages
ln -s ../../Volumes/CD104/Packages /var/tmp/jaguar/System/Installation/Packages
md5 /var/tmp/jaguar/System/Installation/Packages/OSInstall.mpkg/Contents/Info.plist > "$out/osinstall-md5.txt"
grep -q ' = '''+md5+'''$' "$out/osinstall-md5.txt"
mount > "$out/mounts-after.txt"
for arch in i386 ppc;do''')
target=Path('build/input011-105.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in [('run.sh',script.encode()),('hid.c',Path('tests/ppc/hid011-input-runtime.c').read_bytes())]:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage105/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-input105.txt').write_text('\nmount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/in105i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage105/run.sh\n')
