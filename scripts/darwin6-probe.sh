#!/bin/sh
# Native Darwin 6 toolchain and memory probes. SPDX-License-Identifier: MIT
out=/var/tmp/remaklar-results
mkdir -p "$out"
exec > "$out/toolchain.log" 2>&1
set -x
uname -a
arch
mount
df -h
id
ls -l /usr/bin/gcc* /usr/bin/cc /usr/bin/make /usr/bin/gnumake
gcc -v
gcc3 -v
make --version
as -v </dev/null
ld -v
ls -l /usr/include/stdint.h /usr/include/inttypes.h /usr/include/sys/ucontext.h
cat > "$out/hello.c" <<'EOF'
#include <stdio.h>
int main(void) { puts("ReMaklar native Darwin i386 toolchain"); return 0; }
EOF
cc "$out/hello.c" -o "$out/hello"
file "$out/hello"
"$out/hello"
echo hello_status=$?
cc -Wl,-seg1addr,0x10000000 /var/tmp/remaklar/tests/ppc/probe_low_mapping.c -o "$out/probe-low"
otool -l "$out/probe-low"
"$out/probe-low"
echo low_mapping_status=$?
ls /dev/tty* /dev/cu*
ifconfig -a
echo PROBE_COMPLETE
