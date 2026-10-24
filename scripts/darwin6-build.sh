#!/bin/sh
# One measured native iteration; FAT must be mounted at /exchange.
# SPDX-License-Identifier: MIT
cd /var/tmp/remaklar || exit 1
out=/var/tmp/remaklar-results
mkdir -p "$out"
if [ ! -f "$out/compiler-compat.log" ]; then
    sh scripts/darwin6-toolchain-compat.sh
fi
cp "$out/compiler-compat.log" /exchange/compat.log
echo 'Build not attempted: configure has not succeeded.' > "$out/build-current.log"
sh scripts/configure-qemu-darwin6.sh > "$out/configure-current.log" 2>&1
status=$?
overall_status=$status
echo configure_status=$status >> "$out/configure-current.log"
cp "$out/configure-current.log" /exchange/config.log
if [ "$status" = 0 ]; then
    make -C build/qemu-darwin6 -j2 subdir-ppc-darwin-user > "$out/build-current.log" 2>&1
    build_status=$?
    overall_status=$build_status
    echo build_status=$build_status >> "$out/build-current.log"
    if [ "$build_status" = 0 ]; then
        sh scripts/darwin6-run-tests.sh
        overall_status=$?
    fi
fi
cp "$out/build-current.log" /exchange/build.log
sync
if ! umount /exchange; then overall_status=1; fi
echo BUILD_ITERATION_COMPLETE status=$overall_status
exit "$overall_status"
