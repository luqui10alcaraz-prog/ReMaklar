from pathlib import Path
import tarfile,io
script='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-bundle72
out=/var/tmp/graphics011-bundle72-results
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/bun72.tgz graphics011-bundle72-results;sync;umount /exchange' 0
for arch in i386 ppc;do gcc2 -no-cpp-precomp -arch "$arch" "$p/bundle.c" -framework CoreFoundation -o "$out/bundle-$arch" > "$out/build-$arch.txt" 2>&1;done
probe=/var/tmp/graphics009-r8/run_graphics_008.pl
app=/var/tmp/jaguar/Applications/Utilities/Installer.app
ls -la "$app/Contents/Resources/English.lproj/PagedInstaller.nib" > "$out/nib-files.txt"
md5 "$app/Contents/Info.plist" "$app/Contents/Resources/English.lproj/PagedInstaller.nib"/* > "$out/resource-md5.txt"
perl "$probe" "$out/bundle-native" "$out/bundle-i386" "$app"
perl "$probe" "$out/bundle-jaguar" /var/tmp/graphics011-build68/qemu-ppc --root /var/tmp/jaguar "$out/bundle-ppc" "$app"
'''
target=Path('build/bundle011-72.tgz');assert not target.exists()
with tarfile.open(target,'w:gz') as tar:
 for name,data in [('run.sh',script.encode()),('bundle.c',Path('tests/ppc/bundle011-runtime.c').read_bytes())]:
  data=data.replace(b'\r\n',b'\n');info=tarfile.TarInfo('graphics011-bundle72/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-bundle72.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/bun72i.tgz\numount /exchange\nsh /var/tmp/graphics011-bundle72/run.sh\n')
