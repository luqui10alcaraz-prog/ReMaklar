from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
mode=$1
out=/var/tmp/graphics011-input109-$mode
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk2 /exchange;cd /var/tmp;gnutar czf /exchange/RUNS/input109-$mode.tgz graphics011-input109-$mode;sync;umount /exchange' 0
export REMAKLAR_QUIET_TLS=1
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
bin=/var/tmp/graphics011-build108-results
case "$mode" in
n) perl "$probe" "$out/probe" "$bin/hid-i386";;
p) perl "$probe" "$out/probe" /var/tmp/graphics011-build101/qemu-ppc --root /var/tmp/jaguar "$bin/hid-ppc";;
j) perl "$probe" "$out/probe" /var/tmp/graphics011-build108/qemu-ppc --root /var/tmp/jaguar "$bin/hid-ppc";;
*) exit 2;;
esac
cat "$out/probe.status"
if test "$mode" = p;then grep -q '^leader_exit=125$' "$out/probe.status";else grep -q '^leader_exit=0$' "$out/probe.status";grep -q '^timeout=0$' "$out/probe.status";fi
'''
target=Path('build/input011-109.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 data=script.encode();info=Darwin6TarInfo('graphics011-stage109/run.sh');info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-input109-n.txt').write_text('\nmount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/in109i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage109/run.sh n\n')
for mode in ('p','j'):Path('build/guest011-input109-'+mode+'.txt').write_text('sh /var/tmp/graphics011-stage109/run.sh '+mode+'\n')
