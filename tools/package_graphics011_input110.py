from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
with tarfile.open('build/input011-109.tgz') as tar:script=tar.extractfile('graphics011-stage109/run.sh').read().decode()
script=script.replace('mode=$1','mode=$1\nattempt=$2').replace('109-$mode','110-$mode$attempt').replace('109-$mode','110-$mode$attempt')
target=Path('build/input011-110.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 data=script.encode();info=Darwin6TarInfo('graphics011-stage110/run.sh');info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-input110-setup.txt').write_text('\nmount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/in110i.tgz\numount /exchange\n')
