#!/bin/sh
set -eu
out=/var/tmp/graphics009-run12
payload=/var/tmp/graphics009-r12
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
src=/var/tmp/graphics009-run2/source
build=/var/tmp/graphics009-run2/build
cp "$src/darwin-user/remaklar/darwin-kernel.c" "$out/prior-darwin-kernel.c"
cp "$payload/darwin-kernel.c" "$src/darwin-user/remaklar/darwin-kernel.c"
rm -f "$build/ppc-darwin-user/darwin-kernel.o"
make -C "$build" SRC_PATH="$src" subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$build/ppc-darwin-user/qemu-ppc";cp "$exe" "$out/qemu-ppc"
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$payload/graphics-system-runtime.c" -o "$out/system-$arch" > "$out/system-$arch-build.txt" 2>&1;done
perl "$probe" "$out/system-native" "$out/system-i386"
perl "$probe" "$out/system-jaguar" "$exe" --root /var/tmp/jaguar "$out/system-ppc"
perl "$probe" "$out/splash" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Installation/CDIS/splash /Applications/Utilities/Installer.app/Contents/MacOS/Installer
ps -axww > "$out/processes.txt"
echo RUN12_COMPLETE
