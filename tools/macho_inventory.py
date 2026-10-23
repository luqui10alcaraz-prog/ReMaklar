#!/usr/bin/env python3
"""Read-only Mach-O32/FAT inventory; no third-party dependencies.

ReMaklar project tooling. SPDX-License-Identifier: MIT
Reports wire data; does not claim source/binary identity.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def inventory(data):
    def unpack(fmt, off):
        return struct.unpack_from(fmt, data, off)
    magic = data[:4]
    if magic == b'\xca\xfe\xba\xbe':
        count, = unpack('>I', 4)
        if count > 32:
            raise ValueError('too many FAT slices')
        slices = []
        for i in range(count):
            cpu, subtype, off, size, align = unpack('>5I', 8 + i * 20)
            if off + size > len(data):
                raise ValueError('slice outside file')
            slices.append({'offset': off, 'size': size, 'cputype': cpu,
                           'analysis': inventory(data[off:off + size])})
        return {'format': 'FAT', 'sha256': hashlib.sha256(data).hexdigest(), 'slices': slices}
    endian = {b'\xfe\xed\xfa\xce': '>', b'\xce\xfa\xed\xfe': '<'}.get(magic)
    if endian is None:
        raise ValueError('not a supported Mach-O32/FAT image')
    _, cpu, subtype, kind, count, size, flags = unpack(endian + '7I', 0)
    if 28 + size > len(data) or count > size // 8:
        raise ValueError('invalid load command region')
    report = {'format': 'Mach-O32', 'sha256': hashlib.sha256(data).hexdigest(),
              'cputype': cpu, 'cpusubtype': subtype, 'filetype': kind,
              'flags': flags, 'segments': [], 'sections': [], 'dependencies': [],
              'symbols': [], 'stubs': [], 'entry': None}
    symtab = dysymtab = None
    off = 28
    for _ in range(count):
        cmd, length = unpack(endian + '2I', off)
        if length < 8 or off + length > 28 + size:
            raise ValueError('invalid load command size')
        if cmd == 1:
            fields = unpack(endian + '2I16s8I', off)
            _, _, name, vm, vmsize, fileoff, filesize, maxprot, prot, nsects, segflags = fields
            report['segments'].append({'name': name.rstrip(b'\0').decode(), 'vmaddr': vm,
                                       'vmsize': vmsize, 'fileoff': fileoff, 'filesize': filesize})
            for i in range(nsects):
                fields = unpack(endian + '16s16s9I', off + 56 + i * 68)
                sn, sg, addr, nbytes, foff, align, reloff, nreloc, fl, r1, r2 = fields
                report['sections'].append({'name': sn.rstrip(b'\0').decode(), 'addr': addr,
                    'size': nbytes, 'fileoff': foff, 'flags': fl, 'reserved1': r1, 'reserved2': r2})
        elif cmd == 2:
            symtab = unpack(endian + '4I', off + 8)
        elif cmd == 0xb:
            dysymtab = unpack(endian + '18I', off + 8)
        elif cmd in (0xc, 0xe):
            noff, = unpack(endian + 'I', off + 8)
            if noff >= length:
                raise ValueError('invalid library name')
            name = data[off + noff:off + length].split(b'\0')[0].decode()
            report['dependencies'].append({'kind': 'dyld' if cmd == 0xe else 'dylib', 'path': name})
        elif cmd in (4, 5) and cpu == 18:
            flavor, nwords = unpack(endian + '2I', off + 8)
            if flavor == 1 and nwords >= 40 and length >= 176:
                report['entry'], = unpack(endian + 'I', off + 16)
        off += length
    if symtab:
        so, ns, stro, strs = symtab
        strings = data[stro:stro + strs]
        for i in range(ns):
            index, stype, sect, desc, val = unpack(endian + 'IBBhI', so + 12 * i)
            name = strings[index:].split(b'\0')[0].decode(errors='replace')
            report['symbols'].append({'index': i, 'name': name, 'type': stype, 'value': val})
    if dysymtab:
        indoff, indcount = dysymtab[12:14]
        for section in report['sections']:
            if section['flags'] & 0xff != 8 or not section['reserved2']:
                continue
            for i in range(section['size'] // section['reserved2']):
                idx = section['reserved1'] + i
                if idx >= indcount:
                    raise ValueError('stub outside indirect symbol table')
                symidx, = unpack(endian + 'I', indoff + 4 * idx)
                if symidx < len(report['symbols']):
                    report['stubs'].append({'address': section['addr'] + i * section['reserved2'],
                                           'symbol': report['symbols'][symidx]['name']})
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file', type=Path)
    ap.add_argument('--extract-ppc', type=Path)
    args = ap.parse_args()
    data = args.file.read_bytes()
    report = inventory(data)
    if args.extract_ppc:
        ppc = next(s for s in report['slices'] if s['cputype'] == 18)
        args.extract_ppc.parent.mkdir(parents=True, exist_ok=True)
        args.extract_ppc.write_bytes(data[ppc['offset']:ppc['offset'] + ppc['size']])
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
