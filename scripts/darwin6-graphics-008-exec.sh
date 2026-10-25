#!/bin/sh
# Second measured iteration, incremental over the successful fork build.
# SPDX-License-Identifier: MIT
set -eu
payload=${1:?payload}
out=${2:?new output directory}
mode=${3:-build}
if [ "$mode" = --resume ]; then
test -x "$out/build/ppc-darwin-user/qemu-ppc"
exec > "$out/session-resume.txt" 2>&1
set -x
else
test ! -e "$out"
mkdir "$out"
exec > "$out/session.txt" 2>&1
set -x
cp -Rp /var/tmp/graphics008-run1/source "$out/source"
cp -Rp /var/tmp/graphics008-run1/build "$out/build"
for name in darwin-kernel.c bootstrap-main.c bootstrap.h; do
    cp "$payload/$name" "$out/source/darwin-user/remaklar/$name"
done
rm "$out/build/ppc-darwin-user/darwin-kernel.o" "$out/build/ppc-darwin-user/bootstrap-main.o"
make -C "$out/build" SRC_PATH="$out/source" subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc"
{ uname -a; file "$exe"; md5 "$exe"; } > "$out/host.txt"
fi
exe="$out/build/ppc-darwin-user/qemu-ppc"
# Add missing original CD paths; never replace an existing extracted component.
test ! -e /var/tmp/jaguar/Applications/Utilities/Installer.app
gnutar xzf "$payload/installer-originals.tgz" -C /var/tmp/jaguar Applications/Utilities/Installer.app System/Installation/CDIS
if [ ! -L /var/tmp/jaguar/System/Library/CoreServices/WindowServer ]; then
    gnutar xzf "$payload/installer-originals.tgz" -C /var/tmp/jaguar System/Library/CoreServices/WindowServer
fi
ls -l /var/tmp/jaguar/System/Library/CoreServices/WindowServer > "$out/windowserver-link.txt"
mkdir -p /var/tmp/remaklar/research/samples-local/tmp
gcc2 -no-cpp-precomp -arch ppc "$payload/exec-runtime.c" -o "$out/exec-ppc" > "$out/exec-build.txt" 2>&1
gcc2 -no-cpp-precomp -arch i386 "$payload/exec-runtime.c" -o "$out/exec-i386" > "$out/exec-native-build.txt" 2>&1
cp "$out/exec-ppc" /var/tmp/remaklar/research/samples-local/tmp/exec-008.ppc
cp "$out/exec-ppc" /var/tmp/jaguar/tmp/exec-008.ppc
perl "$payload/run_graphics_008.pl" "$out/exec-native" "$out/exec-i386" "$out/exec-i386"
perl "$payload/run_graphics_008.pl" "$out/exec-darwin" "$exe" --root /var/tmp/remaklar/research/samples-local "$out/exec-ppc" /tmp/exec-008.ppc
perl "$payload/run_graphics_008.pl" "$out/exec-jaguar" "$exe" --root /var/tmp/jaguar "$out/exec-ppc" /tmp/exec-008.ppc
perl "$payload/run_graphics_008.pl" "$out/windowserver" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/CoreServices/WindowServer
perl "$payload/run_graphics_008.pl" "$out/splash" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Installation/CDIS/splash /Applications/Utilities/Installer.app/Contents/MacOS/Installer
perl "$payload/run_graphics_008.pl" "$out/installer" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer
set +e
ioreg -l > "$out/ioreg.txt" 2>&1
echo $? > "$out/ioreg.status"
ls -l /dev/mem /dev/kmem /dev/fb* > "$out/graphics-devices.txt" 2>&1
echo GRAPHICS_008_EXEC_COMPLETE
