#!/bin/sh
# Collect one minimal TCG execution with the host's native fault registers.
# SPDX-License-Identifier: MIT
out=/var/tmp/remaklar-results
exe=/var/tmp/remaklar/build/qemu-darwin6/ppc-darwin-user/qemu-ppc
cd "$out" || exit 1
case ${1:-exit42} in
    true|false)
        root=/var/tmp/remaklar/research/samples-local
        REMAKLAR_TRACE=1 "$exe" --root "$root" "$root/usr/bin/$1" > trace.stdout 2> trace.stderr ;;
    exit42)
        REMAKLAR_TRACE=1 "$exe" /var/tmp/remaklar/build/fixtures/exit42.macho > trace.stdout 2> trace.stderr ;;
    *) exit 2 ;;
esac
echo exit=$? > trace.status
cp remaklar-tcg.log /exchange/trace.log
cp trace.stderr /exchange/trace.err
cp trace.status /exchange/status.txt
cp "$exe" /exchange/runner
sync
umount /exchange
echo TRACE_COMPLETE
