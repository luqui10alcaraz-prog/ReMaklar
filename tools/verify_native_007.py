#!/usr/bin/env python3
"""Validate exported i386 runtime evidence without rerunning guest tests.
SPDX-License-Identifier: MIT
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct


def verify(source):
    expected = {
        'objc': b'OBJC class dispatch super value=42\nOBJC i386 structure and free OK\n',
        'cf': b'CF i386 UTF8 empty nonASCII array retain release time OK\n',
    }
    results = {}
    for name, output in expected.items():
        image = (source/name).read_bytes()
        magic, cpu, subtype, filetype = struct.unpack_from('<4I', image)
        stderr = (source/(name+'.stderr')).read_text()
        command = (source/(name+'.command')).read_text().strip()
        images = re.findall(r'^IMAGE cpu=(\d+) magic=([0-9a-f]+) path=(.*)$', stderr, re.M)
        required = {'./'+name, '/usr/lib/libSystem.B.dylib',
                    '/System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation'}
        if name == 'objc':
            required.add('/usr/lib/libobjc.A.dylib')
        assert (magic, cpu, filetype) == (0xfeedface, 7, 2), (name, 'Mach-O header')
        assert (source/(name+'.status')).read_text().strip() == '0', (name, 'exit')
        assert (source/(name+'.stdout')).read_bytes() == output, (name, 'stdout')
        assert command == 'DIRECT COMMAND: ./'+name, (name, 'command')
        assert images and all(c == '7' and m == 'feedface' for c, m, _ in images)
        assert required <= {p for _, _, p in images}, (name, 'loaded libraries')
        assert re.search(r'^DYLD_MEMORY address=[0-9a-f]+ cpu=7 filetype=7$', stderr, re.M)
        assert 'qemu-ppc' not in stderr and 'probe-main:' not in stderr
        assert 'Mach-O executable i386' in (source/(name+'.images')).read_text()
        results[name] = {'status': 'PASS', 'exit': 0, 'cpu': cpu,
                         'cpusubtype': subtype, 'sha256': hashlib.sha256(image).hexdigest(),
                         'direct_command': command, 'loaded_images': [p for _, _, p in images],
                         'dyld_i386_observed_in_memory': True}
    installed = (source/'installed-images.txt').read_text()
    assert 'current version 262.0.0' in installed
    assert 'current version 218.0.0' in installed
    assert 'current version 60.0.0' in installed
    assert 'qemu-ppc' not in (source/'processes.txt').read_text()
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    results = verify(args.source)
    args.destination.mkdir(exist_ok=False, parents=True)
    # Own caller executables remain in the original exported archive under logs/.
    for p in args.source.iterdir():
        if p.is_file() and p.name not in results:
            shutil.copyfile(p, args.destination/p.name)
    report = {
        'scope': 'Objective-C and CoreFoundation native i386 only',
        'environment': 'Darwin 6.0 RELEASE_I386 under QEMU system x86 TCG',
        'ppc_translation_used': False,
        'results': results,
        'evidence_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in args.destination.iterdir() if p.is_file()},
    }
    (args.destination/'results.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS Objective-C i386; PASS CoreFoundation i386; dyld and loaded images CPU 7')
