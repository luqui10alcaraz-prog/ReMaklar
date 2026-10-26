from pathlib import Path
import tarfile,io
files=['cpu-all.h','darwin-user/mmap.c','darwin-user/remaklar/high-window.c','darwin-user/remaklar/high-window.h','target-ppc/cpu.h','target-ppc/translate.c','target-ppc/helper.h','target-ppc/op_helper.c','darwin-user/remaklar/bootstrap-main.c','darwin-user/qemu.h','darwin-user/remaklar/darwin-kernel.c','darwin-user/remaklar/mach-native.inc','darwin-user/remaklar/live-regions.inc','darwin-user/remaklar/typed-live.c','darwin-user/remaklar/typed-live.h','darwin-user/remaklar/threads.inc']
s='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage41
out=/var/tmp/graphics011-run41
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?; echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/stage151.tgz graphics011-run41/*.txt graphics011-run41/*.status graphics011-run41/*.stdout graphics011-run41/*.stderr;sync;umount /exchange' 0
ln -s /var/tmp/graphics011-run1/source "$out/source"
cp -Rp /var/tmp/graphics011-run37/build "$out/build"
'''
for f in files:s+=f'cmp -s "$p/source/{f}" "$out/source/{f}" || cp "$p/source/{f}" "$out/source/{f}"\n'
s+='''make -C "$out/build" SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc";cp "$exe" "$out/qemu-ppc"
gcc2 -no-cpp-precomp -arch ppc "$p/threads011-runtime.c" -framework IOKit -o "$out/threads-ppc" > "$out/threads-build.txt" 2>&1
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/high011-runtime.c" -o "$out/high-$arch" > "$out/high-$arch-build.txt" 2>&1;done
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/remote011-runtime.c" -o "$out/remote-$arch" > "$out/remote-$arch-build.txt" 2>&1;done
perl "$probe" "$out/remote-native" "$out/remote-i386"
perl "$probe" "$out/remote-jaguar" "$exe" --root /var/tmp/jaguar "$out/remote-ppc"

for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/trailer011-runtime.c" -o "$out/trailer-$arch" > "$out/trailer-$arch-build.txt" 2>&1;done
perl "$probe" "$out/trailer-native" "$out/trailer-i386"
perl "$probe" "$out/trailer-previous" /var/tmp/graphics011-run32/qemu-ppc --root /var/tmp/jaguar "$out/trailer-ppc"
perl "$probe" "$out/trailer-jaguar" "$exe" --root /var/tmp/jaguar "$out/trailer-ppc"

gcc2 -no-cpp-precomp -arch ppc "$p/fasttrap011-runtime.c" -o "$out/fasttrap-ppc" > "$out/fasttrap-build.txt" 2>&1
perl "$probe" "$out/fasttrap" "$exe" --root /var/tmp/jaguar "$out/fasttrap-ppc"
perl "$probe" "$out/fasttrap-previous" /var/tmp/graphics011-run26/qemu-ppc --root /var/tmp/jaguar "$out/fasttrap-ppc"
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/capability011-runtime.c" -o "$out/capability-$arch" > "$out/capability-$arch-build.txt" 2>&1;done
perl "$probe" "$out/capability-native" "$out/capability-i386"
perl "$probe" "$out/capability-jaguar" "$exe" --root /var/tmp/jaguar "$out/capability-ppc"
perl "$probe" "$out/capability-previous" /var/tmp/graphics011-run26/qemu-ppc --root /var/tmp/jaguar "$out/capability-ppc"
perl "$probe" "$out/high-native" "$out/high-i386"
perl "$probe" "$out/high-jaguar" "$exe" --root /var/tmp/jaguar "$out/high-ppc"
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/timer011-runtime.c" -o "$out/timer-$arch" > "$out/timer-$arch-build.txt" 2>&1;done
perl "$probe" "$out/timer-native" "$out/timer-i386"
perl "$probe" "$out/timer-jaguar" "$exe" --root /var/tmp/jaguar "$out/timer-ppc"
perl "$probe" "$out/threads" "$exe" --root /var/tmp/jaguar "$out/threads-ppc"
gcc2 -no-cpp-precomp -arch i386 -O2 -I"$p/source/darwin-user/remaklar" "$p/source/darwin-user/remaklar/typed-live.c" "$p/typed-live-test.c" -o "$out/typed-native" > "$out/typed-build.txt" 2>&1
perl "$probe" "$out/typed-native" "$out/typed-native"
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/shared011-runtime.c" -framework IOKit -o "$out/shared-$arch" > "$out/shared-$arch-build.txt" 2>&1;done
perl "$probe" "$out/shared-native" "$out/shared-i386"
perl "$probe" "$out/shared-jaguar" "$exe" --root /var/tmp/jaguar "$out/shared-ppc"
perl "$probe" "$out/pbs" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/CoreServices/pbs
perl "$probe" "$out/windowserver" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/CoreServices/WindowServer
'''
Path('scripts/darwin6-graphics-011-threads.sh').write_text(s)
with tarfile.open('build/stage151-in.tgz','w:gz') as t:
 for name,data in [('run.sh',s.encode()),('remote011-runtime.c',Path('tests/ppc/remote011-runtime.c').read_bytes()),('trailer011-runtime.c',Path('tests/ppc/trailer011-runtime.c').read_bytes()),('threads011-runtime.c',Path('tests/ppc/threads011-runtime.c').read_bytes()),('high011-runtime.c',Path('tests/ppc/high011-runtime.c').read_bytes()),('timer011-runtime.c',Path('tests/ppc/timer011-runtime.c').read_bytes()),('capability011-runtime.c',Path('tests/ppc/capability011-runtime.c').read_bytes()),('fasttrap011-runtime.c',Path('tests/ppc/fasttrap011-runtime.c').read_bytes()),('shared011-runtime.c',Path('tests/ppc/shared011-runtime.c').read_bytes()),('typed-live-test.c',Path('tests/memory/typed-live-test.c').read_bytes()),* [('source/'+f,Path('build/qemu-011-source',f).read_bytes()) for f in files]]:
  data=data.replace(b'\r\n',b'\n');i=tarfile.TarInfo('graphics011-stage41/'+name);i.size=len(data);t.addfile(i,io.BytesIO(data))
Path('build/guest011-threads.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/stage151i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage41/run.sh\n')
