#!/bin/sh
# Bounded follow-up: setsid and original launch probes only.
# SPDX-License-Identifier: MIT
set -eu
payload=${1:?payload}
out=${2:?new output directory}
test ! -e "$out"
mkdir "$out"
exec > "$out/session.txt" 2>&1
set -x
cp -Rp /var/tmp/graphics008-run5/source "$out/source"
cp -Rp /var/tmp/graphics008-run5/build "$out/build"
cp "$payload/darwin-kernel.c" "$out/source/darwin-user/remaklar/darwin-kernel.c"
rm "$out/build/ppc-darwin-user/darwin-kernel.o"
make -C "$out/build" SRC_PATH="$out/source" subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc"
{ uname -a;file "$exe";md5 "$exe"; } > "$out/host.txt"
path=System/Library/PrivateFrameworks/DesktopServicesPriv.framework/Versions/A/DesktopServicesPriv
ls -ld "/var/tmp/jaguar/$path" > "$out/dependency-before.txt" 2>&1 || true
if [ ! -e "/var/tmp/jaguar/$path" ];then
    mkdir -p "/var/tmp/jaguar/$(dirname "$path")"
    cp -p "$payload/DesktopServicesPriv" "/var/tmp/jaguar/$path"
fi
ls -ld "/var/tmp/jaguar/$path" > "$out/dependency-after.txt" 2>&1
md5 "/var/tmp/jaguar/$path" > "$out/dependency-md5.txt"
gcc2 -no-cpp-precomp -arch ppc "$payload/process-runtime.c" -o "$out/process-ppc" > "$out/process-ppc-build.txt" 2>&1
gcc2 -no-cpp-precomp -arch i386 "$payload/process-runtime.c" -o "$out/process-native" > "$out/process-native-build.txt" 2>&1
probe="$payload/run_graphics_008.pl"
perl "$probe" "$out/process-native" "$out/process-native"
perl "$probe" "$out/process-jaguar" "$exe" --root /var/tmp/jaguar "$out/process-ppc"
perl "$probe" "$out/windowserver" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/CoreServices/WindowServer
perl "$probe" "$out/splash" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Installation/CDIS/splash /Applications/Utilities/Installer.app/Contents/MacOS/Installer
perl "$probe" "$out/installer" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer
ps -axww > "$out/processes.txt"
echo GRAPHICS_008_FOLLOWUP_COMPLETE
