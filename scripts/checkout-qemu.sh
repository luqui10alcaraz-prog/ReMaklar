#!/bin/sh
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
dest="$project/experiments/qemu-0.10.6"
if [ -e "$dest" ]; then
    echo "Already exists; not replacing $dest" >&2
    exit 1
fi
git -c core.autocrlf=false clone --depth 1 --branch v0.10.6 https://github.com/qemu/qemu.git "$dest"
git -C "$dest" config core.autocrlf false
test "$(git -C "$dest" rev-parse HEAD)" = 9eab386edbf8cf002a731f8204a156f243a47a57
checkpoint=${REMAKLAR_CHECKPOINT:-0.02-dyld}
case "$checkpoint" in
    0.01|0.02-dyld) ;;
    *) echo "Unknown checkpoint: $checkpoint" >&2; exit 1 ;;
esac
git -C "$dest" switch -c "remaklar/$checkpoint"
git -C "$dest" apply --check "$project/patches/qemu-0.10.6/0001-remaklar-0.01.patch"
git -C "$dest" apply "$project/patches/qemu-0.10.6/0001-remaklar-0.01.patch"
if [ "$checkpoint" = 0.02-dyld ]; then
    git -C "$dest" apply --check "$project/patches/qemu-0.10.6/0002-dyld-startup.patch"
    git -C "$dest" apply "$project/patches/qemu-0.10.6/0002-dyld-startup.patch"
fi
