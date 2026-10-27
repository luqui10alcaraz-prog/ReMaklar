from pathlib import Path
import io,tarfile
script='''#!/bin/sh
set -eu
mount -t msdos /dev/disk2 /exchange
/sbin/newfs -m 5 -v ReMaklarWork /dev/rdisk1s1 > /exchange/mkfs88.txt 2>&1
sync
umount /exchange
mount -t ufs /dev/disk1s1 /exchange
test ! -e /exchange/storage88-copy.txt
exec > /exchange/storage88-copy.txt 2>&1
set -x
date
df -k
for dir in /var/tmp/* /var/tmp/.[!.]*;do
 if test -e "$dir" || test -L "$dir";then
  echo "COPY $dir"
  cp -Rp "$dir" /exchange/
  date
  df -k /exchange
 fi
done
md5 /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer /exchange/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer
echo COPY_COMPLETE
sync
'''
target=Path('build/storage011-88.tgz');assert not target.exists()
with tarfile.open(target,'w:gz') as tar:
 b=script.encode();info=tarfile.TarInfo('storage011-88.sh');info.size=len(b);tar.addfile(info,io.BytesIO(b))
Path('build/guest011-storage88-copy.txt').write_text('mount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/st88i.tgz\numount /exchange\ncd /\nsh /var/tmp/storage011-88.sh\n')
