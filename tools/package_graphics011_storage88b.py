from pathlib import Path
import tarfile,io
script='''#!/bin/sh
set -eu
out=/exchange/storage88-complete
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
gcc2 -no-cpp-precomp -arch i386 /var/tmp/tree011-compare.c -o "$out/compare" > "$out/build.txt" 2>&1
for dir in /var/tmp/* /var/tmp/.[!.]*;do
 name=${dir##*/}
 case "$name" in [a-i]*|jaguar) continue;;esac
 if test -e "$dir" || test -L "$dir";then
  echo "COPY_REMAINDER $dir"
  cp -Rp "$dir" /exchange/ > "$out/copy-$name.txt" 2>&1 || echo "COPY_WARNINGS $dir; full content verification follows"
 fi
done
"$out/compare" /var/tmp /exchange > "$out/verify.txt" 2>&1
md5 /mach_kernel /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer /exchange/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer > "$out/original-md5.txt"
echo COPY_COMPLETE
sync
'''
target=Path('build/storage011-88b.tgz');assert not target.exists()
with tarfile.open(target,'w:gz') as tar:
 for name,b in [('storage011-88b.sh',script.encode()),('tree011-compare.c',Path('tests/memory/tree011-compare.c').read_bytes())]:
  info=tarfile.TarInfo(name);info.size=len(b);tar.addfile(info,io.BytesIO(b))
Path('build/guest011-storage88-complete.txt').write_text('cd /\numount /var/tmp\nmount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/st88bi.tgz\ncd /\numount /exchange\nmount -t ufs /dev/disk1s1 /exchange\nsh /var/tmp/storage011-88b.sh\n')
