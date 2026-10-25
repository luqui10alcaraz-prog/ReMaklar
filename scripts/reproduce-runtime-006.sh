#!/bin/sh
# Fresh offline reconstruction from the preserved local upstream Git object.
# SPDX-License-Identifier: MIT
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
dest=${1:?usage: new-absolute-work-directory}
case "$dest" in /*) ;; *) echo 'Absolute destination required' >&2; exit 1;; esac
test ! -e "$dest"
mkdir -p "$dest/source" "$dest/build" "$dest/logs"
git -C "$project/experiments/qemu-0.10.6" archive 9eab386edbf8cf002a731f8204a156f243a47a57 > "$dest/upstream.tar"
tar xf "$dest/upstream.tar" -C "$dest/source"
# Isolate git apply from any enclosing repository's directory prefix.
git init -q "$dest/source"
for patch in "$project"/patches/qemu-0.10.6/000[1-5]-*.patch; do
    git -C "$dest/source" apply --check "$patch"
    git -C "$dest/source" apply "$patch"
done
REMAKLAR_QEMU_DIR="$dest/source" REMAKLAR_BUILD_DIR="$dest/build" \
    sh "$project/scripts/configure-qemu-linux32.sh" > "$dest/logs/configure.txt" 2>&1
make -C "$dest/build" -j2 subdir-ppc-darwin-user > "$dest/logs/build.txt" 2>&1
export REMAKLAR_EXECUTOR="$dest/build/ppc-darwin-user/qemu-ppc"
REMAKLAR_FIXTURE_LOGDIR="$dest/logs/fixtures" \
    python3 "$project/tests/ppc/run_tests.py" > "$dest/logs/fixtures.txt" 2>&1
set +e
REMAKLAR_DYNAMIC_LOGDIR="$dest/logs/dynamic" \
    python3 "$project/tests/ppc/test_dynamic.py" > "$dest/logs/dynamic.txt" 2>&1
status=$?
set -e
echo "$status" > "$dest/logs/dynamic-runner.status"
echo "Build and fixtures passed; dynamic runner status=$status (inspect logs)."
