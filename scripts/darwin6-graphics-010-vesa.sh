#!/bin/sh
set -eu
out=/var/tmp/graphics010-vesa17
exe=/var/tmp/graphics010-run17/qemu-ppc
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
uname -a > "$out/kernel.txt"
sysctl hw > "$out/hardware.txt"
ps -axww > "$out/before-processes.txt"
gcc2 -no-cpp-precomp -arch i386 /var/tmp/graphics010-vesa/hid010-native.c -framework IOKit -o "$out/hid-native" > "$out/hid-build.txt" 2>&1
perl "$probe" "$out/hid-native" "$out/hid-native"
perl "$probe" "$out/framebuffer-native" /var/tmp/graphics010-run17/framebuffer010-runtime-i386
perl "$probe" "$out/framebuffer-ppc" "$exe" --root /var/tmp/jaguar /var/tmp/graphics010-run17/framebuffer010-runtime-ppc
perl /var/tmp/graphics010-final/joint.pl /var/tmp/graphics010-joint-vesa17 "$exe" /var/tmp/jaguar
mount -t msdos /dev/disk1 /exchange
cd /var/tmp
gnutar czf /exchange/vesa17.tgz graphics010-vesa17 graphics010-joint-vesa17
sync
umount /exchange
