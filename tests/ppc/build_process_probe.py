#!/usr/bin/env python3
"""Own raw PPC fork/wait ABI fixture; no cross-compiler or Apple binary edits.
SPDX-License-Identifier: MIT
"""
from pathlib import Path
import struct
import sys

root = Path(__file__).resolve().parents[2]
words, labels, fixups = [], {}, []
def emit(word): words.append(word)
def label(name): labels[name] = len(words)*4
def branch(name, op=0x48000000):
    fixups.append((len(words), name, op));emit(op)
def li(reg, value): emit(0x38000000 | reg<<21 | (value & 65535))
def mr(dst, src): emit(0x7c000378 | src<<21 | dst<<16 | src<<11)
def cmpi(reg, value): emit(0x2c000000 | reg<<16 | (value & 65535))
def cmp(a,b): emit(0x7c000000 | a<<16 | b<<11)
def syscall(n): li(0,n);emit(0x44000002);branch('fail')
def bne(name): branch(name,0x40820000)
def beq(name): branch(name,0x41820000)
emit(0x3fe01000)                         # lis r31,0x1000
emit(0x63ff0800)                         # ori r31,r31,0x800
li(30,42);emit(0x93df0000)               # stw r30,0(r31)
syscall(20);mr(29,3)                     # parent identity
syscall(2)
cmpi(4,1);beq('child')
cmpi(4,0);bne('fail')
cmpi(3,0);beq('fail');mr(28,3)
mr(3,28);emit(0x389f0004);li(5,0);li(6,0) # status at r31+4
syscall(7);cmp(3,28);bne('fail')
emit(0x807f0004);cmpi(3,37<<8);bne('fail')
emit(0x807f0000);cmpi(3,42);bne('fail')    # child's write did not modify parent
mr(3,28);emit(0x389f0004);li(5,0);li(6,0)
li(0,7);emit(0x44000002);branch('nochild') # ECHILD follows error branch
branch('fail')
label('nochild');cmpi(3,10);bne('fail')
li(3,1);emit(0x389f0020);li(5,22);syscall(4)
li(3,0);li(0,1);emit(0x44000002)
label('child')
cmpi(3,0);bne('fail')
li(30,99);emit(0x93df0000)
syscall(39);cmp(3,29);bne('fail')
syscall(20);cmp(3,29);beq('fail');mr(28,3)
syscall(147);cmp(3,28);bne('fail')
li(0,147);emit(0x44000002);branch('sessionerror');branch('fail')
label('sessionerror');cmpi(3,1);bne('fail')
li(3,37);li(0,1);emit(0x44000002)
label('fail');li(3,99);li(0,1);emit(0x44000002)
for index, name, op in fixups:
    delta=labels[name]-index*4
    words[index]=op | (delta & (0x03fffffc if op==0x48000000 else 0xfffc))
header=struct.pack('>7I',0xfeedface,18,0,2,2,56+176,1)
segment=struct.pack('>2I16s8I',1,56,b'__TEXT',0x10000000,4096,0,4096,7,7,0,0)
thread=struct.pack('>4I40I',5,176,1,40,0x10000200,0,*([0]*38))
image=bytearray(4096);image[:len(header+segment+thread)]=header+segment+thread
image[0x200:0x200+len(words)*4]=struct.pack('>'+str(len(words))+'I',*words)
image[0x820:0x836]=b'fork wait COW ABI OK!\n'
out=Path(sys.argv[1]) if len(sys.argv)>1 else root/'build/process-008.macho';out.write_bytes(image);print(out)
