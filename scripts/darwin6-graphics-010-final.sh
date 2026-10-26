#!/bin/sh
set -eu
cd /var/tmp
sh /var/tmp/graphics010-final/regression.sh
gcc2 -no-cpp-precomp -arch i386 /var/tmp/graphics010-final/cursor010-native.c -framework IOKit -o /var/tmp/graphics010-regression19/cursor-native > /var/tmp/graphics010-regression19/cursor-build.txt 2>&1
perl /var/tmp/graphics009-r8/run_graphics_008.pl /var/tmp/graphics010-regression19/cursor-native /var/tmp/graphics010-regression19/cursor-native
perl /var/tmp/graphics010-final/joint.pl /var/tmp/graphics010-joint19 /var/tmp/graphics010-run19/qemu-ppc /var/tmp/jaguar
mount -t msdos /dev/disk1 /exchange
cd /var/tmp
gnutar czf /exchange/final119.tgz graphics010-regression19 graphics010-joint19
sync
umount /exchange
