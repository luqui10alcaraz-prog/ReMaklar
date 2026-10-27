#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage65
out=/var/tmp/graphics011-run65
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?; echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;for f in "$out"/*.txt "$out"/*.status "$out"/*.stdout "$out"/*.stderr;do test ! -f "$f" || echo "${f#/var/tmp/}";done > "$out/export-list.txt";gnutar czf /exchange/stage175.tgz -T "$out/export-list.txt";sync;umount /exchange' 0
ln -s /var/tmp/graphics011-run1/source "$out/source"
cp -Rp /var/tmp/graphics011-run37/build "$out/build"
cmp -s "$p/source/darwin-user/remaklar/kinfo.inc" "$out/source/darwin-user/remaklar/kinfo.inc" || cp "$p/source/darwin-user/remaklar/kinfo.inc" "$out/source/darwin-user/remaklar/kinfo.inc"
cmp -s "$p/source/darwin-user/remaklar/remote-maps.inc" "$out/source/darwin-user/remaklar/remote-maps.inc" || cp "$p/source/darwin-user/remaklar/remote-maps.inc" "$out/source/darwin-user/remaklar/remote-maps.inc"
cmp -s "$p/source/cpu-all.h" "$out/source/cpu-all.h" || cp "$p/source/cpu-all.h" "$out/source/cpu-all.h"
cmp -s "$p/source/darwin-user/mmap.c" "$out/source/darwin-user/mmap.c" || cp "$p/source/darwin-user/mmap.c" "$out/source/darwin-user/mmap.c"
cmp -s "$p/source/darwin-user/remaklar/high-window.c" "$out/source/darwin-user/remaklar/high-window.c" || cp "$p/source/darwin-user/remaklar/high-window.c" "$out/source/darwin-user/remaklar/high-window.c"
cmp -s "$p/source/darwin-user/remaklar/high-window.h" "$out/source/darwin-user/remaklar/high-window.h" || cp "$p/source/darwin-user/remaklar/high-window.h" "$out/source/darwin-user/remaklar/high-window.h"
cmp -s "$p/source/target-ppc/cpu.h" "$out/source/target-ppc/cpu.h" || cp "$p/source/target-ppc/cpu.h" "$out/source/target-ppc/cpu.h"
cmp -s "$p/source/target-ppc/translate.c" "$out/source/target-ppc/translate.c" || cp "$p/source/target-ppc/translate.c" "$out/source/target-ppc/translate.c"
cmp -s "$p/source/target-ppc/helper.h" "$out/source/target-ppc/helper.h" || cp "$p/source/target-ppc/helper.h" "$out/source/target-ppc/helper.h"
cmp -s "$p/source/target-ppc/op_helper.c" "$out/source/target-ppc/op_helper.c" || cp "$p/source/target-ppc/op_helper.c" "$out/source/target-ppc/op_helper.c"
cmp -s "$p/source/darwin-user/remaklar/bootstrap-main.c" "$out/source/darwin-user/remaklar/bootstrap-main.c" || cp "$p/source/darwin-user/remaklar/bootstrap-main.c" "$out/source/darwin-user/remaklar/bootstrap-main.c"
cmp -s "$p/source/darwin-user/qemu.h" "$out/source/darwin-user/qemu.h" || cp "$p/source/darwin-user/qemu.h" "$out/source/darwin-user/qemu.h"
cmp -s "$p/source/darwin-user/remaklar/darwin-kernel.c" "$out/source/darwin-user/remaklar/darwin-kernel.c" || cp "$p/source/darwin-user/remaklar/darwin-kernel.c" "$out/source/darwin-user/remaklar/darwin-kernel.c"
cmp -s "$p/source/darwin-user/remaklar/mach-native.inc" "$out/source/darwin-user/remaklar/mach-native.inc" || cp "$p/source/darwin-user/remaklar/mach-native.inc" "$out/source/darwin-user/remaklar/mach-native.inc"
cmp -s "$p/source/darwin-user/remaklar/live-regions.inc" "$out/source/darwin-user/remaklar/live-regions.inc" || cp "$p/source/darwin-user/remaklar/live-regions.inc" "$out/source/darwin-user/remaklar/live-regions.inc"
cmp -s "$p/source/darwin-user/remaklar/typed-live.c" "$out/source/darwin-user/remaklar/typed-live.c" || cp "$p/source/darwin-user/remaklar/typed-live.c" "$out/source/darwin-user/remaklar/typed-live.c"
cmp -s "$p/source/darwin-user/remaklar/typed-live.h" "$out/source/darwin-user/remaklar/typed-live.h" || cp "$p/source/darwin-user/remaklar/typed-live.h" "$out/source/darwin-user/remaklar/typed-live.h"
cmp -s "$p/source/darwin-user/remaklar/threads.inc" "$out/source/darwin-user/remaklar/threads.inc" || cp "$p/source/darwin-user/remaklar/threads.inc" "$out/source/darwin-user/remaklar/threads.inc"
make -C "$out/build" SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc";cp "$exe" "$out/qemu-ppc"
gcc2 -no-cpp-precomp -arch ppc "$p/threads011-runtime.c" -framework IOKit -o "$out/threads-ppc" > "$out/threads-build.txt" 2>&1
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/high011-runtime.c" -o "$out/high-$arch" > "$out/high-$arch-build.txt" 2>&1;done
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/vmcopy011-runtime.c" -o "$out/vmcopy-$arch" > "$out/vmcopy-$arch-build.txt" 2>&1;done
perl "$probe" "$out/vmcopy-native" "$out/vmcopy-i386"
perl "$probe" "$out/vmcopy-jaguar" "$exe" --root /var/tmp/jaguar "$out/vmcopy-ppc"

for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/rename011-runtime.c" -o "$out/rename-$arch" > "$out/rename-$arch-build.txt" 2>&1;done
perl "$probe" "$out/rename-native" "$out/rename-i386"
perl "$probe" "$out/rename-jaguar" "$exe" --root /var/tmp/jaguar "$out/rename-ppc"

for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/fcntl011-runtime.c" -o "$out/fcntl-$arch" > "$out/fcntl-$arch-build.txt" 2>&1;done
perl "$probe" "$out/fcntl-native" "$out/fcntl-i386"
perl "$probe" "$out/fcntl-jaguar" "$exe" --root /var/tmp/jaguar "$out/fcntl-ppc"

for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/taskthreads011-runtime.c" -o "$out/taskthreads-$arch" > "$out/taskthreads-$arch-build.txt" 2>&1;done
perl "$probe" "$out/taskthreads-native" "$out/taskthreads-i386"
perl "$probe" "$out/taskthreads-jaguar" "$exe" --root /var/tmp/jaguar "$out/taskthreads-ppc"

for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/priority011-runtime.c" -o "$out/priority-$arch" > "$out/priority-$arch-build.txt" 2>&1;done
perl "$probe" "$out/priority-native" "$out/priority-i386"
perl "$probe" "$out/priority-jaguar" "$exe" --root /var/tmp/jaguar "$out/priority-ppc"

mkdir -p /var/tmp/jaguar/System/Library/CoreServices/SystemStarter/QuartzDisplay.bundle/Resources
cp "$p/BootPanel.pdf" /var/tmp/jaguar/System/Library/CoreServices/SystemStarter/QuartzDisplay.bundle/Resources/BootPanel.pdf
md5 /var/tmp/jaguar/System/Library/CoreServices/SystemStarter/QuartzDisplay.bundle/Resources/BootPanel.pdf > "$out/bootpanel-md5.txt"
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/forkio011-runtime.c" -framework IOKit -o "$out/forkio-$arch" > "$out/forkio-$arch-build.txt" 2>&1;done
perl "$probe" "$out/forkio-native" "$out/forkio-i386"
perl "$probe" "$out/forkio-jaguar" "$exe" --root /var/tmp/jaguar "$out/forkio-ppc"

for name in kinfo ool;do
 for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/$name-011.c" -o "$out/$name-$arch" > "$out/$name-$arch-build.txt" 2>&1;done
 perl "$probe" "$out/$name-native" "$out/$name-i386"
 perl "$probe" "$out/$name-jaguar" "$exe" --root /var/tmp/jaguar "$out/$name-ppc"
done

for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/remote011-runtime.c" -o "$out/remote-$arch" > "$out/remote-$arch-build.txt" 2>&1;done
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/remoteio011-runtime.c" -framework IOKit -o "$out/remoteio-$arch" > "$out/remoteio-$arch-build.txt" 2>&1;done
perl "$probe" "$out/remoteio-native" "$out/remoteio-i386"
perl "$probe" "$out/remoteio-jaguar" "$exe" --root /var/tmp/jaguar "$out/remoteio-ppc"
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
