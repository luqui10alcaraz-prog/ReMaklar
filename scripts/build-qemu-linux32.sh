#!/bin/sh
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
mkdir -p "$project/logs"
build_dir=${REMAKLAR_BUILD_DIR:-$project/build/qemu-linux32}
sh "$project/scripts/configure-qemu-linux32.sh" > "$project/logs/qemu-configure-current.log" 2>&1
if make -C "$build_dir" -j2 subdir-ppc-darwin-user > "$project/logs/qemu-build-current.log" 2>&1; then
    tail -8 "$project/logs/qemu-build-current.log"
else
    tail -60 "$project/logs/qemu-build-current.log"
    exit 1
fi
