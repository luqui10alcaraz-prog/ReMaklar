from pathlib import Path
import io,tarfile
joint=Path('tests/ppc/run_graphics_011_installer_joint.pl').read_text().replace('$leader{$name}=$pid;'*7,'$leader{$name}=$pid;').replace(' last if $exited{$leader{installer}};\n'*7,' last if $exited{$leader{installer}};\n')
joint=joint.replace('my ($name,@args)=@_;my $stem=', '''my ($name,@args)=@_;
 my $guest_argv0=$args[0];$guest_argv0=substr($guest_argv0,length($root)) if index($guest_argv0,"$root/")==0;
 unshift @args,'--exec-argv0',$guest_argv0;
 my $stem=''',1)
Path('tests/ppc/run_graphics_011_installer_guest_paths.pl').write_bytes(joint.encode())
script='''#!/bin/sh
set -eu
out=/var/tmp/graphics011-guestpaths78-results
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/path78.tgz graphics011-guestpaths78-results graphics011-joint78;sync;umount /exchange' 0
export REMAKLAR_OBSERVE_APPKIT=1
export REMAKLAR_OBSERVE_APPKIT_OFFSETS=624e0,1c7758,1c779c,1c7800
export REMAKLAR_TRACE_PATHS=1
perl /var/tmp/graphics011-guestpaths78/joint.pl /var/tmp/graphics011-joint78 /var/tmp/graphics011-build77/qemu-ppc /var/tmp/jaguar
'''
target=Path('build/guestpaths011-78.tgz');assert not target.exists()
with tarfile.open(target,'w:gz') as tar:
 for name,data in [('run.sh',script),('joint.pl',joint)]:
  data=data.replace('\r\n','\n').encode();info=tarfile.TarInfo('graphics011-guestpaths78/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path('build/guest011-guestpaths78.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/path78i.tgz\numount /exchange\nsh /var/tmp/graphics011-guestpaths78/run.sh\n')
