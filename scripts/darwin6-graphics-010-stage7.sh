#!/bin/sh
set -eu
payload=/var/tmp/graphics010-stage7
out=/var/tmp/graphics010-run7
src=/var/tmp/graphics010-run1/source
build=/var/tmp/graphics010-run1/build
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
for name in darwin-kernel.c mach-native.inc;do cp "$src/darwin-user/remaklar/$name" "$out/prior-$name";cp "$payload/$name" "$src/darwin-user/remaklar/$name";done
rm -f "$build/ppc-darwin-user/darwin-kernel.o"
make -C "$build" SRC_PATH="$src" subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$build/ppc-darwin-user/qemu-ppc";cp "$exe" "$out/qemu-ppc"
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
for name in mach010-runtime shm010-runtime credentials010-runtime framebuffer010-runtime;do
 extra='';if [ "$name" = iokit-cstring-runtime ] || [ "$name" = iokit010-open-runtime ] || [ "$name" = framebuffer010-runtime ];then extra='-framework IOKit';fi
 for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$payload/$name.c" $extra -o "$out/$name-$arch" > "$out/$name-$arch-build.txt" 2>&1;done
 if [ "$name" = mach010-runtime ] || [ "$name" = shm010-runtime ];then
 cp "$out/$name-ppc" /var/tmp/jaguar/tmp/$name-r7.ppc
 perl "$probe" "$out/$name-native" "$out/$name-i386" "$out/$name-i386"
 perl "$probe" "$out/$name-jaguar" "$exe" --root /var/tmp/jaguar "$out/$name-ppc" /tmp/$name-r7.ppc
 else
 perl "$probe" "$out/$name-native" "$out/$name-i386"
 perl "$probe" "$out/$name-jaguar" "$exe" --root /var/tmp/jaguar "$out/$name-ppc"
 fi
done
test -e /var/tmp/jaguar/System/Library/CoreServices/pbs || cp "$payload/pbs" /var/tmp/jaguar/System/Library/CoreServices/pbs
perl "$probe" "$out/ats" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/ATS.framework/Versions/A/Support/StartATSServer
perl "$probe" "$out/pbs" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/CoreServices/pbs
perl "$probe" "$out/installer" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer
perl "$probe" "$out/windowserver" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Library/CoreServices/WindowServer
perl "$probe" "$out/splash" "$exe" --root /var/tmp/jaguar /var/tmp/jaguar/System/Installation/CDIS/splash /Applications/Utilities/Installer.app/Contents/MacOS/Installer
ps -axww > "$out/processes.txt"
echo GRAPHICS010_STAGE7_COMPLETE
