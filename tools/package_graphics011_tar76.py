from pathlib import Path
import io,tarfile
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-resources75
out=/var/tmp/graphics011-tar76-results
test ! -e "$out";mkdir "$out" "$out/old" "$out/safe";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/tar76.tgz graphics011-tar76-results;sync;umount /exchange' 0
gnutar xf "$p/boundary-old.tar" -C "$out/old"
gnutar xf "$p/boundary-safe.tar" -C "$out/safe"
'''
directory='a'*89
script+=f'test -f "$out/old/{directory}/'+('b'*9)+'"\n'
script+=f'test ! -e "$out/old/{directory}/'+('b'*10)+'"\n'
script+=f'test -f "$out/safe/{directory}/'+('b'*10)+'"\n'
script+='find "$out/old" "$out/safe" -type f > "$out/extracted-paths.txt"\necho native_Darwin6_100_byte_header_truncation_reproduced_and_prefix_fix_verified > "$out/result.txt"\n'
target=Path('build/tar011-76.tgz');assert not target.exists()
with tarfile.open(target,'w:gz') as tar:
 data=script.encode();info=tarfile.TarInfo('graphics011-tar76.sh');info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-tar76.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/tar76i.tgz\numount /exchange\nsh /var/tmp/graphics011-tar76.sh\n')
