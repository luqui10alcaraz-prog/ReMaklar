#!/bin/sh
# Reuse the verified native build; replace only the changed personality object.
# SPDX-License-Identifier: MIT
set -eu
payload=${1:?payload directory}
out=${2:?new work directory}
test ! -e "$out"
mkdir "$out"
exec > "$out/session.txt" 2>&1
set -x
cp -Rp /var/tmp/remaklar/experiments/qemu-0.10.6 "$out/source"
cp -Rp /var/tmp/remaklar/build/qemu-darwin6 "$out/build"
cp "$payload/darwin-kernel.c" "$out/source/darwin-user/remaklar/darwin-kernel.c"
# Overridden SRC_PATH leaves original source/build paths intact. The remaining
# object files are from that recorded 0.06 native build, not a clean rebuild.
rm "$out/build/ppc-darwin-user/darwin-kernel.o"
make -C "$out/build" SRC_PATH="$out/source" subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc"
{ uname -a; file "$exe"; md5 "$exe"; } > "$out/host.txt"
gcc2 -no-cpp-precomp -arch ppc "$payload/process-runtime.c" -o "$out/process-ppc" > "$out/process-build.txt" 2>&1
gcc2 -no-cpp-precomp -arch i386 "$payload/process-runtime.c" -o "$out/process-i386" > "$out/process-native-build.txt" 2>&1
perl "$payload/run_graphics_008.pl" "$out/process-native" "$out/process-i386"
perl "$payload/run_graphics_008.pl" "$out/process-raw" "$exe" "$payload/process-008.macho"
perl "$payload/run_graphics_008.pl" "$out/process-darwin" "$exe" --root /var/tmp/remaklar/research/samples-local "$out/process-ppc"
perl "$payload/run_graphics_008.pl" "$out/process-jaguar" "$exe" --root /var/tmp/jaguar "$out/process-ppc"
perl "$payload/run_graphics_008.pl" "$out/windowserver" "$exe" --root /var/tmp/jaguar "/var/tmp/jaguar/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/CoreGraphics.framework/Versions/A/Resources/Window Manager"
echo GRAPHICS_008_COMPLETE
