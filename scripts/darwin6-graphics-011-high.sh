#!/bin/sh
set -eu
p=/var/tmp/graphics011-high15
out=/var/tmp/graphics011-high15-results
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
gcc2 -no-cpp-precomp -arch i386 -O2 "$p/high-window.c" "$p/high-window-test.c" -o "$out/high-window-native" > "$out/build.txt" 2>&1
perl /var/tmp/graphics009-r8/run_graphics_008.pl "$out/native" "$out/high-window-native"
mount -t msdos /dev/disk1 /exchange
cd /var/tmp
gnutar czf /exchange/high15.tgz graphics011-high15-results/*.txt graphics011-high15-results/*.status graphics011-high15-results/*.stdout graphics011-high15-results/*.stderr graphics011-validation13/*.txt
sync;umount /exchange
