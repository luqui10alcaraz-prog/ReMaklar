#!/bin/sh
set -u
out=/var/tmp/graphics010-native-fixtures19
payload=/var/tmp/graphics010-native-fixtures
exe=/var/tmp/graphics010-run19/qemu-ppc
test ! -e "$out" || exit 1
mkdir "$out" || exit 1
failed=0
for item in exit42:42 write:0 write-ebadf:0 write-efault:0 load-be:0 unsupported-syscall:125 illegal-instruction:125 memory-fault:126 truncated:125 bad-command:125 needs-dyld:125;do
 name=${item%:*};expected=${item#*:}
 perl -e 'alarm 30;exec @ARGV' "$exe" "$payload/$name.macho" > "$out/$name.stdout" 2> "$out/$name.stderr"
 actual=$?
 echo "$name exit=$actual expected=$expected" >> "$out/results.txt"
 if [ "$actual" != "$expected" ];then failed=1;fi
done
echo "failed=$failed" >> "$out/results.txt"
mount -t msdos /dev/disk1 /exchange
cd /var/tmp
gnutar czf /exchange/fixtures.tgz graphics010-native-fixtures19
sync
umount /exchange
exit "$failed"
