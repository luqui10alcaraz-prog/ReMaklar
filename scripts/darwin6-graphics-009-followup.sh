#!/bin/sh
# Native follow-up; reuse an existing source/build and preserve a new output.
# SPDX-License-Identifier: MIT
set -eu
payload=${1:?payload directory}
out=${2:?new output directory}
test ! -e "$out";mkdir "$out"
exec > "$out/session.txt" 2>&1
set -x
src=${3:-/var/tmp/graphics009-run2/source}
build=${4:-/var/tmp/graphics009-run2/build}
cp "$src/darwin-user/remaklar/darwin-kernel.c" "$out/prior-darwin-kernel.c"
for name in darwin-kernel.c bootstrap-main.c bootstrap.h;do cp "$payload/$name" "$src/darwin-user/remaklar/$name";done
rm -f "$build/ppc-darwin-user/darwin-kernel.o" "$build/ppc-darwin-user/bootstrap-main.o"
make -C "$build" SRC_PATH="$src" subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$build/ppc-darwin-user/qemu-ppc"
cp "$exe" "$out/qemu-ppc"
probe="$payload/run_graphics_008.pl"
for name in signals-runtime statfs-runtime graphics-system-runtime iokit-open-runtime;do
 extra='';if [ "$name" = iokit-open-runtime ];then extra='-framework IOKit';fi
 gcc2 -no-cpp-precomp -arch i386 "$payload/$name.c" $extra -o "$out/$name-i386" > "$out/$name-native-build.txt" 2>&1
 gcc2 -no-cpp-precomp -arch ppc "$payload/$name.c" $extra -o "$out/$name-ppc" > "$out/$name-ppc-build.txt" 2>&1
 if [ "$name" = signals-runtime ];then
 cp "$out/$name-ppc" /var/tmp/jaguar/tmp/signals-009-r10.ppc
 perl "$probe" "$out/$name-native" "$out/$name-i386" "$out/$name-i386"
 perl "$probe" "$out/$name-jaguar" "$exe" --root /var/tmp/jaguar "$out/$name-ppc" /tmp/signals-009-r10.ppc
 else
 perl "$probe" "$out/$name-native" "$out/$name-i386"
 perl "$probe" "$out/$name-jaguar" "$exe" --root /var/tmp/jaguar "$out/$name-ppc"
 fi
done
perl "$probe" "$out/windowserver" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/CoreServices/WindowServer
perl "$probe" "$out/installer" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer
perl "$probe" "$out/splash" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Installation/CDIS/splash /Applications/Utilities/Installer.app/Contents/MacOS/Installer
for name in process-runtime access-runtime exec-runtime iokit-runtime;do
 extra='';if [ "$name" = iokit-runtime ];then extra='-framework IOKit';fi
 gcc2 -no-cpp-precomp -arch ppc "$payload/$name.c" $extra -o "$out/$name-ppc" > "$out/$name-build.txt" 2>&1
 if [ "$name" = exec-runtime ];then
 cp "$out/$name-ppc" /var/tmp/jaguar/tmp/exec-009-r10.ppc
 perl "$probe" "$out/$name" "$exe" --root /var/tmp/jaguar "$out/$name-ppc" /tmp/exec-009-r10.ppc
 else
 perl "$probe" "$out/$name" "$exe" --root /var/tmp/jaguar "$out/$name-ppc"
 fi
done
gcc2 -no-cpp-precomp -arch i386 "$payload/native/objc.m" -lobjc -o "$out/objc-i386" > "$out/objc-build.txt" 2>&1
gcc2 -no-cpp-precomp -arch i386 "$payload/native/cf.c" -framework CoreFoundation -o "$out/cf-i386" > "$out/cf-build.txt" 2>&1
for name in objc cf;do perl "$probe" "$out/$name-native" "$out/$name-i386";done
perl "$payload/run_utilities.pl" "$exe" "$payload/samples" "$payload/utility-cases.tsv" "$out/utilities" > "$out/utilities.txt" 2>&1
perl "$payload/run_filesystem.pl" "$exe" "$payload/samples" "$payload/filesystem-probe.macho" "$out/filesystem" > "$out/filesystem.txt" 2>&1
ps -axww > "$out/processes.txt"
echo RUN10_COMPLETE
