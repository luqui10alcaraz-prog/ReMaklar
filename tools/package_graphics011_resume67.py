from pathlib import Path
import io,tarfile,ast
root=Path('.')
text=Path('tools/package_graphics011_vmcopy65.py').read_text()
tree=ast.parse(text)
files=ast.literal_eval(next(node.value for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='files' for t in node.targets)))
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage67
out=/var/tmp/graphics011-run67
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/run67.tgz graphics011-run67/*.txt graphics011-run67/*.status graphics011-run67/*.stdout graphics011-run67/*.stderr graphics011-joint67;sync;umount /exchange' 0
ln -s /var/tmp/graphics011-run1/source "$out/source"
cp -Rp /var/tmp/graphics011-run65/build "$out/build"
'''
for name in files:script+=f'cmp -s "$p/source/{name}" "$out/source/{name}" || cp "$p/source/{name}" "$out/source/{name}"\n'
script+='''make -C "$out/build" SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
exe="$out/build/ppc-darwin-user/qemu-ppc";cp "$exe" "$out/qemu-ppc"
gcc2 -no-cpp-precomp -arch i386 -O2 -I"$p/source/darwin-user/remaklar" "$p/mailbox.c" -o "$out/mailbox-native" > "$out/mailbox-build.txt" 2>&1
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
perl "$probe" "$out/mailbox-native" "$out/mailbox-native"
grep -q '^leader_exit=0$' "$out/mailbox-native.status"
grep -q '^timeout=0$' "$out/mailbox-native.status"
for name in vmcopy rename fcntl taskthreads priority forkio kinfo ool remoteio remote shared high timer capability trailer;do
 perl "$probe" "$out/$name-jaguar" "$exe" --root /var/tmp/jaguar "/var/tmp/graphics011-run65/$name-ppc"
 grep -q '^leader_exit=0$' "$out/$name-jaguar.status"
 grep -q '^timeout=0$' "$out/$name-jaguar.status"
done
perl "$probe" "$out/threads" "$exe" --root /var/tmp/jaguar /var/tmp/graphics011-run65/threads-ppc
perl "$probe" "$out/fasttrap" "$exe" --root /var/tmp/jaguar /var/tmp/graphics011-run65/fasttrap-ppc
sync
echo probes_completed > "$out/phase.txt"
perl "$p/joint.pl" /var/tmp/graphics011-joint67 "$exe" /var/tmp/jaguar
echo joint_trial_completed > "$out/phase.txt"
'''
joint=Path('tests/ppc/run_graphics_011_installer_joint.pl').read_text()
# Historical generators repeatedly inserted these same statements.
for line in ['$leader{$name}=$pid;',' last if $exited{$leader{installer}};\n']:
 while line+line in joint:joint=joint.replace(line+line,line)
joint=joint.replace("my $backend_block=0;","my $backend_block=0;\n")
members=[('run.sh',script.encode()),('mailbox.c',Path('tests/memory/remote-mailbox011-lifecycle.c').read_bytes()),('joint.pl',joint.encode())]
members += [('source/'+f,Path('build/qemu-011-source',f).read_bytes()) for f in files]
target=Path('build/resume011-67.tgz');assert not target.exists()
with tarfile.open(target,'w:gz') as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=tarfile.TarInfo('graphics011-stage67/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-resume67.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/res67i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage67/run.sh\n')
print(target)
