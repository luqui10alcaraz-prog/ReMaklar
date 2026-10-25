#!/bin/sh
# Reuse the native build; test new ABI bridges and all required regressions.
# SPDX-License-Identifier: MIT
set -eu
payload=${1:?payload};out=${2:?new output}
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
cp -Rp /var/tmp/graphics009-run1/source "$out/source"
cp -Rp /var/tmp/graphics009-run1/build "$out/build"
for name in darwin-kernel.c bootstrap-main.c bootstrap.h;do cp "$payload/$name" "$out/source/darwin-user/remaklar/$name";done
rm "$out/build/ppc-darwin-user/darwin-kernel.o" "$out/build/ppc-darwin-user/bootstrap-main.o"
make -C "$out/build" SRC_PATH="$out/source" subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc";probe="$payload/run_graphics_008.pl"
{ uname -a;file "$exe";md5 "$exe"; } > "$out/host.txt"
for name in signals-runtime statfs-runtime iokit-open-runtime getattrlist-runtime;do
 extra='';if [ "$name" = iokit-open-runtime ];then extra='-framework IOKit';fi
 gcc2 -no-cpp-precomp -arch i386 "$payload/$name.c" $extra -o "$out/$name-i386" > "$out/$name-native-build.txt" 2>&1
 gcc2 -no-cpp-precomp -arch ppc "$payload/$name.c" $extra -o "$out/$name-ppc" > "$out/$name-ppc-build.txt" 2>&1
 if [ "$name" = signals-runtime ];then
   test ! -e /var/tmp/jaguar/tmp/signals-009.ppc
   cp "$out/$name-ppc" /var/tmp/jaguar/tmp/signals-009.ppc
   perl "$probe" "$out/$name-native" "$out/$name-i386" "$out/$name-i386"
   perl "$probe" "$out/$name-jaguar" "$exe" --root /var/tmp/jaguar "$out/$name-ppc" /tmp/signals-009.ppc
 else
   perl "$probe" "$out/$name-native" "$out/$name-i386"
   perl "$probe" "$out/$name-jaguar" "$exe" --root /var/tmp/jaguar "$out/$name-ppc"
 fi
done
perl "$probe" "$out/windowserver" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/CoreServices/WindowServer
perl "$probe" "$out/installer" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer
perl "$probe" "$out/splash" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Installation/CDIS/splash /Applications/Utilities/Installer.app/Contents/MacOS/Installer
perl "$probe" "$out/process-regression" "$exe" --root /var/tmp/jaguar /var/tmp/graphics008-run6/process-ppc
perl "$probe" "$out/access-regression" "$exe" --root /var/tmp/jaguar /var/tmp/graphics008-run7/access-ppc
perl "$probe" "$out/exec-regression" "$exe" --root /var/tmp/jaguar /var/tmp/graphics008-run5/exec-runtime-ppc /tmp/exec-008-final.ppc
perl "$probe" "$out/iokit-regression" "$exe" --root /var/tmp/jaguar /var/tmp/graphics008-run5/iokit-runtime-ppc
perl "$probe" "$out/quartz-regression" "$exe" --root /var/tmp/jaguar /var/tmp/remaklar/build/quartz-ppc /tmp/quartz-009-regression.ppm
if [ -f /var/tmp/jaguar/tmp/quartz-009-regression.ppm ];then cp /var/tmp/jaguar/tmp/quartz-009-regression.ppm "$out/quartz.ppm";fi
mkdir "$out/utilities" "$out/filesystem";set +e
old=/var/tmp/remaklar/research/samples-local
perl /var/tmp/remaklar/tests/ppc/run_utilities.pl "$exe" "$old" /var/tmp/remaklar/build/utility-cases.tsv "$out/utilities" > "$out/utilities.txt" 2>&1
echo $? > "$out/utilities.status"
perl /var/tmp/remaklar/tests/ppc/run_filesystem.pl "$exe" "$old" /var/tmp/remaklar/build/filesystem-probe.macho "$out/filesystem" > "$out/filesystem.txt" 2>&1
echo $? > "$out/filesystem.status"
for name in objc cf;do perl "$probe" "$out/native007-$name" "/var/tmp/native007-run3/$name";done
ioreg -l > "$out/ioreg.txt" 2>&1
ps -axww > "$out/processes.txt"
echo GRAPHICS009_INTEGRATED_COMPLETE
