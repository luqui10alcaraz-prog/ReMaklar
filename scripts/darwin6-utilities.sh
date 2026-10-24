#!/bin/sh
# Additional original-program tests; preserve the 0.03 native checks.
# SPDX-License-Identifier: MIT
cd /var/tmp/remaklar || exit 1
out=/var/tmp/remaklar-utilities
mkdir -p "$out"
exe=/var/tmp/remaklar/build/qemu-darwin6/ppc-darwin-user/qemu-ppc
root=/var/tmp/remaklar/research/samples-local
{ uname -a; arch; file "$exe"; } > "$out/host.txt"
sh scripts/darwin6-run-tests.sh
baseline=$?
perl tests/ppc/run_utilities.pl "$exe" "$root" build/utility-cases.tsv "$out" > "$out/console.txt" 2>&1
status=$?
md5 "$root/bin/echo" "$root/bin/cat" > "$out/md5.txt"
echo baseline_status=$baseline >> "$out/console.txt"
echo utilities_status=$status >> "$out/console.txt"
gnutar czf /exchange/utils.tgz -C /var/tmp remaklar-utilities
sync
umount /exchange || exit 1
echo UTILITIES_COMPLETE baseline=$baseline utilities=$status
test "$baseline" = 0 && test "$status" = 0
