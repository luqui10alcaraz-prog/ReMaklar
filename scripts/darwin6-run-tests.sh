#!/bin/sh
# Native guest checks with the unchanged Linux fixtures and Apple samples.
# SPDX-License-Identifier: MIT
cd /var/tmp/remaklar || exit 1
exe=/var/tmp/remaklar/build/qemu-darwin6/ppc-darwin-user/qemu-ppc
root=/var/tmp/remaklar/research/samples-local
out=/var/tmp/remaklar-results
{
    uname -a
    arch
    mount
    file "$exe"
} > "$out/native-tests.log"
otool -l "$exe" > "$out/executor-load-commands.log"
failed=0
for item in exit42:42 write:0 write-ebadf:0 write-efault:0 load-be:0 unsupported-syscall:125 illegal-instruction:125 memory-fault:126 truncated:125 bad-command:125 needs-dyld:125; do
    name=${item%:*}
    expected=${item#*:}
    perl -e 'alarm 30; exec @ARGV' "$exe" "build/fixtures/$name.macho" > "$out/$name.stdout" 2> "$out/$name.stderr"
    status=$?
    echo "$name exit=$status expected=$expected" >> "$out/native-tests.log"
    if [ "$status" != "$expected" ]; then failed=1; fi
done
printf 'ReMaklar PPC -> Intel\n' > "$out/write.expected"
if ! cmp "$out/write.expected" "$out/write.stdout"; then failed=1; fi
for name in true false; do
    expected=0
    if [ "$name" = false ]; then expected=1; fi
    perl -e 'alarm 60; exec @ARGV' "$exe" --root "$root" "$root/usr/bin/$name" > "$out/$name.stdout" 2> "$out/$name.stderr"
    status=$?
    echo "$name exit=$status expected=$expected" >> "$out/native-tests.log"
    if [ "$status" != "$expected" ] || [ -s "$out/$name.stdout" ] ||
       ! grep -q 'startup: entered original executable at 0000195c' "$out/$name.stderr" ||
       ! grep -q ' r0=1 ' "$out/$name.stderr" ||
       ! grep -q "guest open $root/usr/lib/libSystem.B.dylib" "$out/$name.stderr" ||
       ! grep -q "guest open $root/usr/lib/system/libmathCommon.A.dylib" "$out/$name.stderr" ||
       grep -q 'unsupported\|unhandled host memory fault' "$out/$name.stderr" ||
       grep -q 'probe-main:' "$out/$name.stderr"; then
        failed=1
    fi
done
md5 "$root/usr/bin/true" "$root/usr/bin/false" "$root/usr/lib/dyld" "$root/usr/lib/libSystem.B.dylib" "$root/usr/lib/system/libmathCommon.A.dylib" > "$out/sample-md5.log"
echo failed=$failed >> "$out/native-tests.log"
cp "$out/native-tests.log" /exchange/tests.log
cp "$out/executor-load-commands.log" /exchange/exe.log
cp "$out/sample-md5.log" /exchange/md5.log
cp "$out/true.stdout" /exchange/true.out
cp "$out/true.stderr" /exchange/true.err
cp "$out/false.stdout" /exchange/false.out
cp "$out/false.stderr" /exchange/false.err
return_status=$failed
exit "$return_status"
