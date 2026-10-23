#!/bin/sh
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if ! make -C "$project/build/qemu-linux32" -j2 subdir-ppc-darwin-user > "$project/logs/qemu-build-dynamic.log" 2>&1; then
    tail -60 "$project/logs/qemu-build-dynamic.log"
    exit 1
fi
python3 "$project/tests/ppc/run_dynamic.py"
