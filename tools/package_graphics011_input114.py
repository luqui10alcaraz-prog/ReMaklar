from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
with tarfile.open('build/input011-110.tgz') as tar:script=tar.extractfile('graphics011-stage110/run.sh').read().decode()
script=script.replace('110','114').replace('graphics011-build108-results','graphics011-build113-results').replace('graphics011-build101/qemu-ppc','graphics011-build112/qemu-ppc').replace('graphics011-build108/qemu-ppc','graphics011-build113/qemu-ppc')
script=script.replace('"$bin/hid-i386";;','"$bin/hid-i386" --mouse;;').replace('"$bin/hid-ppc";;','"$bin/hid-ppc" --mouse;;')
target=Path('build/input011-114.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 data=script.encode();info=Darwin6TarInfo('graphics011-stage114/run.sh');info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-input114-setup.txt').write_text('\nmount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/in114i.tgz\numount /exchange\n')
