#!/bin/sh
# Final narrow launch probe after real access()/indirect syscall adaptation.
# SPDX-License-Identifier: MIT
set -eu
payload=${1:?payload}
out=${2:?new output directory}
test ! -e "$out"
mkdir "$out"
exec > "$out/session.txt" 2>&1
set -x
cp -Rp /var/tmp/graphics008-run6/source "$out/source"
cp -Rp /var/tmp/graphics008-run6/build "$out/build"
cp "$payload/darwin-kernel.c" "$out/source/darwin-user/remaklar/darwin-kernel.c"
rm "$out/build/ppc-darwin-user/darwin-kernel.o"
make -C "$out/build" SRC_PATH="$out/source" subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc"
{ uname -a;file "$exe";md5 "$exe";file /System/Library/Frameworks/IOKit.framework/Versions/A/IOKit;md5 /System/Library/Frameworks/IOKit.framework/Versions/A/IOKit;md5 /var/tmp/remaklar/build/qemu-darwin6/ppc-darwin-user/qemu-ppc; } > "$out/host.txt"
gcc2 -no-cpp-precomp -arch ppc "$payload/access-runtime.c" -o "$out/access-ppc" > "$out/access-ppc-build.txt" 2>&1
gcc2 -no-cpp-precomp -arch i386 "$payload/access-runtime.c" -o "$out/access-native" > "$out/access-native-build.txt" 2>&1
probe="$payload/run_graphics_008.pl"
perl "$probe" "$out/access-native" "$out/access-native"
perl "$probe" "$out/access-jaguar" "$exe" --root /var/tmp/jaguar "$out/access-ppc"
perl "$probe" "$out/windowserver" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/CoreServices/WindowServer
perl "$probe" "$out/installer" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer
ps -axww > "$out/processes.txt"
echo GRAPHICS_008_ACCESS_COMPLETE
