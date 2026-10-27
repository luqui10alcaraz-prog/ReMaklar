from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage99
out=/var/tmp/graphics011-threadswitch99-results
exe=/var/tmp/graphics011-build98/qemu-ppc
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk2 /exchange;cd /var/tmp;paths=graphics011-threadswitch99-results;if test -d graphics011-joint99;then paths="$paths graphics011-joint99";fi;gnutar czf /exchange/swch99.tgz $paths;sync;umount /exchange' 0
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/threadswitch.c" -o "$out/threadswitch-$arch" > "$out/threadswitch-$arch-build.txt" 2>&1;done
export REMAKLAR_QUIET_TLS=1
perl "$probe" "$out/threadswitch-native" "$out/threadswitch-i386"
perl "$probe" "$out/threadswitch-previous" /var/tmp/graphics011-build97/qemu-ppc --root /var/tmp/jaguar "$out/threadswitch-ppc"
grep -q '^leader_exit=1$' "$out/threadswitch-previous.status"
perl "$probe" "$out/threadswitch-jaguar" "$exe" --root /var/tmp/jaguar "$out/threadswitch-ppc"
cmp "$out/threadswitch-native.stdout" "$out/threadswitch-jaguar.stdout"
for mode in native jaguar;do
 grep -q '^leader_exit=0$' "$out/threadswitch-$mode.status"
 grep -q '^timeout=0$' "$out/threadswitch-$mode.status"
done
echo probes_completed > "$out/phase.txt"
export REMAKLAR_JOINT_SAMPLES=72
export REMAKLAR_OBSERVE_APPKIT=1
export REMAKLAR_OBSERVE_APPKIT_OFFSETS=624e0,1c7758,1c779c,1c7800
export REMAKLAR_TRACE_PATHS=1
perl "$p/joint.pl" /var/tmp/graphics011-joint99 "$exe" /var/tmp/jaguar
'''
members=[('run.sh',script.encode()),('joint.pl',Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_bytes()),('threadswitch.c',Path('tests/ppc/threadswitch011-runtime.c').read_bytes())]
target=Path('build/threadswitch011-99.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage99/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-threadswitch99.txt').write_text('mount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/sw99i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage99/run.sh\n')
