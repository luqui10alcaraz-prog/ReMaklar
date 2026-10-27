"""Validate named-flag ABI and actual tracking event regressions."""
from pathlib import Path
import json,re
root=Path('reports/graphics-011');events={};record={}
for mode,expected in [('n',0),('p',8),('j',0)]:
 base=root/'input136'/(mode+'1');source=base/('graphics011-input136-'+mode+'1')
 assert json.loads((base/'acceptance.json').read_text())['expected_exit']==expected
 status=(source/'probe.status').read_text();assert 'leader_exit=%d\n'%expected in status and 'timeout=0\n' in status
 stdout=(source/'probe.stdout').read_text()
 assert ('real tracking exits=0' if mode=='p' else 'real tracking exits=1') in stdout
 if mode!='p':events[mode]=[re.sub(r'location=-?\d+,-?\d+ ?','',line) for line in stdout.splitlines() if line.startswith('event type=')]
 record[mode]={'exit':expected,'stdout':str(source/'probe.stdout')}
assert events['n']==events['j']
base=root/'build135/export/graphics011-build135-results'
assert (base/'script-status.txt').read_text().strip()=='script_exit=0'
assert 'native compiler EvGlobals ABI' in (base/'unit-bits.stdout').read_text()
record['result']='PASS actual kernel type9/keyboard/move/button/auxiliary sequence native=PPC; previous executor loses tracking event'
record['events_except_location']=events['n'];record['native_compiler_flags_oracle']=str(base/'unit-bits.stdout')
record['pointer_VRAM_proof']='reports/graphics-011/resume-validation/pointer134-framebuffer-verification.json'
out=root/'resume-validation/input136-and-flags46-acceptance.json';assert not out.exists();out.write_text(json.dumps(record,indent=2)+'\n');print(out)
