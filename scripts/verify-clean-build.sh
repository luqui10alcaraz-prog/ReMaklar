#!/bin/sh
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export REMAKLAR_BUILD_DIR="$project/build/qemu-linux32-clean"
export REMAKLAR_EXECUTOR="$REMAKLAR_BUILD_DIR/ppc-darwin-user/qemu-ppc"
if [ -e "$REMAKLAR_BUILD_DIR" ]; then
    echo 'Clean verification directory already exists; choose a new directory or review it first.' >&2
    exit 1
fi
sh "$project/scripts/build-qemu-linux32.sh"
sh "$project/scripts/test-qemu-linux32.sh"
file "$REMAKLAR_EXECUTOR"
sha256sum "$REMAKLAR_EXECUTOR"
