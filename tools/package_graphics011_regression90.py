from pathlib import Path
import io,tarfile
script=Path('scripts/darwin6-graphics-010-regression.sh').read_text().replace('out=/var/tmp/graphics010-regression19','out=/var/tmp/graphics011-regression90').replace('exe=/var/tmp/graphics010-run19/qemu-ppc','exe=/var/tmp/graphics011-build89/qemu-ppc')
script=script.replace('set -x\n',"set -x\nexport REMAKLAR_QUIET_TLS=1\ntrap 'status=$?;echo script_exit=$status > \"$out/script-status.txt\";sync;mount -t msdos /dev/disk2 /exchange;cd /var/tmp;gnutar czf /exchange/reg90.tgz graphics011-regression90;sync;umount /exchange' 0\n",1)
target=Path('build/regression011-90.tgz');assert not target.exists()
with tarfile.open(target,'w:gz') as tar:
 data=script.replace('\r\n','\n').encode();info=tarfile.TarInfo('regression011-90.sh');info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-regression90.txt').write_text('mount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/reg90i.tgz\numount /exchange\nsh /var/tmp/regression011-90.sh\n')
