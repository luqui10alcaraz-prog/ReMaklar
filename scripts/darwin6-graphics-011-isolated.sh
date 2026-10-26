#!/bin/sh
set -eu
p=/var/tmp/graphics011-isolated
out=/var/tmp/graphics011-isolated-results5
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
for name in typed-live-test typed-framebuffer-native;do
 extra='';if [ "$name" = typed-framebuffer-native ];then extra='-framework IOKit';fi
 gcc2 -no-cpp-precomp -arch i386 -O2 "$p/typed-live.c" "$p/$name.c" $extra -o "$out/$name" > "$out/$name-build.txt" 2>&1
 perl /var/tmp/graphics009-r8/run_graphics_008.pl "$out/$name" "$out/$name"
done
mount -t msdos /dev/disk1 /exchange
cd /var/tmp
gnutar czf /exchange/isol015.tgz graphics011-isolated-results5
sync;umount /exchange
