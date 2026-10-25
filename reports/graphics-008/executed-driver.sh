#!/bin/sh
# Reproduce the final bounded 0.08 probes, reusing the native 0.06 build.
# SPDX-License-Identifier: MIT
set -eu
payload=${1:?payload directory}
out=${2:?new output directory}
test ! -e "$out"
mkdir "$out"
exec > "$out/session.txt" 2>&1
set -x
cp -Rp /var/tmp/remaklar/experiments/qemu-0.10.6 "$out/source"
cp -Rp /var/tmp/remaklar/build/qemu-darwin6 "$out/build"
for name in darwin-kernel.c bootstrap-main.c bootstrap.h; do cp "$payload/$name" "$out/source/darwin-user/remaklar/$name";done
rm "$out/build/ppc-darwin-user/darwin-kernel.o" "$out/build/ppc-darwin-user/bootstrap-main.o"
make -C "$out/build" SRC_PATH="$out/source" subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc"
{ uname -a;file "$exe";md5 "$exe"; } > "$out/host.txt"
if [ ! -e /var/tmp/jaguar/Applications/Utilities/Installer.app ];then
    gnutar xzf "$payload/installer-originals.tgz" -C /var/tmp/jaguar Applications/Utilities/Installer.app
fi
if [ ! -e /var/tmp/jaguar/System/Installation/CDIS/splash ];then
    gnutar xzf "$payload/installer-originals.tgz" -C /var/tmp/jaguar System/Installation/CDIS
fi
if [ ! -L /var/tmp/jaguar/System/Library/CoreServices/WindowServer ];then
    gnutar xzf "$payload/installer-originals.tgz" -C /var/tmp/jaguar System/Library/CoreServices/WindowServer
fi
: > "$out/libraries-added.txt"
while IFS= read -r path;do
    if [ ! -e "/var/tmp/jaguar/$path" ];then echo "$path" >> "$out/libraries-added.txt";fi
done < "$payload/library-paths.txt"
if [ -s "$out/libraries-added.txt" ];then
    gnutar xzf "$payload/libraries.tgz" -C /var/tmp/jaguar -T "$out/libraries-added.txt"
fi
while IFS= read -r path;do md5 "/var/tmp/jaguar/$path";done < "$payload/library-paths.txt" > "$out/originals-md5.txt"
old=/var/tmp/remaklar/research/samples-local
if [ ! -e "$old/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit" ];then
    mkdir -p "$old/System/Library/Frameworks/IOKit.framework/Versions/A"
    cp -p /System/Library/Frameworks/IOKit.framework/Versions/A/IOKit "$old/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit"
fi
for name in exec-runtime iokit-runtime;do
    extra='';if [ "$name" = iokit-runtime ];then extra='-framework IOKit';fi
    gcc2 -no-cpp-precomp -arch ppc "$payload/$name.c" $extra -o "$out/$name-ppc" > "$out/$name-ppc-build.txt" 2>&1
    gcc2 -no-cpp-precomp -arch i386 "$payload/$name.c" $extra -o "$out/$name-i386" > "$out/$name-native-build.txt" 2>&1
done
cp "$out/exec-runtime-ppc" "$old/tmp/exec-008-final.ppc"
cp "$out/exec-runtime-ppc" /var/tmp/jaguar/tmp/exec-008-final.ppc
probe="$payload/run_graphics_008.pl"
perl "$probe" "$out/exec-native" "$out/exec-runtime-i386" "$out/exec-runtime-i386"
perl "$probe" "$out/exec-darwin" "$exe" --root "$old" "$out/exec-runtime-ppc" /tmp/exec-008-final.ppc
perl "$probe" "$out/exec-jaguar" "$exe" --root /var/tmp/jaguar "$out/exec-runtime-ppc" /tmp/exec-008-final.ppc
perl "$probe" "$out/iokit-native" "$out/iokit-runtime-i386"
perl "$probe" "$out/iokit-darwin" "$exe" --root "$old" "$out/iokit-runtime-ppc"
perl "$probe" "$out/iokit-jaguar" "$exe" --root /var/tmp/jaguar "$out/iokit-runtime-ppc"
perl "$probe" "$out/process-regression" "$exe" --root /var/tmp/jaguar /var/tmp/graphics008-run1/process-ppc
perl "$probe" "$out/windowserver" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/CoreServices/WindowServer
perl "$probe" "$out/splash" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Installation/CDIS/splash /Applications/Utilities/Installer.app/Contents/MacOS/Installer
perl "$probe" "$out/installer" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer
perl "$probe" "$out/quartz-regression" "$exe" --root /var/tmp/jaguar /var/tmp/remaklar/build/quartz-ppc /tmp/quartz-008-regression.ppm
if [ -f /var/tmp/jaguar/tmp/quartz-008-regression.ppm ];then cp /var/tmp/jaguar/tmp/quartz-008-regression.ppm "$out/quartz.ppm";fi
mkdir "$out/utilities" "$out/filesystem"
set +e
perl /var/tmp/remaklar/tests/ppc/run_utilities.pl "$exe" "$old" /var/tmp/remaklar/build/utility-cases.tsv "$out/utilities" > "$out/utilities.txt" 2>&1
echo $? > "$out/utilities.status"
perl /var/tmp/remaklar/tests/ppc/run_filesystem.pl "$exe" "$old" /var/tmp/remaklar/build/filesystem-probe.macho "$out/filesystem" > "$out/filesystem.txt" 2>&1
echo $? > "$out/filesystem.status"
for name in objc cf;do
    perl "$probe" "$out/native007-$name" "/var/tmp/native007-run3/$name"
done
ioreg -l > "$out/ioreg.txt" 2>&1
ps -axww > "$out/processes.txt"
echo GRAPHICS_008_FINAL_COMPLETE
