#!/usr/bin/env python3
"""Exercise real PPC exec above Linux mmap_min_addr, preserving host policy.
Own generated Mach-O code only. SPDX-License-Identifier: MIT
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess

parser=argparse.ArgumentParser()
parser.add_argument('executor',type=Path)
parser.add_argument('new_output',type=Path)
args=parser.parse_args();args.new_output.mkdir(parents=True,exist_ok=False)
root=args.new_output.resolve()
def li(reg,value):return 0x38000000 | reg<<21 | (value&65535)
def make(words):
    h=struct.pack('>7I',0xfeedface,18,0,2,2,232,1)
    segment=struct.pack('>2I16s8I',1,56,b'__TEXT',0x10000000,4096,0,4096,7,7,0,0)
    thread=struct.pack('>4I40I',5,176,1,40,0x10000200,0,*([0]*38))
    data=bytearray(4096);data[:len(h+segment+thread)]=h+segment+thread
    data[0x200:0x200+len(words)*4]=struct.pack('>'+str(len(words))+'I',*words)
    return data
source=make([0x3c601000,0x60630800,0x3c801000,0x60840840,0x3ca01000,0x60a50860,
             li(0,59),0x44000002,li(3,91),li(0,1),0x44000002])
source[0x800:0x808]=b'/target\0'
source[0x840:0x84c]=struct.pack('>3I',0x10000880,0x10000890,0)
source[0x860:0x868]=struct.pack('>2I',0x100008a0,0)
source[0x880:0x886]=b'probe\0';source[0x890:0x896]=b'child\0'
source[0x8a0:0x8aa]=b'EXEC=yes\0\0'
output=b'exec replacement OK\n'
target=make([li(0,4),li(3,1),0x3c801000,0x60840800,li(5,len(output)),0x44000002,
             0x48000010,li(3,23),li(0,1),0x44000002,li(3,92),li(0,1),0x44000002])
target[0x800:0x800+len(output)]=output
for name,image in [('source',source),('target',target)]:
    p=root/name;p.write_bytes(image);p.chmod(0o700)
run=subprocess.Popen([str(args.executor.resolve()),'--root',str(root),str(root/'source')],
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE)
stdout,stderr=run.communicate(timeout=20)
(root/'stdout').write_bytes(stdout);(root/'stderr').write_bytes(stderr)
assert run.returncode==23 and stdout==output,(run.returncode,stdout,stderr[-2000:])
assert ('execve real replacement host_pid=%d'%run.pid).encode() in stderr
result={'status':'PASS','exit':run.returncode,'same_host_pid':run.pid,
        'originals_modified':False,'kernel_mapping_policy_changed':False,
        'generated_images_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['source','target']}}
(root/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS PPC exec replacement with unchanged PID and new original entry')
