"""Build minimal dup2 fix; native/PPC/negative regression, then original GUI."""
from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage131
out=/var/tmp/graphics011-dup131-results
work=/var/tmp/graphics011-build131
test ! -e "$out";test ! -e "$work";mkdir "$out" "$work";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/RUNS/dup131.tgz graphics011-dup131-results;sync;umount /exchange' 0
cp "$p/darwin-kernel.c" /var/tmp/graphics011-run1/source/darwin-user/remaklar/
make -C /var/tmp/graphics011-build81/build SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
cp /var/tmp/graphics011-build81/build/ppc-darwin-user/qemu-ppc "$work/qemu-ppc"
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/dup2.c" -o "$out/dup2-$arch" > "$out/dup2-$arch-build.txt" 2>&1;done
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
export REMAKLAR_QUIET_TLS=1
perl "$probe" "$out/native" "$out/dup2-i386"
perl "$probe" "$out/previous" /var/tmp/graphics011-build122/qemu-ppc --root /var/tmp/jaguar "$out/dup2-ppc"
grep -q '^leader_exit=125$' "$out/previous.status"
perl "$probe" "$out/jaguar" "$work/qemu-ppc" --root /var/tmp/jaguar "$out/dup2-ppc"
cmp "$out/native.stdout" "$out/jaguar.stdout"
for mode in native jaguar;do grep -q '^leader_exit=0$' "$out/$mode.status";grep -q '^timeout=0$' "$out/$mode.status";done
echo dup2_regression_complete > "$out/phase.txt"
'''
with tarfile.open('build/joint011-124.tgz') as tar:joint=tar.extractfile('graphics011-stage125/run.sh').read().decode().replace('125','132').replace('build122','build131')
members=[('graphics011-stage131/run.sh',script.encode()),('graphics011-stage131/dup2.c',Path('tests/ppc/dup2-011-runtime.c').read_bytes()),('graphics011-stage131/darwin-kernel.c',Path('build/qemu-011-source/darwin-user/remaklar/darwin-kernel.c').read_bytes()),('graphics011-stage132/run.sh',joint.encode()),('graphics011-stage132/joint.pl',Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_bytes())]
target=Path('build/dup011-131.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-dup131.txt').write_text('\nmount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/d131i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage131/run.sh\n')
Path('build/guest011-joint132.txt').write_text('sh /var/tmp/graphics011-stage132/run.sh\n')
