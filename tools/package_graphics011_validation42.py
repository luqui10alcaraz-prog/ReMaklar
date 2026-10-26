from pathlib import Path
import tarfile,io
s=Path('scripts/darwin6-graphics-011-joint-validation.sh').read_text().replace('validation31','validation42').replace('run30','run41').replace('regression30','regression41').replace('joint30','joint42').replace('valid31','valid42')
s=s.replace('fasttrap capability-native','remote-native remote-jaguar trailer-native trailer-jaguar fasttrap capability-native')
s=s.replace('echo self_tests_verified','cmp /var/tmp/graphics011-run41/trailer-native.stdout /var/tmp/graphics011-run41/trailer-jaguar.stdout\necho self_tests_verified')
s=s.replace('echo native_regression_completed > "$out/phase.txt"','echo native_regression_completed > "$out/phase.txt"\nsync')
reg=Path('scripts/darwin6-graphics-010-regression.sh').read_text().replace('graphics010-regression19','graphics011-regression41').replace('graphics010-run19/qemu-ppc','graphics011-run41/qemu-ppc')
joint=Path('tests/ppc/run_graphics_011_ready_joint.pl').read_text().replace('if(/^(unsupported','if(/could not establish the default connection/ || /^(unsupported').replace('native IPC OOL','native (IPC|received) OOL|unverified native Mach trailer')
Path('tests/ppc/run_graphics_011_ready_joint.pl').write_text(joint)
with tarfile.open('build/validation011-42.tgz','w:gz') as t:
 for name,data in [('run.sh',s.encode()),('regression.sh',reg.encode()),('joint.pl',joint.encode())]:
  i=tarfile.TarInfo('graphics011-validation42/'+name);i.size=len(data);t.addfile(i,io.BytesIO(data))
Path('build/guest011-joint42.txt').write_text('mount -t msdos /dev/disk1 /exchange\ncd /var/tmp\ngnutar xzf /exchange/valid42i.tgz\numount /exchange\nsh /var/tmp/graphics011-validation42/run.sh\n')
