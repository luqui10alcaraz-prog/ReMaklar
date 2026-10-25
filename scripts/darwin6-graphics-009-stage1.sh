#!/bin/sh
# Native incremental statfs/IOKit tests; preserves all 0.08 outputs. SPDX-License-Identifier: MIT
set -eu
payload=${1:?payload};out=${2:?new output}
test ! -e "$out";mkdir "$out"
exec > "$out/session.txt" 2>&1
set -x
cp -Rp /var/tmp/graphics008-run7/source "$out/source"
cp -Rp /var/tmp/graphics008-run7/build "$out/build"
cp "$payload/darwin-kernel.c" "$out/source/darwin-user/remaklar/darwin-kernel.c"
rm "$out/build/ppc-darwin-user/darwin-kernel.o"
make -C "$out/build" SRC_PATH="$out/source" subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc"
{ uname -a;file "$exe";md5 "$exe"; } > "$out/host.txt"
probe="$payload/run_graphics_008.pl"
for name in statfs-runtime iokit-open-runtime;do
 extra='';if [ "$name" = iokit-open-runtime ];then extra='-framework IOKit';fi
 gcc2 -no-cpp-precomp -arch i386 "$payload/$name.c" $extra -o "$out/$name-i386" > "$out/$name-native-build.txt" 2>&1
 gcc2 -no-cpp-precomp -arch ppc "$payload/$name.c" $extra -o "$out/$name-ppc" > "$out/$name-ppc-build.txt" 2>&1
 perl "$probe" "$out/$name-native" "$out/$name-i386"
 perl "$probe" "$out/$name-jaguar" "$exe" --root /var/tmp/jaguar "$out/$name-ppc"
done
perl "$probe" "$out/installer" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer
perl "$probe" "$out/splash" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Installation/CDIS/splash /Applications/Utilities/Installer.app/Contents/MacOS/Installer
ps -axww > "$out/processes.txt"
echo GRAPHICS009_STAGE1_COMPLETE
