#!/bin/sh
set -u
cd /mnt/h/ReMaklar
file experiments/qemu-0.10.6/configure
head -12 experiments/qemu-0.10.6/configure | cat -v
printf 'int main(void){return 0;}\n' > /tmp/remaklar-probe.c
gcc -m32 /tmp/remaklar-probe.c -o /tmp/remaklar-probe
id
sudo -n true
command -v clang-18 llvm-mc llvm-mc-18 || true
