#!/bin/sh
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
# Build the common archive in its declaring makefile. Forcing a nested make
# without -o would otherwise recreate that archive with the generic empty rule.
make -B -C "$project/build/qemu-linux32" -j2 libqemu_user.a > "$project/logs/qemu-build-default-common.log" 2>&1
if ! make -B -C "$project/build/qemu-linux32/ppc-darwin-user" -o ../libqemu_user.a -j2 all > "$project/logs/qemu-build-default-final.log" 2>&1; then
    tail -60 "$project/logs/qemu-build-default-final.log"
    exit 1
fi
sh "$project/scripts/test-qemu-linux32.sh"
python3 "$project/tools/record_build.py"
