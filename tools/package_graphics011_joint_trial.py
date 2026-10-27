"""Prepare a numbered bounded trial without mutating historical generators."""
import argparse,io,tarfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('trial',type=int);p.add_argument('--executor',required=True);p.add_argument('--observe',action='store_true');args=p.parse_args()
assert args.trial>=69 and args.executor.startswith('/var/tmp/') and '"' not in args.executor
n=args.trial;out=f'/var/tmp/graphics011-trial{n}-results'
script=f'''#!/bin/sh
set -eu
out={out}
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
trap 'status=$?;echo script_exit=$status > "$out/script-status.txt";sync;mount -t msdos /dev/disk1 /exchange;cd /var/tmp;gnutar czf /exchange/trial{n}.tgz graphics011-trial{n}-results graphics011-joint{n};sync;umount /exchange' 0
'''
if args.observe:script+='export REMAKLAR_OBSERVE_APPKIT=1\n'
script+=f'perl /var/tmp/graphics011-trial{n}/joint.pl /var/tmp/graphics011-joint{n} "{args.executor}" /var/tmp/jaguar\n'
joint=Path('tests/ppc/run_graphics_011_installer_joint.pl').read_text()
joint=joint.replace('$leader{$name}=$pid;'*7,'$leader{$name}=$pid;').replace(' last if $exited{$leader{installer}};\n'*7,' last if $exited{$leader{installer}};\n')
target=Path(f'build/trial011-{n}.tgz');assert not target.exists()
with tarfile.open(target,'w:gz') as tar:
 for name,data in [('run.sh',script),('joint.pl',joint)]:
  data=data.replace('\r\n','\n').encode();info=tarfile.TarInfo(f'graphics011-trial{n}/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
Path(f'build/guest011-trial{n}.txt').write_text(f'mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/tr{n}i.tgz\numount /exchange\nsh /var/tmp/graphics011-trial{n}/run.sh\n')
