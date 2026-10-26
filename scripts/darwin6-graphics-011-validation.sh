#!/bin/sh
set -eu
out=/var/tmp/graphics011-validation14
p=/var/tmp/graphics011-validation-payload14
exe=/var/tmp/graphics011-run11/qemu-ppc
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
gcc2 -no-cpp-precomp -arch i386 -O2 "$p/high-window.c" "$p/high-window-test.c" -o "$out/high-window-native" > "$out/high-window-build.txt" 2>&1
perl /var/tmp/graphics009-r8/run_graphics_008.pl "$out/high-window-native" "$out/high-window-native"
sed -e 's/graphics010-regression19/graphics011-regression11/g' -e 's@graphics010-run19/qemu-ppc@graphics011-run11/qemu-ppc@' /var/tmp/graphics010-final/regression.sh > "$out/regression.sh"
sh "$out/regression.sh"
perl /var/tmp/graphics010-final/joint.pl /var/tmp/graphics011-joint11 "$exe" /var/tmp/jaguar
mount -t msdos /dev/disk1 /exchange
cd /var/tmp
gnutar czf /exchange/valid14.tgz graphics011-validation14/*.txt graphics011-validation14/*.stdout graphics011-validation14/*.stderr graphics011-validation14/*.status graphics011-regression10/*.txt graphics011-regression10/*.stdout graphics011-regression10/*.stderr graphics011-regression10/*.status graphics011-regression11/*.txt graphics011-regression11/*.stdout graphics011-regression11/*.stderr graphics011-regression11/*.status graphics011-joint11/*.txt graphics011-joint11/*.stdout graphics011-joint11/*.stderr graphics011-joint11/*.status
sync;umount /exchange
