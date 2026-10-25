#!/bin/sh
# Run in a new directory on a disposable Darwin overlay. No PPC executor.
# SPDX-License-Identifier: MIT
set -eu
src=${1:?usage: source-directory new-output-directory}
out=${2:?usage: source-directory new-output-directory}
mode=${3:-all}
case "$mode" in all|--runtimes-only) ;; *) echo 'Invalid suite mode' >&2; exit 1;; esac
test ! -e "$out"
mkdir -p "$out"
cd "$out"
exec > session.txt 2>&1
set -x
uname -a
arch
gcc2 -v
ld -v || true
ls -l /usr/lib/crt*.o /usr/include/objc/Object.h
ls -l /System/Library/Frameworks/CoreFoundation.framework/Headers
ps -axww > processes.txt
for image in /mach_kernel /usr/lib/dyld /usr/lib/libSystem.B.dylib /usr/lib/libobjc.A.dylib /System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation; do
    file "$image"
    md5 "$image"
    otool -arch i386 -hv "$image"
    otool -arch i386 -L "$image"
done > installed-images.txt 2>&1
run_case() {
    name=$1
    shift
    echo "DIRECT COMMAND: $*" > "$name.command"
    set +e
    DYLD_PRINT_LIBRARIES=1 perl -e 'alarm 30;exec @ARGV; die $!' "$@" > "$name.stdout" 2> "$name.stderr"
    status=$?
    set -e
    echo "$status" > "$name.status"
}
build_case() {
    name=$1
    shift
    if gcc2 -no-cpp-precomp -arch i386 -I"$src/tests/native-i386" "$@" -o "$name" > "$name.build" 2>&1; then
        file "$name" > "$name.images"
        otool -arch i386 -hv -L "$name" >> "$name.images"
        md5 "$name" >> "$name.images"
        run_case "$name" "./$name"
    else
        echo BLOCKED > "$name.status"
    fi
}
if [ "$mode" = all ]; then
build_case hello "$src/tests/native-i386/hello.c"
if gcc2 -no-cpp-precomp -arch i386 -dynamiclib "$src/tests/native-i386/library.c" -install_name "$out/libprobe.dylib" -o libprobe.dylib > library.build 2>&1; then
    otool -arch i386 -hv -L libprobe.dylib > library.images
    build_case dynamic "$src/tests/native-i386/dynamic.c" -L. -lprobe
    if [ -f dynamic ]; then
        mv libprobe.dylib libprobe.hidden
        run_case missing-library ./dynamic
        mv libprobe.hidden libprobe.dylib
    fi
fi
fi
build_case objc "$src/tests/native-i386/objc.m" -lobjc
build_case cf "$src/tests/native-i386/cf.c" -framework CoreFoundation
echo NATIVE_007_RUN_COMPLETE
