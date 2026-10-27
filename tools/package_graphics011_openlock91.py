from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage91
out=/var/tmp/graphics011-openlock91-results
work=/var/tmp/graphics011-build91
test ! -e "$out";test ! -e "$work";mkdir "$out" "$work";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk2 /exchange;cd /var/tmp;paths=graphics011-openlock91-results;if test -d graphics011-joint91;then paths="$paths graphics011-joint91";fi;gnutar czf /exchange/lock91.tgz $paths;sync;umount /exchange' 0
cp "$p/darwin-kernel.c" /var/tmp/graphics011-run1/source/darwin-user/remaklar/darwin-kernel.c
make -C /var/tmp/graphics011-build81/build SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
cp /var/tmp/graphics011-build81/build/ppc-darwin-user/qemu-ppc "$work/qemu-ppc"
exe="$work/qemu-ppc"
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/openlock.c" -o "$out/openlock-$arch" > "$out/openlock-$arch-build.txt" 2>&1;done
export REMAKLAR_QUIET_TLS=1
perl "$probe" "$out/openlock-native" "$out/openlock-i386"
perl "$probe" "$out/openlock-previous" /var/tmp/graphics011-build89/qemu-ppc --root /var/tmp/jaguar "$out/openlock-ppc"
grep -q '^leader_exit=125$' "$out/openlock-previous.status"
perl "$probe" "$out/openlock-jaguar" "$exe" --root /var/tmp/jaguar "$out/openlock-ppc"
cmp "$out/openlock-native.stdout" "$out/openlock-jaguar.stdout"
for mode in native jaguar;do
 grep -q '^leader_exit=0$' "$out/openlock-$mode.status"
 grep -q '^timeout=0$' "$out/openlock-$mode.status"
done
echo probes_completed > "$out/phase.txt"
export REMAKLAR_OBSERVE_APPKIT=1
export REMAKLAR_OBSERVE_APPKIT_OFFSETS=624e0,1c7758,1c779c,1c7800
export REMAKLAR_TRACE_PATHS=1
perl "$p/joint.pl" /var/tmp/graphics011-joint91 "$exe" /var/tmp/jaguar
'''
members=[('run.sh',script.encode()),('joint.pl',Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_bytes()),('openlock.c',Path('tests/ppc/openlock011-runtime.c').read_bytes()),('darwin-kernel.c',Path('build/qemu-011-source/darwin-user/remaklar/darwin-kernel.c').read_bytes())]
target=Path('build/openlock011-91.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage91/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-openlock91.txt').write_text('mount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/lk91i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage91/run.sh\n')
