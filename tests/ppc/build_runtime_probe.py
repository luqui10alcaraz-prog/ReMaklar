#!/usr/bin/env python3
"""Own dynamic PPC Mach-O with eager symbol pointers; original dyld binds APIs.
SPDX-License-Identifier: MIT
"""
from pathlib import Path
import struct
import subprocess
root=Path(__file__).resolve().parents[2]; out=root/'build/objc-probe';out.mkdir(exist_ok=True)
subprocess.run(['powerpc-linux-gnu-as','-mppc','-o',str(out/'probe.o'),str(root/'tests/ppc/runtime-loader-probe.S')],check=True)
subprocess.run(['powerpc-linux-gnu-ld','-Ttext=0x10000400','-e','_start','-o',str(out/'probe.elf'),str(out/'probe.o')],check=True)
subprocess.run(['powerpc-linux-gnu-objcopy','-O','binary','-j','.text',str(out/'probe.elf'),str(out/'probe.bin')],check=True)
pack=lambda *v:struct.pack('>'+len(v)*'I',*v)
def segment(name,addr,off,prot,sections=b''):
    return struct.pack('>2I16s8I',1,56+len(sections),name,addr,4096,off,4096,7,prot,len(sections)//68,0)+sections
def section(name,segment,addr,size,off,flags=0):
    return struct.pack('>16s16s9I',name,segment,addr,size,off,2,0,0,flags,0,0)
def load(cmd,name):
    start=12 if cmd==14 else 24; size=(start+len(name)+1+3)&~3
    return pack(cmd,size,start)+ (pack(0,0,0) if cmd==12 else b'') +name+b'\0'*(size-start-len(name))
code=(out/'probe.bin').read_bytes(); assert len(code)<2048
commands=[segment(b'__TEXT',0x10000000,0,5,section(b'__text',b'__TEXT',0x10000400,len(code),0x400)),
          segment(b'__DATA',0x10001000,4096,3,section(b'__nl_symbol_ptr',b'__DATA',0x10001000,24,4096,6)),
          segment(b'__LINKEDIT',0x10002000,8192,1),
          load(14,b'/usr/lib/dyld'),load(12,b'/usr/lib/libSystem.B.dylib'),load(12,b'/usr/lib/libobjc.A.dylib'),
          pack(5,176,1,40,0x10000400,0,*([0]*38)),pack(2,24,8192,6,8192+72,192)]
fields=[0]*18;fields[4]=0;fields[5]=6;fields[12]=8192+264;fields[13]=6
commands.append(pack(11,80,*fields))
blob=b''.join(commands);assert 28+len(blob)<=0x400
image=bytearray(12288); image[:28+len(blob)]=pack(0xfeedface,18,0,2,len(commands),len(blob),0x84)+blob
image[0x400:0x400+len(code)]=code
strings=b'\0';symbols=b''
for name,ordinal in [(b'_objc_getClass',2),(b'_sel_registerName',2),(b'_objc_msgSend',2),
                     (b'_mach_init',1),(b'__cthread_init_routine',1),(b'__objcInit',2)]:
    symbols+=struct.pack('>IBBhI',len(strings),1,0,ordinal<<8,0);strings+=name+b'\0'
assert len(strings)<=192
image[8192:8192+72]=symbols;image[8192+72:8192+72+len(strings)]=strings
image[8192+264:8192+288]=pack(0,1,2,3,4,5)
(root/'build/objc-runtime-probe.macho').write_bytes(image)
