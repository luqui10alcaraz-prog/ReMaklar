from pathlib import Path
import tarfile,io,json,hashlib,shlex
from darwin6_tar import Darwin6TarInfo
archive=Path('build/installer-originals-008.tgz');target=Path('build/resources011-75.tgz');assert not target.exists()
members=[];manifest=[]
with tarfile.open(archive) as tar:
 for item in tar:
  if not item.isfile():continue
  header=item.tobuf(tarfile.USTAR_FORMAT)
  if b'\0' in header[:100]:continue
  data=tar.extractfile(item).read();members.append(('repair75/'+item.name,data))
  manifest.append({'path':item.name,'bytes':len(data),'md5':hashlib.md5(data).hexdigest(),'sha256':hashlib.sha256(data).hexdigest()})
assert any(r['path'].endswith('English.lproj/PagedInstaller.nib/objects.nib') for r in manifest)
script='''#!/bin/sh
set -eu
out=/var/tmp/graphics011-resources75-results
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/res75.tgz graphics011-resources75-results graphics011-joint75;sync;umount /exchange' 0
'''
for row in manifest:
 src=shlex.quote('/var/tmp/repair75/'+row['path']);dst=shlex.quote('/var/tmp/jaguar/'+row['path']);parent=shlex.quote(str(Path('/var/tmp/jaguar/'+row['path']).parent).replace('\\','/'))
 script+=f'source={src};dest={dst}\n'
 script+=f'got=$(md5 "$source");case "$got" in *" = {row["md5"]}") ;; *) exit 30;;esac\n'
 script+=f'if test -e "$dest";then cmp "$source" "$dest";else mkdir -p {parent};cp -p "$source" "$dest";fi\n'
 script+='md5 "$dest" >> "$out/restored-md5.txt"\n'
script+='''export REMAKLAR_OBSERVE_APPKIT=1
perl /var/tmp/graphics011-resources75/joint.pl /var/tmp/graphics011-joint75 /var/tmp/graphics011-build68/qemu-ppc /var/tmp/jaguar
'''
joint=Path('tests/ppc/run_graphics_011_installer_joint.pl').read_text().replace('$leader{$name}=$pid;'*7,'$leader{$name}=$pid;').replace(' last if $exited{$leader{installer}};\n'*7,' last if $exited{$leader{installer}};\n')
members += [('graphics011-resources75/run.sh',script.encode()),('graphics011-resources75/joint.pl',joint.encode())]
# A synthetic regression fixture demonstrates old and safe headers side by side.
fixture='a'*89+'/'+'b'*10
assert len(fixture)==100
raw=io.BytesIO()
with tarfile.open(fileobj=raw,mode='w',format=tarfile.USTAR_FORMAT) as tar:
 info=tarfile.TarInfo(fixture);info.size=4;tar.addfile(info,io.BytesIO(b'old\n'))
members.append(('graphics011-resources75/boundary-old.tar',raw.getvalue()))
raw=io.BytesIO()
with tarfile.open(fileobj=raw,mode='w',format=tarfile.USTAR_FORMAT) as tar:
 info=Darwin6TarInfo(fixture);info.size=5;tar.addfile(info,io.BytesIO(b'safe\n'))
members.append(('graphics011-resources75/boundary-safe.tar',raw.getvalue()))
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('reports/graphics-011/resume-validation/resources75-manifest.json').write_text(json.dumps({'source':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':manifest},indent=2)+'\n')
Path('build/guest011-resources75.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/res75i.tgz\numount /exchange\nsh /var/tmp/graphics011-resources75/run.sh\n')
print('Restoring',len(manifest),'original files at the header boundary, without deleting truncated names.')
