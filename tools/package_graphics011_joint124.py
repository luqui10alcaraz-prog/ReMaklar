"""Mount native devfs and run all original Jaguar GUI services with patch43."""
from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
setup='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage124
out=/var/tmp/graphics011-setup124
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/RUNS/setup124.tgz graphics011-setup124;sync;umount /exchange' 0
gcc2 -no-cpp-precomp -arch i386 "$p/mount-devfs.c" -o "$out/mount-devfs" > "$out/build.txt" 2>&1
"$out/mount-devfs" /var/tmp/jaguar/dev > "$out/devfs.txt"
ls -l /var/tmp/jaguar/dev/rdisk* /var/tmp/jaguar/dev/console > "$out/devices.txt"
mount > "$out/mounts.txt"
'''
with tarfile.open('build/joint011-111.tgz') as tar:joint=tar.extractfile('graphics011-stage111/run.sh').read().decode()
joint=joint.replace('111','125').replace('/dev/disk2 /exchange','/dev/disk1 /exchange').replace('graphics011-build108/qemu-ppc','graphics011-build122/qemu-ppc')
target=Path('build/joint011-124.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in [('graphics011-stage124/run.sh',setup.encode()),('graphics011-stage124/mount-devfs.c',Path('tests/native/mount-devfs011.c').read_bytes()),('graphics011-stage125/run.sh',joint.encode()),('graphics011-stage125/joint.pl',Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_bytes())]:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-setup124.txt').write_text('\nmount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/j124i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage124/run.sh\n')
Path('build/guest011-joint125.txt').write_text('sh /var/tmp/graphics011-stage125/run.sh\n')
