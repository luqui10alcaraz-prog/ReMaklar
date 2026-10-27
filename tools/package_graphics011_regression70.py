from pathlib import Path
import io,tarfile
script=Path('scripts/darwin6-graphics-010-regression.sh').read_text().replace('out=/var/tmp/graphics010-regression19','out=/var/tmp/graphics011-regression70').replace('exe=/var/tmp/graphics010-run19/qemu-ppc','exe=/var/tmp/graphics011-build68/qemu-ppc')
script=script.replace('set -x\n',"set -x\ntrap 'status=$?;echo script_exit=$status > \"$out/script-status.txt\";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/reg70.tgz graphics011-regression70;sync;umount /exchange' 0\n",1)
target=Path('build/regression011-70.tgz');assert not target.exists()
with tarfile.open(target,'w:gz') as tar:
 data=script.replace('\r\n','\n').encode();info=tarfile.TarInfo('regression011-70.sh');info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-regression70.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/reg70i.tgz\numount /exchange\nsh /var/tmp/regression011-70.sh\n')
