#!/bin/sh
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
build_dir=${REMAKLAR_BUILD_DIR:-$project/build/qemu-linux32}
mkdir -p "$build_dir" "$project/logs"
cd "$build_dir"
sh "${REMAKLAR_QEMU_DIR:-$project/experiments/qemu-0.10.6}/configure" \
  --target-list=ppc-darwin-user --enable-darwin-user \
  --disable-system --disable-linux-user --disable-bsd-user \
  --cpu=i386 --disable-sdl --disable-curses --disable-kvm --disable-kqemu \
  --disable-aio --disable-brlapi --disable-bluez --disable-vnc-tls \
  --extra-cflags='-m32 -fno-pie -fcommon -fno-strict-aliasing -fno-tree-vectorize -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-stack-protector -fno-stack-clash-protection -fno-builtin' \
  --extra-ldflags='-m32 -no-pie'
