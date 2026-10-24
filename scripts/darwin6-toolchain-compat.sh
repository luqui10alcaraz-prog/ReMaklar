#!/bin/sh
# Record compiler alternatives and low-memory mapping independently of QEMU.
# SPDX-License-Identifier: MIT
out=/var/tmp/remaklar-results
mkdir -p "$out"
cat > "$out/hello.c" <<'EOF'
#include <stdio.h>
int main(void) { puts("ReMaklar native Darwin i386 toolchain"); return 0; }
EOF
exec > "$out/compiler-compat.log" 2>&1
set -x
gcc3 -no-cpp-precomp "$out/hello.c" -o "$out/hello3"
echo gcc3_status=$?
gcc3 -O2 -no-cpp-precomp "$out/hello.c" -o "$out/hello3"
echo gcc3_O2_status=$?
gcc2 -no-cpp-precomp "$out/hello.c" -o "$out/hello2"
echo gcc2_status=$?
file "$out/hello2"
"$out/hello2"
echo hello2_status=$?
gcc2 -no-cpp-precomp -m32 "$out/hello.c" -o "$out/hello-m32"
echo gcc2_m32_status=$?
gcc2 -no-cpp-precomp -Wl,-seg1addr,0x10000000 /var/tmp/remaklar/tests/ppc/probe_low_mapping.c -o "$out/probe-low"
echo probe_build_status=$?
otool -l "$out/probe-low"
"$out/probe-low"
echo low_mapping_status=$?
