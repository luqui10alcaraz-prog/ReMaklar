#!/bin/sh
# Prepared for the future native build. Not yet validated in Darwin 6.
# No Python, GLib, Meson or modern GCC flags are required by this script.
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
case $(uname -s) in Darwin) ;; *) echo 'Run this script inside Darwin' >&2; exit 1;; esac
mkdir -p "$project/build/qemu-darwin6"
cd "$project/build/qemu-darwin6"
sh "$project/experiments/qemu-0.10.6/configure" \
    --target-list=ppc-darwin-user --enable-darwin-user --cpu=i386 \
    --disable-system --disable-linux-user --disable-bsd-user \
    --disable-sdl --disable-curses --disable-kvm --disable-kqemu \
    --disable-aio --disable-brlapi --disable-bluez --disable-vnc-tls \
    --extra-cflags='-fno-strict-aliasing'
