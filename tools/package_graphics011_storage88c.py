from pathlib import Path
import io,tarfile
script='''#!/bin/sh
set -eu
out=/exchange/storage88-complete
test ! -e "$out/verify2.txt"
cp /var/tmp/tree011-compare.c /exchange/tree011-compare.c
cp /var/tmp/storage011-88c.sh /exchange/storage011-88c.sh
gcc2 -no-cpp-precomp -arch i386 /var/tmp/tree011-compare.c -o "$out/compare2" > "$out/build2.txt" 2>&1
"$out/compare2" /var/tmp /exchange --repair-modes > "$out/verify2.txt" 2>&1
"$out/compare2" /var/tmp /exchange > "$out/verify3-strict.txt" 2>&1
md5 /mach_kernel /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer /exchange/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer > "$out/original-md5.txt"
echo COPY_COMPLETE
sync
'''
target=Path('build/storage011-88c.tgz');assert not target.exists()
with tarfile.open(target,'w:gz') as tar:
 for name,b in [('storage011-88c.sh',script.encode()),('tree011-compare.c',Path('tests/memory/tree011-compare.c').read_bytes())]:
  info=tarfile.TarInfo(name);info.size=len(b);tar.addfile(info,io.BytesIO(b))
Path('build/guest011-storage88-verify2.txt').write_text('cd /\numount /exchange\nmount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/st88ci.tgz\ncd /\numount /exchange\nmount -t ufs /dev/disk1s1 /exchange\nsh /var/tmp/storage011-88c.sh\n')
