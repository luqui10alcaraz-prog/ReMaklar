#!/usr/bin/env python3
"""Own high-address PPC signal/frame fixture, real host kill, no Apple binaries.
SPDX-License-Identifier: MIT
"""
from pathlib import Path
import struct,sys
words=[];labels={};fix=[]
def emit(n):words.append(n)
def li(r,n):emit(0x38000000|r<<21|(n&65535))
def mr(d,s):emit(0x7c000378|s<<21|d<<16|s<<11)
def label(n):labels[n]=len(words)*4
def branch(n,op=0x48000000):fix.append((len(words),n,op));emit(op)
def cmp(r,n):emit(0x2c000000|r<<16|(n&65535))
def ne(n):branch(n,0x40820000)
def sc(n):li(0,n);emit(0x44000002);branch('fail')
# r31 = data, r14 tests whole-context restoration by sigreturn.
emit(0x3fe01000);emit(0x63ff0800);li(14,42)
li(3,30);mr(4,31);li(5,0);sc(46)
if '--external' in sys.argv:
    label('spin');emit(0x807f0020);cmp(3,0);branch('spin',0x41820000)
else:
    sc(20);li(4,30);sc(37)
cmp(14,42);ne('fail');emit(0x807f0020);cmp(3,1);ne('fail')
li(3,1);emit(0x389f0040);li(5,26);sc(4);li(3,0);li(0,1);emit(0x44000002)
label('fail');li(3,99);li(0,1);emit(0x44000002)
while len(words)*4<0x180:emit(0)
label('tramp');mr(20,7);mr(12,3);emit(0x7d8903a6);mr(3,5);emit(0x4e800421)
mr(3,20);li(0,103);emit(0x44000002);branch('fail')
while len(words)*4<0x200:emit(0)
label('handler');cmp(3,30);ne('fail');li(14,99);emit(0x807f0020);emit(0x38630001);emit(0x907f0020);emit(0x4e800020)
for i,n,op in fix:words[i]=op|((labels[n]-i*4)&(0x03fffffc if op==0x48000000 else 0xfffc))
h=struct.pack('>7I',0xfeedface,18,0,2,2,232,1)
s=struct.pack('>2I16s8I',1,56,b'__TEXT',0x10000000,4096,0,4096,7,7,0,0)
t=struct.pack('>4I40I',5,176,1,40,0x10000200,0,*([0]*38))
b=bytearray(4096);b[:len(h+s+t)]=h+s+t;b[0x200:0x200+len(words)*4]=struct.pack('>'+str(len(words))+'I',*words)
b[0x800:0x810]=struct.pack('>4I',0x10000200+labels['handler'],0x10000200+labels['tramp'],0,0)
message=b'real PPC signal return OK\n';assert len(message)==26;b[0x840:0x85a]=message
p=Path(sys.argv[1]);p.write_bytes(b)
