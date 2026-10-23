#!/usr/bin/env python3
"""Generate tiny original test fixtures, NOT Apple/Jaguar binaries.
SPDX-License-Identifier: MIT. Instructions are PPC32; syscall ABI is Darwin.
"""
import hashlib
import json
import struct
from pathlib import Path

BASE, CODE, MESSAGE = 0x10000000, 0x200, 0x800


def li(reg, val):
    return 0x38000000 | reg << 21 | (val & 0xffff)


def image(words):
    header = struct.pack('>7I', 0xfeedface, 18, 0, 2, 2, 56 + 176, 1)
    segment = struct.pack('>2I16s8I', 1, 56, b'__TEXT', BASE, 4096, 0, 4096, 7, 5, 0, 0)
    state = [BASE + CODE, 0] + [0] * 38
    thread = struct.pack('>4I40I', 5, 176, 1, 40, *state)
    data = bytearray(4096)
    data[:len(header + segment + thread)] = header + segment + thread
    data[CODE:CODE + 4 * len(words)] = struct.pack('>' + 'I' * len(words), *words)
    data[MESSAGE:MESSAGE + len(b'ReMaklar PPC -> Intel\n')] = b'ReMaklar PPC -> Intel\n'
    return bytes(data)


def fixtures():
    sc = 0x44000002
    yield 'exit42', [li(3, 42), li(0, 1), sc], 42, b''
    # Darwin resumes at the branch on error, skips it on successful write.
    text = b'ReMaklar PPC -> Intel\n'
    yield 'write', [li(0, 4), li(3, 1), 0x3c801000, 0x60840800, li(5, len(text)), sc,
                    0x48000014, 0x2c030000 | len(text), 0x4082000c,
                    li(3, 0), 0x48000008, li(3, 91), li(0, 1), sc], 0, text
    # EBADF is 9 on Darwin. A success return is deliberately a test failure.
    yield 'write-ebadf', [li(0, 4), li(3, -1), 0x3c801000, 0x60840800, li(5, 1), sc,
                          0x48000010, li(3, 92), li(0, 1), sc,
                          0x2c030009, 0x4082000c, li(3, 0), 0x48000008,
                          li(3, 93), li(0, 1), sc], 0, b''
    yield 'write-efault', [li(0, 4), li(3, 1), li(4, 0), li(5, 1), sc,
                           0x48000010, li(3, 92), li(0, 1), sc,
                           0x2c03000e, 0x4082000c, li(3, 0), 0x48000008,
                           li(3, 93), li(0, 1), sc], 0, b''
    # lwz reads big-endian data from the message, checks its first word 'ReMa'.
    yield 'load-be', [0x3c801000, 0x80840800, 0x3ca05265, 0x60a54d61,
                       0x7c042800, 0x4082000c, li(3, 0), 0x48000008,
                       li(3, 94), li(0, 1), sc], 0, b''
    yield 'unsupported-syscall', [li(0, 999), sc], 125, b''
    yield 'illegal-instruction', [0], 125, b''
    yield 'memory-fault', [0x80600000, li(0, 1), sc], 125, b''


def main():
    out = Path(__file__).resolve().parents[2] / 'build' / 'fixtures'
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    checks = {'write': 'return r3=22 error=0', 'write-ebadf': 'return r3=9 error=9',
              'write-efault': 'return r3=14 error=14',
              'unsupported-syscall': 'unsupported Darwin syscall/trap 999',
              'illegal-instruction': 'unsupported PPC exception',
              'memory-fault': 'unsupported PPC exception'}
    for name, words, status, stdout in fixtures():
        data = image(words)
        (out / (name + '.macho')).write_bytes(data)
        manifest.append({'name': name, 'exit': status, 'stdout': stdout.decode(),
                         'stderr_contains': checks.get(name, 'loaded entry='),
                         'sha256': hashlib.sha256(data).hexdigest()})
    (out / 'truncated.macho').write_bytes(b'\xfe\xed\xfa\xce')
    manifest.append({'name': 'truncated', 'exit': 125, 'stdout': '',
                     'stderr_contains': 'truncated Mach-O header'})
    bad = bytearray(image([li(0, 1), li(3, 0), 0x44000002]))
    struct.pack_into('>I', bad, 32, 0)
    (out / 'bad-command.macho').write_bytes(bad)
    manifest.append({'name': 'bad-command', 'exit': 125, 'stdout': '',
                     'stderr_contains': 'invalid load command size'})
    dynamic = bytearray(image([li(0, 1), li(3, 0), 0x44000002]))
    dylinker = struct.pack('>3I', 0xe, 28, 12) + b'/usr/lib/dyld\0\0\0'
    struct.pack_into('>2I', dynamic, 16, 3, 56 + 176 + len(dylinker))
    dynamic[28 + 56 + 176:28 + 56 + 176 + len(dylinker)] = dylinker
    (out / 'needs-dyld.macho').write_bytes(dynamic)
    manifest.append({'name': 'needs-dyld', 'exit': 125, 'stdout': '',
                     'stderr_contains': 'unimplemented dyld integration'})
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
