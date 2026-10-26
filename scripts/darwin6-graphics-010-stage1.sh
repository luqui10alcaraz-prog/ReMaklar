#!/bin/sh
set -eu
payload=/var/tmp/graphics010-stage1
out=/var/tmp/graphics010-run1
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
cp -Rp /var/tmp/graphics009-run2/source "$out/source"
cp -Rp /var/tmp/graphics009-run2/build "$out/build"
for name in darwin-kernel.c bootstrap-main.c bootstrap.h mach-native.inc;do cp "$payload/$name" "$out/source/darwin-user/remaklar/$name";done
rm -f "$out/build/ppc-darwin-user/darwin-kernel.o"
make -C "$out/build" SRC_PATH="$out/source" subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc";cp "$exe" "$out/qemu-ppc"
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$payload/mach010-runtime.c" -o "$out/mach-$arch" > "$out/mach-$arch-build.txt" 2>&1;done
cp "$out/mach-ppc" /var/tmp/jaguar/tmp/mach010-r1.ppc
perl "$probe" "$out/mach-native" "$out/mach-i386" "$out/mach-i386"
perl "$probe" "$out/mach-jaguar" "$exe" --root /var/tmp/jaguar "$out/mach-ppc" /tmp/mach010-r1.ppc
perl "$probe" "$out/installer" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer
perl "$probe" "$out/windowserver" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/CoreServices/WindowServer
perl "$probe" "$out/splash" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Installation/CDIS/splash /Applications/Utilities/Installer.app/Contents/MacOS/Installer
ps -axww > "$out/processes.txt"
echo GRAPHICS010_STAGE1_COMPLETE
