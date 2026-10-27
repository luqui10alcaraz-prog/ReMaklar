from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage111
out=/var/tmp/graphics011-joint111-results
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk2 /exchange;cd /var/tmp;gnutar czf /exchange/RUNS/joint111.tgz graphics011-joint111-results graphics011-joint111;sync;umount /exchange' 0
md5 /mach_kernel /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer > "$out/original-md5.txt"
mount > "$out/mounts.txt"
kextstat > "$out/kextstat.txt"
export REMAKLAR_QUIET_TLS=1
export REMAKLAR_TRACE_PATHS=1
export REMAKLAR_JOINT_SAMPLES=72
perl "$p/joint.pl" /var/tmp/graphics011-joint111 /var/tmp/graphics011-build108/qemu-ppc /var/tmp/jaguar
'''
target=Path('build/joint011-111.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in [('run.sh',script.encode()),('joint.pl',Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_bytes())]:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage111/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-joint111.txt').write_text('\nmount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/j111i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage111/run.sh\n')
