from pathlib import Path
import io,tarfile
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage68
out=/var/tmp/graphics011-run68-results
work=/var/tmp/graphics011-build68
test ! -e "$out";test ! -e "$work";mkdir "$out" "$work";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/run68.tgz graphics011-run68-results graphics011-joint68;sync;umount /exchange' 0
cp -Rp /var/tmp/graphics011-run67/build "$work/build"
'''
files=['darwin-user/qemu.h','darwin-user/remaklar/bootstrap-main.c','darwin-user/remaklar/darwin-kernel.c','darwin-user/remaklar/remote-maps.inc']
for name in files:script+=f'cp "$p/source/{name}" "/var/tmp/graphics011-run1/source/{name}"\n'
script+='''make -C "$work/build" SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
cp "$work/build/ppc-darwin-user/qemu-ppc" "$work/qemu-ppc"
gcc2 -no-cpp-precomp -arch i386 -O2 -I"$p/previous" "$p/mailbox.c" -o "$work/mailbox-previous" > "$out/mailbox-previous-build.txt" 2>&1
perl /var/tmp/graphics009-r8/run_graphics_008.pl "$out/mailbox-previous" "$work/mailbox-previous"
grep -q '^leader_exit=1$' "$out/mailbox-previous.status"
grep -q '^timeout=0$' "$out/mailbox-previous.status"
md5 /mach_kernel /var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer "$work/qemu-ppc" > "$out/binary-md5.txt"
export REMAKLAR_OBSERVE_APPKIT=1
perl "$p/joint.pl" /var/tmp/graphics011-joint68 "$work/qemu-ppc" /var/tmp/jaguar
'''
joint=Path('tests/ppc/run_graphics_011_installer_joint.pl').read_text()
joint=joint.replace('$leader{$name}=$pid;'*7,'$leader{$name}=$pid;').replace(' last if $exited{$leader{installer}};\n'*7,' last if $exited{$leader{installer}};\n')
members=[('run.sh',script.encode()),('joint.pl',joint.encode()),('mailbox.c',Path('tests/memory/remote-mailbox011-lifecycle.c').read_bytes()),('previous/remote-maps.inc',Path('build/011-vmcopy-patch-check/darwin-user/remaklar/remote-maps.inc').read_bytes())]
members += [('source/'+f,Path('build/qemu-011-source',f).read_bytes()) for f in files]
target=Path('build/observe011-68.tgz');assert not target.exists()
with tarfile.open(target,'w:gz') as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=tarfile.TarInfo('graphics011-stage68/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-observe68.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/obs68i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage68/run.sh &\n')
