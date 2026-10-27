"""Verify saved real-input and descriptor regressions; draw no graphics."""
from pathlib import Path
import hashlib,json,re
root=Path('reports/graphics-011');record={'real_input':{},'dup2':{}}
events={}
for mode,attempt in [('n',2),('p',1),('j',1)]:
 tag=mode+str(attempt);base=root/'input123'/tag
 accepted=json.loads((base/'acceptance.json').read_text());assert accepted['result']=='PASS'
 source=base/('graphics011-input123-'+tag);stdout=(source/'probe.stdout').read_text()
 if mode!='p':
  assert 'letter_a=2' in stdout and 'downs=1 ups=1 auxiliary=2' in stdout and 'changed=1' in stdout
  events[mode]=[re.sub(r'location=-?\d+,-?\d+ ?','',line) for line in stdout.splitlines() if line.startswith('event type=')]
 record['real_input'][tag]={'acceptance':str(base/'acceptance.json'),'stdout_sha256':hashlib.sha256((source/'probe.stdout').read_bytes()).hexdigest()}
assert events['n']==events['j'],(events['n'],events['j'])
record['native_and_PPC_event_sequence_identical_except_initial_location']=events['n']
base=root/'dup131/export/graphics011-dup131-results'
assert (base/'script-status.txt').read_text().strip()=='script_exit=0'
for mode,expected in [('native',0),('previous',125),('jaguar',0)]:
 status=(base/(mode+'.status')).read_text();assert 'leader_exit=%d\n'%expected in status and 'timeout=0\n' in status
assert (base/'native.stdout').read_bytes()==(base/'jaguar.stdout').read_bytes()
record['dup2']={'result':'PASS native/PPC byte-identical output, prior executor exits125','directory':str(base)}
record['native_USB_panic_preserved']='reports/graphics-011/resume-validation/usb121-native-panic-preserved.json'
record['native_preferences_and_registry_names']='reports/graphics-011/setup130/export/graphics011-setup130'
record['kernel_md5']='56da829d60b6b4353c25cca8b060b5f8';record['installer_md5']='1496d181829e74bd60de5fd3f9222185'
out=root/'resume-validation/input123-and-dup131-acceptance.json';assert not out.exists();out.write_text(json.dumps(record,indent=2)+'\n');print(out)
