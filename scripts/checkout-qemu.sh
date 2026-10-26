#!/bin/sh
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
dest=${REMAKLAR_QEMU_DIR:-$project/experiments/qemu-0.10.6}
if [ -e "$dest" ]; then
    echo "Already exists; not replacing $dest" >&2
    exit 1
fi
git -c core.autocrlf=false clone --depth 1 --branch v0.10.6 https://github.com/qemu/qemu.git "$dest"
git -C "$dest" config core.autocrlf false
test "$(git -C "$dest" rev-parse HEAD)" = 9eab386edbf8cf002a731f8204a156f243a47a57
checkpoint=${REMAKLAR_CHECKPOINT:-0.05-filesystem}
case "$checkpoint" in
    0.01|0.02-dyld|0.03-darwin6|0.05-filesystem|0.06-runtime|0.08-graphics|0.09-graphics|0.10-graphics) ;;
    *) echo "Unknown checkpoint: $checkpoint" >&2; exit 1 ;;
esac
git -C "$dest" switch -c "remaklar/$checkpoint"
git -C "$dest" apply --check "$project/patches/qemu-0.10.6/0001-remaklar-0.01.patch"
git -C "$dest" apply "$project/patches/qemu-0.10.6/0001-remaklar-0.01.patch"
if [ "$checkpoint" != 0.01 ]; then
    git -C "$dest" apply --check "$project/patches/qemu-0.10.6/0002-dyld-startup.patch"
    git -C "$dest" apply "$project/patches/qemu-0.10.6/0002-dyld-startup.patch"
fi
if [ "$checkpoint" = 0.03-darwin6 ] || [ "$checkpoint" = 0.05-filesystem ] || [ "$checkpoint" = 0.06-runtime ] || [ "$checkpoint" = 0.08-graphics ] || [ "$checkpoint" = 0.09-graphics ] || [ "$checkpoint" = 0.10-graphics ]; then
    git -C "$dest" apply --check "$project/patches/qemu-0.10.6/0003-darwin6-i386.patch"
    git -C "$dest" apply "$project/patches/qemu-0.10.6/0003-darwin6-i386.patch"
fi
if [ "$checkpoint" = 0.05-filesystem ] || [ "$checkpoint" = 0.06-runtime ] || [ "$checkpoint" = 0.08-graphics ] || [ "$checkpoint" = 0.09-graphics ] || [ "$checkpoint" = 0.10-graphics ]; then
    git -C "$dest" apply --check "$project/patches/qemu-0.10.6/0004-filesystem.patch"
    git -C "$dest" apply "$project/patches/qemu-0.10.6/0004-filesystem.patch"
fi
if [ "$checkpoint" = 0.06-runtime ] || [ "$checkpoint" = 0.08-graphics ] || [ "$checkpoint" = 0.09-graphics ] || [ "$checkpoint" = 0.10-graphics ]; then
    git -C "$dest" apply --check "$project/patches/qemu-0.10.6/0005-runtime-quartz.patch"
    git -C "$dest" apply "$project/patches/qemu-0.10.6/0005-runtime-quartz.patch"
fi
if [ "$checkpoint" = 0.08-graphics ] || [ "$checkpoint" = 0.09-graphics ] || [ "$checkpoint" = 0.10-graphics ]; then
    git -C "$dest" apply --check "$project/patches/qemu-0.10.6/0006-processes-iokit.patch"
    git -C "$dest" apply "$project/patches/qemu-0.10.6/0006-processes-iokit.patch"
fi
if [ "$checkpoint" = 0.09-graphics ] || [ "$checkpoint" = 0.10-graphics ]; then
    git -C "$dest" apply --check "$project/patches/qemu-0.10.6/0007-statfs-signals-iokit.patch"
    git -C "$dest" apply "$project/patches/qemu-0.10.6/0007-statfs-signals-iokit.patch"
fi

if [ "$checkpoint" = 0.10-graphics ]; then
    git -C "$dest" apply --check "$project/patches/qemu-0.10.6/0008-native-mach-graphics.patch"
    git -C "$dest" apply "$project/patches/qemu-0.10.6/0008-native-mach-graphics.patch"
fi
