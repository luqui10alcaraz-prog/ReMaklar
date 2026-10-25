#!/bin/sh
# Repeat from persistent disk, deleting the generated bitmap first.
# SPDX-License-Identifier: MIT
cd /var/tmp/remaklar || exit 1
out=/var/tmp/remaklar-runtime-006-cold
mkdir -p "$out"
exe=build/qemu-darwin6/ppc-darwin-user/qemu-ppc
root=/var/tmp/jaguar
uname -a > "$out/host.txt"
rm -f "$root/tmp/quartz.ppm"
failed=0
for name in objc-smoke-006 cf-smoke-006 mach-runtime-006 graphics-contracts-006 foundation-ppc quartz-ppc; do
    perl -e 'alarm 120;exec @ARGV' "$exe" --root "$root" build/$name /tmp/quartz.ppm > "$out/$name.stdout" 2> "$out/$name.stderr"
    status=$?
    echo "$name status=$status" >> "$out/status.txt"
    if [ "$status" != 0 ]; then failed=1; fi
done
if [ -f "$root/tmp/quartz.ppm" ]; then cp "$root/tmp/quartz.ppm" "$out/quartz.ppm";else failed=1;fi
echo failed=$failed >> "$out/status.txt"
gnutar czf /exchange/cold006.tgz -C /var/tmp remaklar-runtime-006-cold
sync
umount /exchange
echo COLD_RUNTIME_COMPLETE failed=$failed
halt
