#!/bin/sh
# Preparation probe, not a passing regression until the runtime is supported.
# SPDX-License-Identifier: MIT
cd /var/tmp/remaklar || exit 1
out=${1:-/var/tmp/remaklar-fs-005}
mkdir -p "$out"
gcc2 -no-cpp-precomp -arch ppc -o build/objc-smoke tests/ppc/objc-smoke.m -lobjc > "$out/objc-compiler.txt" 2>&1
compiler_status=$?
echo compiler_status=$compiler_status >> "$out/objc-compiler.txt"
if [ "$compiler_status" != 0 ]; then exit "$compiler_status"; fi
file build/objc-smoke > "$out/objc-image.txt"
otool -L build/objc-smoke >> "$out/objc-image.txt"
perl -e 'alarm 90; exec @ARGV' build/qemu-darwin6/ppc-darwin-user/qemu-ppc --root /var/tmp/remaklar/research/samples-local build/objc-smoke > "$out/objc-real.stdout" 2> "$out/objc-real.stderr"
status=$?
echo runtime_probe_status=$status > "$out/objc-real-status.txt"
md5 build/objc-smoke >> "$out/objc-image.txt"
exit "$status"
