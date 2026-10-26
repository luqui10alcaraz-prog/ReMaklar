#!/bin/sh
set -eu
p=/var/tmp/graphics011-validation31
out=/var/tmp/graphics011-validation31-results
exe=/var/tmp/graphics011-run30/qemu-ppc
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;for dir in graphics011-validation31-results graphics011-regression30 graphics011-joint30;do if test -d "$dir";then for f in "$dir"/*.txt "$dir"/*.status "$dir"/*.stdout "$dir"/*.stderr;do if test -f "$f";then echo "$f";fi;done;fi;done > "$out/export-list.txt";gnutar czf /exchange/valid31.tgz -T "$out/export-list.txt";sync;umount /exchange' 0
for name in fasttrap capability-native capability-jaguar high-native high-jaguar timer-native timer-jaguar threads typed-native shared-native shared-jaguar;do
 grep -q '^leader_exit=0$' "/var/tmp/graphics011-run30/$name.status"
 grep -q '^timeout=0$' "/var/tmp/graphics011-run30/$name.status"
done
cmp /var/tmp/graphics011-run30/capability-native.stdout /var/tmp/graphics011-run30/capability-jaguar.stdout
echo self_tests_verified > "$out/phase.txt"
sh "$p/regression.sh"
echo native_regression_completed > "$out/phase.txt"
perl "$p/joint.pl" /var/tmp/graphics011-joint30 "$exe" /var/tmp/jaguar
echo joint_trial_completed > "$out/phase.txt"
