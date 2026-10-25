#!/bin/sh
# 0.06 runtime regressions and authentic Jaguar graphics probes.
# SPDX-License-Identifier: MIT
cd /var/tmp/remaklar || exit 1
out=/var/tmp/remaklar-runtime-006
mkdir -p "$out"
exe=/var/tmp/remaklar/build/qemu-darwin6/ppc-darwin-user/qemu-ppc
old=/var/tmp/remaklar/research/samples-local
jaguar=/var/tmp/jaguar
{ uname -a;arch;df -k /; } > "$out/host.txt"
sh scripts/configure-qemu-darwin6.sh > "$out/configure.txt" 2>&1
status=$?
if [ "$status" = 0 ]; then
    make -C build/qemu-darwin6 -j2 subdir-ppc-darwin-user > "$out/build.txt" 2>&1
    status=$?
fi
echo build_status=$status >> "$out/build.txt"
if [ "$status" = 0 ]; then
    gcc2 -no-cpp-precomp tests/ppc/ptrace-host.c -o build/ptrace-host > "$out/oracle-build.txt" 2>&1
    build/ptrace-host > "$out/ptrace-oracle.txt" 2>&1
    echo oracle_status=$? >> "$out/ptrace-oracle.txt"
    gcc2 -no-cpp-precomp tests/ppc/mach-runtime.c -o build/mach-native > "$out/mach-native-build.txt" 2>&1
    build/mach-native > "$out/mach-native.txt" 2>&1
    echo status=$? >> "$out/mach-native.txt"
    gcc2 -no-cpp-precomp tests/ppc/graphics-contracts.c -o build/graphics-native > "$out/graphics-native-build.txt" 2>&1
    perl -e 'alarm 30;exec @ARGV' build/graphics-native > "$out/graphics-native.txt" 2>&1
    echo status=$? >> "$out/graphics-native.txt"
    for name in objc-smoke cf-smoke mach-runtime ptrace-host graphics-contracts; do
        extra=''
        if [ "$name" = objc-smoke ]; then source=tests/ppc/objc-smoke.m;extra=-lobjc; else source=tests/ppc/$name.c; fi
        if [ "$name" = cf-smoke ]; then extra='-framework CoreFoundation'; fi
        gcc2 -no-cpp-precomp -arch ppc "$source" -o build/$name-006 $extra > "$out/$name-build.txt" 2>&1
        echo compiler_status=$? >> "$out/$name-build.txt"
        for cohort in darwin jaguar; do
            root=$old
            if [ "$cohort" = jaguar ]; then root=$jaguar; fi
            perl -e 'alarm 90;exec @ARGV' "$exe" --root "$root" build/$name-006 > "$out/$name-$cohort.stdout" 2> "$out/$name-$cohort.stderr"
            echo status=$? > "$out/$name-$cohort.status"
        done
        cp build/$name-006 /exchange/$name
    done
    perl scripts/build-jaguar-probes.pl "$jaguar" "$out"
    for name in quartz foundation; do
        if [ -f build/$name-ppc ]; then
            if [ "$name" = quartz ]; then rm -f "$jaguar/tmp/quartz.ppm"; fi
            perl -e 'alarm 120;exec @ARGV' "$exe" --root "$jaguar" build/$name-ppc /tmp/quartz.ppm > "$out/$name.stdout" 2> "$out/$name.stderr"
            echo status=$? > "$out/$name.status"
            cp build/$name-ppc /exchange/$name
        fi
    done
    perl -e 'alarm 90;exec @ARGV' "$exe" --root "$jaguar" "$jaguar/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/CoreGraphics.framework/Versions/A/Resources/Window Manager" > "$out/windowserver.stdout" 2> "$out/windowserver.stderr"
    echo status=$? > "$out/windowserver.status"
    if [ -f "$jaguar/tmp/quartz.ppm" ]; then cp "$jaguar/tmp/quartz.ppm" "$out/quartz.ppm";fi
    sh scripts/darwin6-run-tests.sh
    echo baseline_status=$? > "$out/regression-status.txt"
    cp /var/tmp/remaklar-results/native-tests.log "$out/baseline.txt"
    mkdir -p "$out/utilities" "$out/filesystem"
    perl tests/ppc/run_utilities.pl "$exe" "$old" build/utility-cases.tsv "$out/utilities" > "$out/utilities.txt" 2>&1
    echo utilities_status=$? >> "$out/regression-status.txt"
    perl tests/ppc/run_filesystem.pl "$exe" "$old" build/filesystem-probe.macho "$out/filesystem" > "$out/filesystem.txt" 2>&1
    echo filesystem_status=$? >> "$out/regression-status.txt"
    cp "$exe" /exchange/run06
fi
gnutar czf /exchange/run006.tgz -C /var/tmp remaklar-runtime-006
sync
umount /exchange
echo RUNTIME_ITERATION_COMPLETE
