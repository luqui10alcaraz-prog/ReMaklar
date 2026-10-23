#!/bin/sh
set -eu
type gcc
readlink -f /usr/bin/gcc
gcc -v
gcc -m32 -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -### -c /tmp/remaklar-probe.c
gcc -dumpspecs | grep -n -E 'FORTIFY|stack-protector|harden|specs' || true
env | grep -E 'GCC|CFLAGS|CPPFLAGS|SPECS' || true
cd /mnt/h/ReMaklar/build/qemu-linux32/ppc-darwin-user
make -n V=1 op_helper.o
