#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage11
out=/var/tmp/graphics011-run11
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?; echo script_exit=$status > "$out/script-status.txt"; mount -t msdos /dev/disk1 /exchange; cd /var/tmp; gnutar czf /exchange/stage121.tgz graphics011-run11/*.txt graphics011-run11/*.status graphics011-run11/*.stdout graphics011-run11/*.stderr graphics011-run11/*.command;sync;umount /exchange' 0
ln -s /var/tmp/graphics011-run1/source "$out/source"
ln -s /var/tmp/graphics011-run1/build "$out/build"
cp "$p/source/cpu-all.h" "$out/source/cpu-all.h"
cp "$p/source/target-ppc/translate.c" "$out/source/target-ppc/translate.c"
cp "$p/source/target-ppc/helper.h" "$out/source/target-ppc/helper.h"
cp "$p/source/target-ppc/op_helper.c" "$out/source/target-ppc/op_helper.c"
cp "$p/source/darwin-user/remaklar/darwin-kernel.c" "$out/source/darwin-user/remaklar/darwin-kernel.c"
cp "$p/source/darwin-user/remaklar/mach-native.inc" "$out/source/darwin-user/remaklar/mach-native.inc"
cp "$p/source/darwin-user/remaklar/live-regions.inc" "$out/source/darwin-user/remaklar/live-regions.inc"
cp "$p/source/darwin-user/remaklar/typed-live.c" "$out/source/darwin-user/remaklar/typed-live.c"
cp "$p/source/darwin-user/remaklar/typed-live.h" "$out/source/darwin-user/remaklar/typed-live.h"
rm -f "$out/build/ppc-darwin-user/darwin-kernel.o" "$out/build/ppc-darwin-user/translate.o" "$out/build/ppc-darwin-user/op_helper.o"
make -C "$out/build" SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc";cp "$exe" "$out/qemu-ppc"
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/shared011-runtime.c" -framework IOKit -o "$out/shared-$arch" > "$out/shared-$arch-build.txt" 2>&1;done
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
perl "$probe" "$out/shared-native" "$out/shared-i386"
perl "$probe" "$out/shared-jaguar" "$exe" --root /var/tmp/jaguar "$out/shared-ppc"
perl "$probe" "$out/windowserver" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/CoreServices/WindowServer
