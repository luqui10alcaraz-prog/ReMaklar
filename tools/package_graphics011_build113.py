from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-stage113
out=/var/tmp/graphics011-build113-results
work=/var/tmp/graphics011-build113
test ! -e "$out";test ! -e "$work";mkdir "$out" "$work";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk2 /exchange;cd /var/tmp;gnutar czf /exchange/RUNS/build113.tgz graphics011-build113-results;sync;umount /exchange' 0
for file in darwin-kernel.c live-regions.inc typed-live.c typed-live.h;do cp "$p/$file" /var/tmp/graphics011-run1/source/darwin-user/remaklar/;done
make -C /var/tmp/graphics011-build81/build SRC_PATH=/var/tmp/graphics011-run1/source subdir-ppc-darwin-user > "$out/build.txt" 2>&1
cp /var/tmp/graphics011-build81/build/ppc-darwin-user/qemu-ppc "$work/qemu-ppc"
for kind in key mouse;do gcc2 -no-cpp-precomp -arch i386 -I"$p" "$p/hid-$kind-fields.c" "$p/typed-live.c" -o "$out/fields-$kind-i386" > "$out/fields-$kind-build.txt" 2>&1;"$out/fields-$kind-i386" > "$out/fields-$kind.stdout" 2> "$out/fields-$kind.stderr";done
for arch in i386 ppc;do
 gcc2 -no-cpp-precomp -arch "$arch" "$p/hid.c" -framework IOKit -framework CoreFoundation -o "$out/hid-$arch" > "$out/hid-$arch-build.txt" 2>&1
 gcc2 -no-cpp-precomp -arch "$arch" "$p/names.c" -framework IOKit -framework CoreFoundation -o "$out/names-$arch" > "$out/names-$arch-build.txt" 2>&1
done
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
export REMAKLAR_QUIET_TLS=1
perl "$probe" "$out/names-native" "$out/names-i386"
perl "$probe" "$out/names-previous" /var/tmp/graphics011-build112/qemu-ppc --root /var/tmp/jaguar "$out/names-ppc"
grep -q '^leader_exit=125$' "$out/names-previous.status"
perl "$probe" "$out/names-jaguar" "$work/qemu-ppc" --root /var/tmp/jaguar "$out/names-ppc"
cmp "$out/names-native.stdout" "$out/names-jaguar.stdout"
for mode in native jaguar;do grep -q '^leader_exit=0$' "$out/names-$mode.status";grep -q '^timeout=0$' "$out/names-$mode.status";done
echo build_and_names_completed > "$out/phase.txt"
'''
members=[('run.sh',script.encode()),('hid.c',Path('tests/ppc/hid011-input-runtime.c').read_bytes()),('names.c',Path('tests/ppc/registry-name011-runtime.c').read_bytes())]
for kind in ('key','mouse'):members.append(('hid-'+kind+'-fields.c',Path('tests/memory/hid-'+kind+'-fields011-test.c').read_bytes()))
for name in ['darwin-kernel.c','live-regions.inc','typed-live.c','typed-live.h']:members.append((name,Path('build/qemu-011-source/darwin-user/remaklar/'+name).read_bytes()))
target=Path('build/build011-113.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo('graphics011-stage113/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-build113.txt').write_text('\nmount -t msdos /dev/disk2 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/b113i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage113/run.sh\n')
