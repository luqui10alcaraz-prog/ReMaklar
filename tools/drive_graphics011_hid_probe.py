"""Deliver actual emulated keyboard input only after the real probe is READY."""
from pathlib import Path
import argparse,json,subprocess,sys,time
p=argparse.ArgumentParser();p.add_argument('--port',type=int,required=True);p.add_argument('--fat',required=True,type=Path);p.add_argument('--mode',choices=('n','p','j'),required=True);p.add_argument('--attempt',type=int,required=True);p.add_argument('--trial',type=int,default=110);p.add_argument('--mouse',action='store_true');p.add_argument('--tracking',action='store_true');p.add_argument('--negative-exit',type=int,choices=(8,125),default=125);a=p.parse_args()
assert 0<a.attempt<100
assert a.trial>=110
tag=a.mode+str(a.attempt);out=Path('reports/graphics-011/input%d'%a.trial)/tag;out.mkdir(parents=True,exist_ok=False)
guest=Path('build/guest011-input%d-'%a.trial+tag+'.txt');guest.write_text('sh /var/tmp/graphics011-stage%d/run.sh %s %d\n'%(a.trial,a.mode,a.attempt))
subprocess.run([sys.executable,'tools/guest_keys.py','--port',str(a.port),'--file',str(guest),'--delay','.05'],check=True,timeout=15)
deadline=time.monotonic()+55;ready=False;finished=False
for i in range(30):
 if time.monotonic()>deadline:break
 sample=out/('sample%02d'%i)
 subprocess.run([sys.executable,'tools/inspect_graphics011_live.py',str(sample),'--port',str(a.port),'--logs','--tail-bytes','2400'],check=True,capture_output=True,timeout=15)
 rows=json.loads((sample/'processes.json').read_text())
 if not ready:
  for row in rows:
   if row['comm'] not in ('qemu-ppc','hid-i386'):continue
   stdout=sample/('%d-fd1.txt'%row['pid'])
   if stdout.exists():
    text=stdout.read_text(errors='replace')
    if 'READY real hardware input' in text and 'DONE keys=' not in text:
     (out/'ready-evidence.json').write_text(json.dumps({'pid':row['pid'],'file':str(stdout),'text':text},indent=2)+'\n')
     subprocess.run([sys.executable,'tools/qemu_monitor.py','--port',str(a.port),'sendkey a 20'],check=True,timeout=5)
     if a.mouse:
      for command in ('mouse_move 10 5','mouse_button 1','mouse_move 1 0','mouse_button 0','mouse_move 1 0'):
       subprocess.run([sys.executable,'tools/qemu_monitor.py','--port',str(a.port),command],check=True,timeout=5)
       time.sleep(.15)
     ready=True;print('Real probe READY, actual hardware input sent to PID',row['pid'],flush=True);break
 if (ready or i>0) and all(row['pid'] in (0,1,2,22) for row in rows):finished=True;break
 time.sleep(1)
if not finished:
 subprocess.run([sys.executable,'tools/qemu_monitor.py','--port',str(a.port),'stop'],timeout=5)
 raise RuntimeError('Probe did not complete within 55 seconds; VM stopped, samples preserved')
archive=out/('input%d-'%a.trial+tag+'.tgz')
subprocess.run(['mcopy','-i',str(a.fat),'::/RUNS/input%d-'%a.trial+tag+'.tgz',str(archive)],check=True,timeout=10)
subprocess.run(['tar','-xzf',str(archive),'-C',str(out)],check=True,timeout=10)
results=out/('graphics011-input%d-'%a.trial+tag)
status=(results/'probe.status').read_text();script_status=(results/'script-status.txt').read_text()
stdout=(results/'probe.stdout').read_text();stderr=(results/'probe.stderr').read_text()
print(stdout,flush=True);print(status,flush=True)
expected=a.negative_exit if a.mode=='p' else 0
assert 'leader_exit=%d\n'%expected in status and 'timeout=0\n' in status,status
assert script_status.strip()=='script_exit=0',script_status
if a.mode=='p':
 if expected==125:assert 'unverified live shared field kind=2' in stderr
 else:assert 'real tracking exits=0' in stdout
else:assert 'key=0 char=97 orig=97 repeat=0 keyboardType=1' in stdout and 'letter_a=2' in stdout
if a.mouse and a.mode!='p':
 assert 'real pointer movement initial=' in stdout and 'changed=1' in stdout
 assert all('event type=%d '%kind in stdout for kind in (1,2,5,14)),stdout
 assert 'auxiliary delta=1 buttons=1' in stdout and 'auxiliary delta=1 buttons=0' in stdout,stdout
if a.tracking and a.mode!='p':assert 'event type=9 ' in stdout and 'real tracking exits=1' in stdout
if 'consumed-null bytes=' in stdout and a.mode!='p':assert 'real consumed key null payloads=2' in stdout
(out/'acceptance.json').write_text(json.dumps({'result':'PASS','mode':a.mode,'attempt':a.attempt,'ready_observed':ready,'emulated_input':'PS/2 keyboard key a and selected QEMU mouse movement/complete click' if a.mouse else 'PS/2 keyboard key a, actual kernel IOHID event','expected_exit':expected,'source_results':str(results)},indent=2)+'\n')
print('PASS actual native-kernel HID input:',tag,flush=True)
