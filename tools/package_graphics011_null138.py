"""Verify actual initialized native kernel HID bytes before original GUI."""
from pathlib import Path
import io,tarfile
from darwin6_tar import Darwin6TarInfo
with tarfile.open('build/build011-135.tgz') as source:
 script=source.extractfile('graphics011-stage135/run.sh').read().decode().replace('135','138')
 joint=source.extractfile('graphics011-stage137/run.sh').read().decode().replace('137','140').replace('build135','build138')
script=script.replace('bits tracking key mouse auxmouse shared;','bits tracking key mouse auxmouse shared null;')
script=script.replace('echo build46_and_native_units_complete', '''export REMAKLAR_QUIET_TLS=1
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
perl "$probe" "$out/native" "$out/hid-i386" --null-only
perl "$probe" "$out/previous" /var/tmp/graphics011-build135/qemu-ppc --root /var/tmp/jaguar "$out/hid-ppc" --null-only
grep -q '^leader_exit=125$' "$out/previous.status"
perl "$probe" "$out/jaguar" "$work/qemu-ppc" --root /var/tmp/jaguar "$out/hid-ppc" --null-only
cmp "$out/native.stdout" "$out/jaguar.stdout"
for mode in native jaguar;do grep -q '^leader_exit=0$' "$out/$mode.status";grep -q '^timeout=0$' "$out/$mode.status";done
echo build47_and_real_kernel_null_complete''')
members=[('graphics011-stage138/run.sh',script.encode()),('graphics011-stage138/hid.c',Path('tests/ppc/hid011-input-runtime.c').read_bytes()),('graphics011-stage140/run.sh',joint.encode()),('graphics011-stage140/joint.pl',Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_bytes())]
for name in ('darwin-kernel.c','live-regions.inc','typed-live.c','typed-live.h'):members.append(('graphics011-stage138/'+name,Path('build/qemu-011-source/darwin-user/remaklar/'+name).read_bytes()))
for kind in ('bits','tracking','key','mouse','auxmouse','shared','null'):
 name='typed-live-test.c' if kind=='shared' else ('hid-bits011-test.c' if kind=='bits' else 'hid-'+kind+'-fields011-test.c')
 members.append(('graphics011-stage138/'+kind+'.c',Path('tests/memory/'+name).read_bytes()))
target=Path('build/null011-138.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  data=data.replace(b'\r\n',b'\n');info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-null138.txt').write_text('\nmount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/RUNS/n138i.tgz\numount /exchange\nsh /var/tmp/graphics011-stage138/run.sh\n')
Path('build/guest011-joint140.txt').write_text('sh /var/tmp/graphics011-stage140/run.sh\n')
