#!/bin/sh
# Record an unadapted native build before changing the runtime.
# SPDX-License-Identifier: MIT
cd /var/tmp/remaklar || exit 1
out=/var/tmp/remaklar-results
mkdir -p "$out"
sh scripts/darwin6-probe.sh
cp "$out/toolchain.log" /exchange/tool.log
sh scripts/configure-qemu-darwin6.sh > "$out/configure-baseline.log" 2>&1
configure_status=$?
echo configure_status=$configure_status >> "$out/configure-baseline.log"
cp "$out/configure-baseline.log" /exchange/config.log
if [ "$configure_status" = 0 ]; then
    make -C build/qemu-darwin6 -j2 subdir-ppc-darwin-user > "$out/build-baseline.log" 2>&1
    echo build_status=$? >> "$out/build-baseline.log"
    cp "$out/build-baseline.log" /exchange/build.log
fi
sync
umount /exchange
echo BASELINE_COMPLETE
