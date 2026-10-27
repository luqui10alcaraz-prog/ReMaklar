from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage115
out=/var/tmp/graphics011-input115-results
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk2 /exchange;cd /var/tmp;gnutar czf /exchange/RUNS/input115.tgz graphics011-input115-results;sync;umount /exchange' 0
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/hid.c" -framework IOKit -framework CoreFoundation -o "$out/hid-$arch" > "$out/build-$arch.txt" 2>&1;done
'''
with tarfile.open('build/input011-114.tgz') as tar:runner=tar.extractfile('graphics011-stage114/run.sh').read().decode()
runner=runner.replace('114','116').replace('graphics011-build113-results','graphics011-input115-results')
target=Path('build/input011-115.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in [('graphics011-stage115/run.sh',script.encode()),('graphics011-stage115/hid.c',Path('tests/ppc/hid011-input-runtime.c').read_bytes()),('graphics011-stage116/run.sh',runner.encode())]:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-input115.txt').write_text('\nmount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/in115i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage115/run.sh\n')
