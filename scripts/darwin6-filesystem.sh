#!/bin/sh
# Measured 0.05 build, unchanged regressions, filesystem cases, runtime probes.
# SPDX-License-Identifier: MIT
cd /var/tmp/remaklar || exit 1
out=/var/tmp/remaklar-fs-005
mkdir -p "$out"
exe=/var/tmp/remaklar/build/qemu-darwin6/ppc-darwin-user/qemu-ppc
root=/var/tmp/remaklar/research/samples-local
{ uname -a; arch; gcc2 --version; } > "$out/host.txt" 2>&1
sh scripts/configure-qemu-darwin6.sh > "$out/configure.txt" 2>&1
status=$?
if [ "$status" = 0 ]; then
    make -C build/qemu-darwin6 -j2 subdir-ppc-darwin-user > "$out/build.txt" 2>&1
    status=$?
fi
echo build_status=$status >> "$out/build.txt"
if [ "$status" = 0 ]; then
    sh scripts/darwin6-run-tests.sh
    baseline=$?
    cp /var/tmp/remaklar-results/native-tests.log "$out/baseline.txt"
    mkdir -p "$out/utilities" "$out/filesystem"
    perl tests/ppc/run_utilities.pl "$exe" "$root" build/utility-cases.tsv "$out/utilities" > "$out/utilities.txt" 2>&1
    utilities=$?
    perl tests/ppc/run_filesystem.pl "$exe" "$root" build/filesystem-probe.macho "$out/filesystem" > "$out/filesystem.txt" 2>&1
    filesystem=$?
    sh scripts/darwin6-objc-probe.sh "$out"
    { md5 "$exe" "$root/bin/ls" "$root/bin/pwd" "$root/usr/lib/libobjc.A.dylib" "$root/System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation"; } > "$out/md5.txt"
    (cd "$root" && md5 bin/ls bin/pwd bin/echo bin/cat usr/bin/true usr/bin/false usr/lib/dyld usr/lib/libSystem.B.dylib usr/lib/system/libmathCommon.A.dylib usr/lib/libobjc.A.dylib System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation) > "$out/original-md5.txt"
    md5 "$exe" > "$out/runner-md5.txt"
    cp "$exe" /exchange/run05
    if [ -f build/objc-smoke ]; then cp build/objc-smoke /exchange/objc2; fi
    echo baseline=$baseline utilities=$utilities filesystem=$filesystem > "$out/status.txt"
    cp "$out/status.txt" "$out/final-status.txt"
else
    echo build_failed=$status > "$out/status.txt"
fi
gnutar czf /exchange/fs.tgz -C /var/tmp remaklar-fs-005
sync
umount /exchange || exit 1
echo FILESYSTEM_ITERATION_COMPLETE
