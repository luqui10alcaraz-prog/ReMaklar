from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
out=/var/tmp/graphics011-input104-results
p=/var/tmp/graphics011-stage104
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk2 /exchange;cd /var/tmp;gnutar czf /exchange/RUNS/input104.tgz graphics011-input104-results;sync;umount /exchange' 0
mount > "$out/mounts.txt"
ioreg -l -w 0 > "$out/ioreg.txt"
umount /dev/disk3s0 > "$out/umount-cd.txt" 2>&1 || true
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/hid.c" -framework IOKit -framework CoreFoundation -o "$out/hid-$arch" > "$out/build-$arch.txt" 2>&1;done
echo ready_native_probe > "$out/phase.txt"
"$out/hid-i386" > "$out/native.stdout" 2> "$out/native.stderr"
'''
target=Path('build/input011-104.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in [('run.sh',script.encode()),('hid.c',Path('tests/ppc/hid011-input-runtime.c').read_bytes())]:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage104/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-input104.txt').write_text('\nmount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/in104i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage104/run.sh\n')
