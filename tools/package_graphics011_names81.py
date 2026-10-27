from pathlib import Path
import io,tarfile,ast
tree=ast.parse(Path('tools/package_graphics011_vmcopy65.py').read_text());files=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='files' for t in n.targets)))
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage81
out=/var/tmp/graphics011-run81-results
work=/var/tmp/graphics011-build81
test ! -e "$out";test ! -e "$work";mkdir "$out" "$work";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/run81.tgz graphics011-run81-results graphics011-joint81;sync;umount /exchange' 0
df -k / > "$out/disk.txt"
cp -Rp /var/tmp/graphics011-build77/build "$work/build"
'''
for name in files:script+=f'cmp -s "$p/source/{name}" "/var/tmp/graphics011-run1/source/{name}" || cp "$p/source/{name}" "/var/tmp/graphics011-run1/source/{name}"\n'
script+='''make -C "$work/build" SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
cp "$work/build/ppc-darwin-user/qemu-ppc" "$work/qemu-ppc"
exe="$work/qemu-ppc"
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/stress.c" -o "$out/stress-$arch" > "$out/stress-$arch-build.txt" 2>&1;done
perl "$probe" "$out/stress-native" "$out/stress-i386"
perl "$probe" "$out/stress-previous" /var/tmp/graphics011-build77/qemu-ppc --root /var/tmp/jaguar "$out/stress-ppc"
grep -q '^leader_exit=125$' "$out/stress-previous.status"
grep -q '^timeout=0$' "$out/stress-previous.status"
export REMAKLAR_QUIET_TLS=1
perl "$probe" "$out/stress-jaguar" "$exe" --root /var/tmp/jaguar "$out/stress-ppc"
cmp "$out/stress-native.stdout" "$out/stress-jaguar.stdout"
grep -q '^leader_exit=0$' "$out/stress-native.status"
grep -q '^leader_exit=0$' "$out/stress-jaguar.status"
grep -q '^timeout=0$' "$out/stress-jaguar.status"
for name in vmcopy rename fcntl taskthreads priority forkio kinfo ool remoteio remote shared high timer capability trailer;do
 perl "$probe" "$out/$name-jaguar" "$exe" --root /var/tmp/jaguar "/var/tmp/graphics011-run65/$name-ppc"
 grep -q '^leader_exit=0$' "$out/$name-jaguar.status"
 grep -q '^timeout=0$' "$out/$name-jaguar.status"
done
perl "$probe" "$out/threads" "$exe" --root /var/tmp/jaguar /var/tmp/graphics011-run65/threads-ppc
perl "$probe" "$out/fasttrap" "$exe" --root /var/tmp/jaguar /var/tmp/graphics011-run65/fasttrap-ppc
echo probes_completed > "$out/phase.txt"
sync
export REMAKLAR_OBSERVE_APPKIT=1
export REMAKLAR_OBSERVE_APPKIT_OFFSETS=624e0,1c7758,1c779c,1c7800
export REMAKLAR_TRACE_PATHS=1
perl "$p/joint.pl" /var/tmp/graphics011-joint81 "$exe" /var/tmp/jaguar
'''
joint=Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_text().replace('if(/^unsupported ', 'if(/^remaklar: / || /^unsupported ')
members=[('run.sh',script.encode()),('joint.pl',joint.encode()),('stress.c',Path('tests/ppc/rename-stress011-runtime.c').read_bytes())]+[('source/'+f,Path('build/qemu-011-source',f).read_bytes()) for f in files]
target=Path('build/names011-81.tgz');assert not target.exists()
with tarfile.open(target,'w:gz') as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=tarfile.TarInfo('graphics011-stage81/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-names81.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/name81i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage81/run.sh\n')
