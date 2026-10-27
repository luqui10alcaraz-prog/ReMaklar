from pathlib import Path
import tempfile,subprocess,tarfile,io,json,hashlib,shlex
from darwin6_tar import Darwin6TarInfo
names=['AquaKanaBold.otf','AquaKanaRegular.otf','Courier.dfont','Geneva.dfont','Helvetica.dfont','Keyboard.dfont','LastResort.dfont','LucidaGrande.dfont','Monaco.dfont','Symbol.dfont','Times.dfont','ZapfDingbats.dfont']
volume='Mac OS X Install Disc 1';temp=Path(tempfile.mkdtemp(prefix='remaklar-fonts82-'));prefix='System/Library/Fonts/'
r=subprocess.run(['7z','x','-y','-o'+str(temp),'media/Mac OS X Jaguar Install CD.iso']+[volume+'/'+prefix+n for n in names],capture_output=True,timeout=60);assert r.returncode==0,r.stdout+r.stderr
rows=[];members=[]
script='''#!/bin/sh
set -eu
out=/var/tmp/graphics011-fonts82-results
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/font82.tgz graphics011-fonts82-results graphics011-joint82;sync;umount /exchange' 0
mkdir -p /var/tmp/jaguar/System/Library/Fonts
df -k / > "$out/disk.txt"
'''
for name in names:
 data=(temp/volume/prefix/name).read_bytes();row={'path':prefix+name,'bytes':len(data),'md5':hashlib.md5(data).hexdigest(),'sha256':hashlib.sha256(data).hexdigest()};rows.append(row);members.append(('jaguar/'+prefix+name,data))
 dest=shlex.quote('/var/tmp/jaguar/'+prefix+name)
 script+=f'dest={dest}\ngot=$(md5 "$dest");case "$got" in *" = {row["md5"]}") ;; *) exit 30;;esac\nmd5 "$dest" >> "$out/font-md5.txt"\n'
script+='''export REMAKLAR_QUIET_TLS=1
export REMAKLAR_OBSERVE_APPKIT=1
export REMAKLAR_OBSERVE_APPKIT_OFFSETS=624e0,1c7758,1c779c,1c7800
export REMAKLAR_TRACE_PATHS=1
perl /var/tmp/graphics011-fonts82/joint.pl /var/tmp/graphics011-joint82 /var/tmp/graphics011-build81/qemu-ppc /var/tmp/jaguar
'''
joint=Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').read_text().replace('if(/^unsupported ','if(/^remaklar: / || /^unsupported ')
members += [('graphics011-fonts82/run.sh',script.encode()),('graphics011-fonts82/joint.pl',joint.encode())]
target=Path('build/fonts011-82.tgz');assert not target.exists()
with tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in members:
  info=Darwin6TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('reports/graphics-011/resume-validation/fonts82-original-cd-manifest.json').write_text(json.dumps({'source_iso':'media/Mac OS X Jaguar Install CD.iso','volume':volume,'files':rows},indent=2)+'\n')
Path('build/guest011-fonts82.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ntest ! -e jaguar/System/Library/Fonts && gnutar xzf /exchange/fnt82i.tgz\numount /exchange\nsh /var/tmp/graphics011-fonts82/run.sh\n')
print('Original font data bytes',sum(r['bytes'] for r in rows),'archive bytes',target.stat().st_size)
