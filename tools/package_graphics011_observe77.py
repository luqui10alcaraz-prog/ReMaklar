from pathlib import Path
import io,tarfile
files=['darwin-user/remaklar/bootstrap-main.c','darwin-user/remaklar/darwin-kernel.c']
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage77
out=/var/tmp/graphics011-run77-results
work=/var/tmp/graphics011-build77
test ! -e "$out";test ! -e "$work";mkdir "$out" "$work";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/run77.tgz graphics011-run77-results graphics011-joint77;sync;umount /exchange' 0
df -k / > "$out/disk.txt"
cp -Rp /var/tmp/graphics011-build68/build "$work/build"
'''
for name in files:script+=f'cp "$p/source/{name}" "/var/tmp/graphics011-run1/source/{name}"\n'
script+='''make -C "$work/build" SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
cp "$work/build/ppc-darwin-user/qemu-ppc" "$work/qemu-ppc"
export REMAKLAR_OBSERVE_APPKIT=1
export REMAKLAR_OBSERVE_APPKIT_OFFSETS=624e0,1c7684,1c7758,1c779c,1c7800
export REMAKLAR_TRACE_PATHS=1
perl "$p/joint.pl" /var/tmp/graphics011-joint77 "$work/qemu-ppc" /var/tmp/jaguar
'''
joint=Path('tests/ppc/run_graphics_011_installer_joint.pl').read_text().replace('$leader{$name}=$pid;'*7,'$leader{$name}=$pid;').replace(' last if $exited{$leader{installer}};\n'*7,' last if $exited{$leader{installer}};\n')
target=Path('build/observe011-77.tgz');assert not target.exists()
with tarfile.open(target,'w:gz') as tar:
 for name,data in [('run.sh',script.encode()),('joint.pl',joint.encode())]+[('source/'+f,Path('build/qemu-011-source',f).read_bytes()) for f in files]:
  data=data.replace(b'\r\n',b'\n');info=tarfile.TarInfo('graphics011-stage77/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-observe77.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/obs77i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage77/run.sh\n')
