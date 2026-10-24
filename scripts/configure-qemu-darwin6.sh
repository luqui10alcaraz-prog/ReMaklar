#!/bin/sh
# Experimental native build; see docs/darwin6-native.md for measured limits.
# No Python, GLib, Meson or modern GCC flags are required by this script.
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
case $(uname -s) in Darwin) ;; *) echo 'Run this script inside Darwin' >&2; exit 1;; esac
mkdir -p "$project/build/qemu-darwin6"
cd "$project/build/qemu-darwin6"
sh "$project/experiments/qemu-0.10.6/configure" \
    --cc='gcc2 -no-cpp-precomp' --host-cc='gcc2 -no-cpp-precomp' \
    --target-list=ppc-darwin-user --enable-darwin-user --cpu=i386 --enable-remaklar-bootstrap \
    --disable-system --disable-linux-user --disable-bsd-user \
    --disable-sdl --disable-curses --disable-kvm --disable-kqemu \
    --disable-aio --disable-brlapi --disable-bluez --disable-vnc-tls \
    --extra-cflags='-fno-strict-aliasing -fno-builtin'
test -f config-host.mak
