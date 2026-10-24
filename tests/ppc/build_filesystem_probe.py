#!/usr/bin/env python3
"""Package own PPC assembly as Mach-O. Uses existing host cross-binutils only.
SPDX-License-Identifier: MIT
"""
from pathlib import Path
import struct
import subprocess
root = Path(__file__).resolve().parents[2]
out = root/'build/fs-probe'
out.mkdir(exist_ok=True)
subprocess.run(['powerpc-linux-gnu-as','-mppc','-o',str(out/'probe.o'),str(root/'tests/ppc/filesystem-probe.S')],check=True)
subprocess.run(['powerpc-linux-gnu-ld','-Ttext=0x10000200','-e','_start','-o',str(out/'probe.elf'),str(out/'probe.o')],check=True)
subprocess.run(['powerpc-linux-gnu-objcopy','-O','binary','-j','.text',str(out/'probe.elf'),str(out/'probe.bin')],check=True)
code = (out/'probe.bin').read_bytes()
size = (0x200+len(code)+4095)&~4095
header = struct.pack('>7I',0xfeedface,18,0,2,2,56+176,1)
segment = struct.pack('>2I16s8I',1,56,b'__TEXT',0x10000000,size,0,size,7,7,0,0)
thread = struct.pack('>4I40I',5,176,1,40,0x10000200,0,*([0]*38))
image = bytearray(size); image[:len(header+segment+thread)] = header+segment+thread
image[0x200:0x200+len(code)] = code
(root/'build/filesystem-probe.macho').write_bytes(image)
