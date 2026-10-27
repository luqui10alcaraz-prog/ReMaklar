from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage83
out=/var/tmp/graphics011-utimes83-results
work=/var/tmp/graphics011-build83
test ! -e "$out";test ! -e "$work";mkdir "$out" "$work";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/utim83.tgz graphics011-utimes83-results graphics011-joint83;sync;umount /exchange' 0
df -k / > "$out/disk.txt"
cp "$p/darwin-kernel.c" /var/tmp/graphics011-run1/source/darwin-user/remaklar/darwin-kernel.c
make -C /var/tmp/graphics011-build81/build SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
cp /var/tmp/graphics011-build81/build/ppc-darwin-user/qemu-ppc "$work/qemu-ppc"
exe="$work/qemu-ppc"
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/utimes.c" -o "$out/utimes-$arch" > "$out/utimes-$arch-build.txt" 2>&1;done
perl "$probe" "$out/utimes-native" "$out/utimes-i386"
perl "$probe" "$out/utimes-previous" /var/tmp/graphics011-build81/qemu-ppc --root /var/tmp/jaguar "$out/utimes-ppc"
grep -q '^leader_exit=125$' "$out/utimes-previous.status"
export REMAKLAR_QUIET_TLS=1
perl "$probe" "$out/utimes-jaguar" "$exe" --root /var/tmp/jaguar "$out/utimes-ppc"
cmp "$out/utimes-native.stdout" "$out/utimes-jaguar.stdout"
for mode in native jaguar;do
 grep -q '^leader_exit=0$' "$out/utimes-$mode.status"
 grep -q '^timeout=0$' "$out/utimes-$mode.status"
done
df -k / >> "$out/disk.txt"
echo probes_completed > "$out/phase.txt"
export REMAKLAR_OBSERVE_APPKIT=1
export REMAKLAR_OBSERVE_APPKIT_OFFSETS=624e0,1c7758,1c779c,1c7800
export REMAKLAR_TRACE_PATHS=1
perl "$p/joint.pl" /var/tmp/graphics011-joint83 "$exe" /var/tmp/jaguar
'''
joint=Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_text().replace('if(/^unsupported ','if(/^remaklar: / || /^unsupported ')
members=[('run.sh',script.encode()),('joint.pl',joint.encode()),('utimes.c',Path('tests/ppc/utimes011-runtime.c').read_bytes()),('darwin-kernel.c',Path('build/qemu-011-source/darwin-user/remaklar/darwin-kernel.c').read_bytes())]
target=Path('build/utimes011-83.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage83/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-utimes83.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/ut83i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage83/run.sh\n')
print(target,target.stat().st_size)
