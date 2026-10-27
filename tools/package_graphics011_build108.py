from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage108
out=/var/tmp/graphics011-build108-results
work=/var/tmp/graphics011-build108
test ! -e "$out";test ! -e "$work";mkdir "$out" "$work";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk2 /exchange;cd /var/tmp;gnutar czf /exchange/RUNS/build108.tgz graphics011-build108-results;sync;umount /exchange' 0
mount > "$out/mounts.txt"
md5 /mach_kernel /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer > "$out/original-md5.txt"
mkdir -p /var/tmp/jaguar/Volumes/CD104 /var/tmp/jaguar/System/Installation
mount -t cd9660 /dev/disk3s0 /var/tmp/jaguar/Volumes/CD104
test ! -e /var/tmp/jaguar/System/Installation/Packages
ln -s ../../Volumes/CD104/Packages /var/tmp/jaguar/System/Installation/Packages
md5 /var/tmp/jaguar/System/Installation/Packages/OSInstall.mpkg/Contents/Info.plist > "$out/osinstall-md5.txt"
grep -q ' = 839f63c9c9366ff0c88d97934d774865$' "$out/osinstall-md5.txt"
for file in darwin-kernel.c live-regions.inc typed-live.c typed-live.h;do cp "$p/$file" /var/tmp/graphics011-run1/source/darwin-user/remaklar/;done
make -C /var/tmp/graphics011-build81/build SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
cp /var/tmp/graphics011-build81/build/ppc-darwin-user/qemu-ppc "$work/qemu-ppc"
gcc2 -no-cpp-precomp -arch i386 -I"$p" "$p/hid-key-fields.c" "$p/typed-live.c" -o "$out/fields-i386" > "$out/fields-build.txt" 2>&1
"$out/fields-i386" > "$out/fields.stdout" 2> "$out/fields.stderr"
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/hid.c" -framework IOKit -framework CoreFoundation -o "$out/hid-$arch" > "$out/build-$arch.txt" 2>&1;done
echo build_completed > "$out/phase.txt"
'''
members=[('run.sh',script.encode()),('hid.c',Path('tests/ppc/hid011-input-runtime.c').read_bytes()),('hid-key-fields.c',Path('tests/memory/hid-key-fields011-test.c').read_bytes())]
for name in ['darwin-kernel.c','live-regions.inc','typed-live.c','typed-live.h']:members.append((name,Path('build/qemu-011-source/darwin-user/remaklar/'+name).read_bytes()))
target=Path('build/build011-108.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage108/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-build108.txt').write_text('\nmount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/b108i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage108/run.sh\n')
