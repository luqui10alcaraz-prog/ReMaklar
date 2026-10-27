"""Build tracking/flags fix, native compiler oracles and real mouse probe."""
from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage135
out=/var/tmp/graphics011-build135-results
work=/var/tmp/graphics011-build135
test ! -e "$out";test ! -e "$work";mkdir "$out" "$work";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/RUNS/build135.tgz graphics011-build135-results;sync;umount /exchange' 0
for name in darwin-kernel.c live-regions.inc typed-live.c typed-live.h;do cp "$p/$name" /var/tmp/graphics011-run1/source/darwin-user/remaklar/;done
make -C /var/tmp/graphics011-build81/build SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
cp /var/tmp/graphics011-build81/build/ppc-darwin-user/qemu-ppc "$work/qemu-ppc"
for kind in bits tracking key mouse auxmouse shared;do gcc2 -no-cpp-precomp -arch i386 -I"$p" "$p/$kind.c" "$p/typed-live.c" -o "$out/unit-$kind" > "$out/unit-$kind-build.txt" 2>&1;"$out/unit-$kind" > "$out/unit-$kind.stdout" 2> "$out/unit-$kind.stderr";done
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/hid.c" -framework IOKit -framework CoreFoundation -o "$out/hid-$arch" > "$out/hid-$arch-build.txt" 2>&1;done
md5 "$work/qemu-ppc" > "$out/executor-md5.txt"
echo build46_and_native_units_complete > "$out/phase.txt"
'''
with tarfile.open('build/build011-122.tgz') as tar:runner=tar.extractfile('graphics011-stage123/run.sh').read().decode().replace('123','136').replace('build122','build135').replace('build113','build133').replace('--mouse','--mouse --tracking')
runner=runner.replace("grep -q '^leader_exit=125$'", "grep -q '^leader_exit=8$'")
with tarfile.open('build/enxio011-133.tgz') as tar:joint=tar.extractfile('graphics011-stage134/run.sh').read().decode().replace('134','137').replace('build133','build135')
members=[('graphics011-stage135/run.sh',script.encode()),('graphics011-stage136/run.sh',runner.encode()),('graphics011-stage137/run.sh',joint.encode()),('graphics011-stage135/hid.c',Path('tests/ppc/hid011-input-runtime.c').read_bytes()),('graphics011-stage137/joint.pl',Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_bytes())]
for name in ('darwin-kernel.c','live-regions.inc','typed-live.c','typed-live.h'):members.append(('graphics011-stage135/'+name,Path('build/qemu-011-source/darwin-user/remaklar/'+name).read_bytes()))
for kind in ('bits','tracking','key','mouse','auxmouse','shared'):
 name='typed-live-test.c' if kind=='shared' else ('hid-bits011-test.c' if kind=='bits' else 'hid-'+kind+'-fields011-test.c')
 members.append(('graphics011-stage135/'+kind+'.c',Path('tests/memory/'+name).read_bytes()))
target=Path('build/build011-135.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-build135.txt').write_text('\nmount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/b135i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage135/run.sh\n')
Path('build/guest011-joint137.txt').write_text('sh /var/tmp/graphics011-stage137/run.sh\n')
