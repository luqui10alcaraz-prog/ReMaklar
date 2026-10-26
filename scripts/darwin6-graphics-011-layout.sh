#!/bin/sh
set -u
p=/var/tmp/graphics011-layout
out=/var/tmp/graphics011-layout-results2
test ! -e "$out" || exit 1
mkdir "$out"
for arch in i386 ppc;do
 gcc2 -no-cpp-precomp -arch "$arch" "$p/shared-layout011.c" -o "$out/layout-$arch" > "$out/build-$arch.txt" 2>&1
 if [ -f "$out/layout-$arch" ];then
  if [ "$arch" = i386 ];then "$out/layout-i386" > "$out/layout-i386.stdout" 2>&1;else /var/tmp/graphics010-run19/qemu-ppc --root /var/tmp/jaguar "$out/layout-ppc" > "$out/layout-ppc.stdout" 2> "$out/layout-ppc.stderr";fi
 fi
done
mount -t msdos /dev/disk1 /exchange
cd /var/tmp
gnutar czf /exchange/layout12.tgz graphics011-layout-results2
sync;umount /exchange
