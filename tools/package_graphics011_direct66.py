from pathlib import Path
import tarfile,io
joint=Path('tests/ppc/run_graphics_011_installer_joint.pl').read_text()
joint=joint.replace('my %owned;my @stems;','my(%owned,%leader,%exited);my @stems;').replace('$owned{$pid}=1;','$owned{$pid}=1;$leader{$name}=$pid;',1).replace('if($w==$pid){open STATUS','if($w==$pid){$exited{$pid}=1;open STATUS',1)
joint=joint.replace('for(1..42){sleep 5;sample();','for(1..42){sleep 5;sample();\n last if $exited{$leader{installer}};')
joint=joint.replace('if(/could not establish the default connection','if(/^unsupported |^unverified |^invalid / || /could not establish the default connection')
Path('tests/ppc/run_graphics_011_installer_joint.pl').write_text(joint)
s='''#!/bin/sh
set -eu
p=/var/tmp/graphics011-direct66
out=/var/tmp/graphics011-direct66-results
exe=/var/tmp/graphics011-run65/qemu-ppc
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/direct66.tgz graphics011-direct66-results graphics011-joint66;sync;umount /exchange' 0
for name in vmcopy-native vmcopy-jaguar rename-native rename-jaguar fcntl-native fcntl-jaguar taskthreads-native taskthreads-jaguar priority-native priority-jaguar forkio-native forkio-jaguar kinfo-native kinfo-jaguar ool-native ool-jaguar remoteio-native remoteio-jaguar remote-native remote-jaguar shared-native shared-jaguar high-native high-jaguar threads timer-native timer-jaguar fasttrap capability-native capability-jaguar trailer-native trailer-jaguar typed-native;do
 grep -q '^leader_exit=0$' "/var/tmp/graphics011-run65/$name.status"
 grep -q '^timeout=0$' "/var/tmp/graphics011-run65/$name.status"
done
perl "$p/joint.pl" /var/tmp/graphics011-joint66 "$exe" /var/tmp/jaguar
echo joint_trial_completed > "$out/phase.txt"
'''
with tarfile.open('build/direct011-66.tgz','w:gz') as t:
 for name,data in [('run.sh',s.encode()),('joint.pl',joint.encode())]:
  data=data.replace(b'\r\n',b'\n');i=tarfile.TarInfo('graphics011-direct66/'+name);i.size=len(data);t.addfile(i,io.BytesIO(data))
Path('build/guest011-direct66.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/direct66i.tgz\numount /exchange\nsh /var/tmp/graphics011-direct66/run.sh\n')
