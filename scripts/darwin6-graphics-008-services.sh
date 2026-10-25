#!/bin/sh
# Measured exec-state and native IOKit iteration; prior outputs stay intact.
# SPDX-License-Identifier: MIT
set -eu
payload=${1:?payload}
out=${2:?new output directory}
test ! -e "$out"
mkdir "$out"
exec > "$out/session.txt" 2>&1
set -x
cp -Rp /var/tmp/graphics008-run2/source "$out/source"
cp -Rp /var/tmp/graphics008-run2/build "$out/build"
for name in darwin-kernel.c bootstrap-main.c bootstrap.h; do cp "$payload/$name" "$out/source/darwin-user/remaklar/$name";done
rm "$out/build/ppc-darwin-user/darwin-kernel.o" "$out/build/ppc-darwin-user/bootstrap-main.o"
make -C "$out/build" SRC_PATH="$out/source" subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc"
{ uname -a;file "$exe";md5 "$exe"; } > "$out/host.txt"
test ! -e /var/tmp/jaguar/System/Library/Printers/Libraries/libPPDLib.dylib
gnutar xzf "$payload/printing-originals.tgz" -C /var/tmp/jaguar
for name in exec-runtime iokit-runtime; do
    extra='';if [ "$name" = iokit-runtime ];then extra='-framework IOKit';fi
    gcc2 -no-cpp-precomp -arch ppc "$payload/$name.c" $extra -o "$out/$name-ppc" > "$out/$name-ppc-build.txt" 2>&1
    gcc2 -no-cpp-precomp -arch i386 "$payload/$name.c" $extra -o "$out/$name-i386" > "$out/$name-native-build.txt" 2>&1
done
cp "$out/exec-runtime-ppc" /var/tmp/remaklar/research/samples-local/tmp/exec-008-stage4.ppc
cp "$out/exec-runtime-ppc" /var/tmp/jaguar/tmp/exec-008-stage4.ppc
perl "$payload/run_graphics_008.pl" "$out/exec-native" "$out/exec-runtime-i386" "$out/exec-runtime-i386"
perl "$payload/run_graphics_008.pl" "$out/exec-darwin" "$exe" --root /var/tmp/remaklar/research/samples-local "$out/exec-runtime-ppc" /tmp/exec-008-stage4.ppc
perl "$payload/run_graphics_008.pl" "$out/exec-jaguar" "$exe" --root /var/tmp/jaguar "$out/exec-runtime-ppc" /tmp/exec-008-stage4.ppc
perl "$payload/run_graphics_008.pl" "$out/iokit-native" "$out/iokit-runtime-i386"
perl "$payload/run_graphics_008.pl" "$out/iokit-darwin" "$exe" --root /var/tmp/remaklar/research/samples-local "$out/iokit-runtime-ppc"
perl "$payload/run_graphics_008.pl" "$out/iokit-jaguar" "$exe" --root /var/tmp/jaguar "$out/iokit-runtime-ppc"
perl "$payload/run_graphics_008.pl" "$out/process-regression" "$exe" --root /var/tmp/jaguar /var/tmp/graphics008-run1/process-ppc
perl "$payload/run_graphics_008.pl" "$out/windowserver" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/CoreServices/WindowServer
perl "$payload/run_graphics_008.pl" "$out/splash" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Installation/CDIS/splash /Applications/Utilities/Installer.app/Contents/MacOS/Installer
perl "$payload/run_graphics_008.pl" "$out/installer" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer
echo GRAPHICS_008_SERVICES_COMPLETE
