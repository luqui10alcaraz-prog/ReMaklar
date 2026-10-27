from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage84
out=/var/tmp/graphics011-utimes84-results
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;paths=graphics011-utimes84-results;if test -d graphics011-joint84;then paths="$paths graphics011-joint84";fi;gnutar czf /exchange/utim84.tgz $paths;sync;umount /exchange' 0
exe=/var/tmp/graphics011-build83/qemu-ppc
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
df -k / > "$out/disk.txt"
echo probes_completed > "$out/phase.txt"
export REMAKLAR_OBSERVE_APPKIT=1
export REMAKLAR_OBSERVE_APPKIT_OFFSETS=624e0,1c7758,1c779c,1c7800
export REMAKLAR_TRACE_PATHS=1
perl "$p/joint.pl" /var/tmp/graphics011-joint84 "$exe" /var/tmp/jaguar
'''
joint=Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_text().replace('if(/^unsupported ','if(/^remaklar: / || /^unsupported ')
members=[('run.sh',script.encode()),('joint.pl',joint.encode()),('utimes.c',Path('tests/ppc/utimes011-runtime.c').read_bytes())]
target=Path('build/utimes011-84.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  info=Darwin6TarInfo('graphics011-stage84/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-utimes84.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/ut84i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage84/run.sh\n')
Path('build/guest011-unmount83.txt').write_text('umount /exchange\n')
print(target,target.stat().st_size)
