#!/bin/sh
# Rebuild the final patch on the preserved 0.09 native environment.
# SPDX-License-Identifier: MIT
set -eu
payload=/var/tmp/graphics010-reproduce
out=${REMAKLAR010_OUT:-/var/tmp/graphics010-reproduced}
root=/var/tmp/jaguar
test ! -e "$out"
mkdir "$out"
exec > "$out/session.txt" 2>&1
set -x
cp -Rp /var/tmp/graphics009-run2/source "$out/source"
cp -Rp /var/tmp/graphics009-run2/build "$out/build"
for name in darwin-kernel.c bootstrap-main.c bootstrap.h mach-native.inc;do
 cp "$payload/$name" "$out/source/darwin-user/remaklar/$name"
done
rm -f "$out/build/ppc-darwin-user/darwin-kernel.o"
make -C "$out/build" SRC_PATH="$out/source" subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc"
cp "$exe" "$out/qemu-ppc"
md5 "$exe" > "$out/runtime.txt"
for name in mach010-runtime shm010-runtime credentials010-runtime mmap010-runtime iokit-cstring-runtime iokit010-open-runtime clock010-runtime framebuffer010-runtime;do
 extra=''
 case "$name" in iokit*|framebuffer*) extra='-framework IOKit';; esac
 for arch in i386 ppc;do
  gcc2 -no-cpp-precomp -arch "$arch" "$payload/$name.c" $extra -o "$out/$name-$arch" > "$out/$name-$arch-build.txt" 2>&1
 done
 case "$name" in
 mach010-runtime|shm010-runtime)
  self=/tmp/$name-010-reproduce.ppc
  cp "$out/$name-ppc" "$root$self"
  perl "$payload/probe.pl" "$out/$name-native" "$out/$name-i386" "$out/$name-i386"
  perl "$payload/probe.pl" "$out/$name-ppc" "$exe" --root "$root" "$out/$name-ppc" "$self"
  ;;
 *)
  perl "$payload/probe.pl" "$out/$name-native" "$out/$name-i386"
  perl "$payload/probe.pl" "$out/$name-ppc" "$exe" --root "$root" "$out/$name-ppc"
  ;;
 esac
done
perl "$payload/joint.pl" "$out/joint" "$exe" "$root"
echo REPRODUCE010_COMPLETE
