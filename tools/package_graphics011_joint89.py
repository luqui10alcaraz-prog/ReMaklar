from pathlib import Path
import io,tarfile,json,shlex
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage89
out=/var/tmp/graphics011-run89-results
work=/var/tmp/graphics011-build89
test ! -e "$out";test ! -e "$work";mkdir "$out" "$work";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk2 /exchange;cd /var/tmp;paths=graphics011-run89-results;if test -d graphics011-joint89;then paths="$paths graphics011-joint89";fi;gnutar czf /exchange/joint89.tgz $paths;sync;umount /exchange' 0
df -k > "$out/disk.txt"
md5 /mach_kernel /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer > "$out/original-md5.txt"
'''
for row in json.loads(Path('reports/graphics-011/resume-validation/fonts82-original-cd-manifest.json').read_text())['files']:
 dest=shlex.quote('/var/tmp/jaguar/'+row['path']);script+=f'got=$(md5 {dest});case "$got" in *" = {row["md5"]}") ;; *) exit 30;;esac\n'
script+='''cp "$p/darwin-kernel.c" /var/tmp/graphics011-run1/source/darwin-user/remaklar/darwin-kernel.c
make -C /var/tmp/graphics011-build81/build SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
cp /var/tmp/graphics011-build81/build/ppc-darwin-user/qemu-ppc "$work/qemu-ppc"
exe="$work/qemu-ppc"
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
export REMAKLAR_QUIET_TLS=1
for name in utimes delete;do
 for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/$name.c" -o "$out/$name-$arch" > "$out/$name-$arch-build.txt" 2>&1;done
 perl "$probe" "$out/$name-native" "$out/$name-i386"
 perl "$probe" "$out/$name-previous" /var/tmp/graphics011-build81/qemu-ppc --root /var/tmp/jaguar "$out/$name-ppc"
 grep -q '^leader_exit=125$' "$out/$name-previous.status"
 perl "$probe" "$out/$name-jaguar" "$exe" --root /var/tmp/jaguar "$out/$name-ppc"
 cmp "$out/$name-native.stdout" "$out/$name-jaguar.stdout"
 for mode in native jaguar;do
  grep -q '^leader_exit=0$' "$out/$name-$mode.status"
  grep -q '^timeout=0$' "$out/$name-$mode.status"
 done
done
for name in vmcopy rename fcntl taskthreads priority forkio kinfo ool remoteio remote shared high timer capability trailer threads fasttrap;do
 perl "$probe" "$out/$name-jaguar" "$exe" --root /var/tmp/jaguar "/var/tmp/graphics011-run65/$name-ppc"
 grep -q '^leader_exit=0$' "$out/$name-jaguar.status"
 grep -q '^timeout=0$' "$out/$name-jaguar.status"
done
echo probes_completed > "$out/phase.txt"
export REMAKLAR_OBSERVE_APPKIT=1
export REMAKLAR_OBSERVE_APPKIT_OFFSETS=624e0,1c7758,1c779c,1c7800
export REMAKLAR_TRACE_PATHS=1
perl "$p/joint.pl" /var/tmp/graphics011-joint89 "$exe" /var/tmp/jaguar
'''
members=[('run.sh',script.encode()),('joint.pl',Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_bytes()),('utimes.c',Path('tests/ppc/utimes011-runtime.c').read_bytes()),('delete.c',Path('tests/ppc/delete011-runtime.c').read_bytes()),('darwin-kernel.c',Path('build/qemu-011-source/darwin-user/remaklar/darwin-kernel.c').read_bytes())]
target=Path('build/joint011-89.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage89/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-joint89.txt').write_text('mount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/jnt89i.tgz\ntest ! -e jaguar/System/Library/Fonts && gnutar xzf /exchange/fnt82i.tgz jaguar/System/Library/Fonts\numount /exchange\nsh /var/tmp/graphics011-stage89/run.sh\n')
print(target,target.stat().st_size)
