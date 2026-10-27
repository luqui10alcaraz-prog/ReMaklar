"""Use actual native device filesystem and input preferences, then disk oracle."""
from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage127
out=/var/tmp/graphics011-setup127
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/RUNS/setup127.tgz graphics011-setup127;sync;umount /exchange' 0
gcc2 -no-cpp-precomp -arch i386 "$p/mount-devfs.c" -o "$out/mount-devfs" > "$out/devfs-build.txt" 2>&1
mkdir -p /var/tmp/jaguar/dev
"$out/mount-devfs" /var/tmp/jaguar/dev > "$out/devfs.txt"
gcc2 -no-cpp-precomp -arch i386 "$p/preferences.c" -framework IOKit -framework CoreFoundation -o "$out/preferences" > "$out/preferences-build.txt" 2>&1
"$out/preferences" > "$out/preferences.txt"
ls -l /var/tmp/jaguar/dev/rdisk* /var/tmp/jaguar/dev/console > "$out/devices.txt"
mount > "$out/mounts.txt"
ioreg -l -w 0 > "$out/ioreg.txt"
md5 /mach_kernel /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer > "$out/original-md5.txt"
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/names.c" -framework IOKit -framework CoreFoundation -o "$out/names-$arch" > "$out/names-$arch-build.txt" 2>&1;done
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
export REMAKLAR_QUIET_TLS=1
perl "$probe" "$out/names-native" "$out/names-i386" disk2s1
perl "$probe" "$out/names-previous" /var/tmp/graphics011-build112/qemu-ppc --root /var/tmp/jaguar "$out/names-ppc" disk2s1
grep -q '^leader_exit=125$' "$out/names-previous.status"
perl "$probe" "$out/names-jaguar" /var/tmp/graphics011-build122/qemu-ppc --root /var/tmp/jaguar "$out/names-ppc" disk2s1
cmp "$out/names-native.stdout" "$out/names-jaguar.stdout"
for mode in native jaguar;do grep -q '^leader_exit=0$' "$out/names-$mode.status";grep -q '^timeout=0$' "$out/names-$mode.status";done
echo setup_and_names_complete > "$out/phase.txt"
'''
members=[('graphics011-stage127/run.sh',script.encode()),('graphics011-stage127/preferences.c',Path('tests/native/hid-preferences011.c').read_bytes()),('graphics011-stage127/mount-devfs.c',Path('tests/native/mount-devfs011.c').read_bytes()),('graphics011-stage127/names.c',Path('tests/ppc/registry-name011-runtime.c').read_bytes())]
with tarfile.open('build/joint011-124.tgz') as tar:
 for name in ('graphics011-stage125/run.sh','graphics011-stage125/joint.pl'):members.append((name,tar.extractfile(name).read()))
target=Path('build/setup011-127.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-setup127.txt').write_text('\nmount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/s127i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage127/run.sh\n')
