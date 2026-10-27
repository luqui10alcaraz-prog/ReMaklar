"""Read-only PPC Mach-O / Objective-C 1 inspection for original Jaguar files."""
from pathlib import Path
import argparse, bisect, json, re, struct, sys

class MachO:
    def __init__(self, path):
        self.path = Path(path); b = self.path.read_bytes()
        if b[:4] == b'\xca\xfe\xba\xbe':
            for i in range(struct.unpack_from('>I', b, 4)[0]):
                cpu, sub, off, size, align = struct.unpack_from('>5I', b, 8 + 20*i)
                if cpu == 18:
                    b = b[off:off+size]; break
        assert b[:4] == b'\xfe\xed\xfa\xce'
        self.b = b; self.sections = []; self.segments = []; self.symbols = []; self.methods = []
        pos = 28
        for i in range(struct.unpack_from('>I', b, 16)[0]):
            cmd, size = struct.unpack_from('>II', b, pos)
            if cmd == 1:
                name = b[pos+8:pos+24].split(b'\0')[0].decode()
                vm, vs, fo, fs, mp, ip, ns, flags = struct.unpack_from('>8I', b, pos+24)
                self.segments.append((name, vm, vs, fo, fs))
                for j in range(ns):
                    p = pos+56+68*j
                    sn, sg = [b[p+k:p+k+16].split(b'\0')[0].decode() for k in (0,16)]
                    addr, length, offset = struct.unpack_from('>3I', b, p+32)
                    self.sections.append((sg, sn, addr, length, offset))
            if cmd == 2:
                so, count, st, ss = struct.unpack_from('>4I', b, pos+8)
                for j in range(count):
                    ix, ty, sc, de, val = struct.unpack_from('>IBBHI', b, so+j*12)
                    if val and ix < ss:
                        self.symbols.append((val, b[st+ix:b.find(b'\0',st+ix)].decode(errors='replace')))
            pos += size
        self.symbols.sort()
        for sg, sn, addr, length, offset in self.sections:
            if sn not in ('__inst_meth', '__cls_meth', '__cat_inst_meth', '__cat_cls_meth'):
                continue
            p = offset
            while p+8 <= offset+length:
                count = struct.unpack_from('>I', b, p+4)[0]
                if not 0 < count < 20000 or p+8+12*count > offset+length:
                    p += 4; continue
                for j in range(count):
                    name, typ, imp = struct.unpack_from('>3I', b, p+8+j*12)
                    self.methods.append((imp, self.string(name), self.string(typ)))
                p += 8+12*count
        self.methods.sort()
    def offset(self, address):
        for name, vm, vs, fo, fs in self.segments:
            if vm <= address < vm+fs: return fo+address-vm
        raise ValueError('Unbacked address %x' % address)
    def data(self, address, length):
        offset = self.offset(address); return self.b[offset:offset+length]
    def u32(self, address): return struct.unpack('>I', self.data(address,4))[0]
    def string(self, address):
        try:
            offset = self.offset(address); end = self.b.find(b'\0',offset)
            return self.b[offset:end].decode(errors='replace')
        except ValueError: return '?%x' % address
    def describe(self, address):
        all_syms = sorted(self.symbols + [(v, '-['+name+']') for v,name,typ in self.methods])
        index = bisect.bisect_right([v for v,n in all_syms], address)-1
        return all_syms[index][1]+'+'+hex(address-all_syms[index][0]) if index>=0 else ''

def main():
    p=argparse.ArgumentParser();p.add_argument('file',type=Path)
    p.add_argument('--methods');p.add_argument('--symbols');p.add_argument('--strings')
    p.add_argument('--disasm',type=lambda x:int(x,0));p.add_argument('--size',type=lambda x:int(x,0),default=0x300)
    p.add_argument('--sections',action='store_true');a=p.parse_args();m=MachO(a.file)
    if a.sections:
        for sg,sn,va,sz,off in m.sections: print('%s %s va=%08x size=%x offset=%x'%(sg,sn,va,sz,off))
    if a.methods:
        for v,n,t in m.methods:
            if re.search(a.methods,n,re.I): print('%08x %s %s'%(v,n,t))
    if a.symbols:
        for v,n in m.symbols:
            if re.search(a.symbols,n,re.I): print('%08x %s'%(v,n))
    if a.strings:
        for sg,sn,va,sz,off in m.sections:
            if sn not in ('__cstring','__meth_var_names','__class_names'): continue
            for match in re.finditer(rb'[^\0]{3,}',m.b[off:off+sz]):
                text=match.group().decode(errors='replace')
                if re.search(a.strings,text,re.I):print('%08x %s %s'%(va+match.start(),sn,text))
    if a.disasm is not None:
        sys.path.insert(0,'build/python-tools');from capstone import Cs,CS_ARCH_PPC,CS_MODE_32,CS_MODE_BIG_ENDIAN
        md=Cs(CS_ARCH_PPC,CS_MODE_32|CS_MODE_BIG_ENDIAN)
        for ins in md.disasm(m.data(a.disasm,a.size),a.disasm):
            extra=''
            if ins.mnemonic.startswith('b') and ins.op_str.startswith('0x'):
                extra=m.describe(int(ins.op_str,16))
            print('%08x %-8s %-30s %s'%(ins.address,ins.mnemonic,ins.op_str,extra))

if __name__=='__main__':main()
