#!/usr/bin/env python3
"""Shared byte-exact vectors for Linux and Darwin's stock Perl 5.
SPDX-License-Identifier: MIT
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from macho_inventory import inventory

root = Path(__file__).resolve().parents[2]
guest = root / 'research/samples-local'
files = guest / 'fixtures'
files.mkdir(exist_ok=True)
text = b'first line\nsecond line\n'
binary = bytes(range(256)) * 513
for name, data in [('empty', b''), ('text', text), ('space name', b'a b\t c\n'), ('large', binary)]:
    (files / name).write_bytes(data)
cases = []
def case(name, program, args, output, stdin=b'', status=0, diagnostic=b''):
    cases.append((name, program, status, stdin, output, diagnostic, args))
for name, args in [
    ('none', []), ('empty', ['']), ('multiple', ['one', 'two', 'three']),
    ('empty-between', ['', 'one', '', 'two', '']),
    ('spaces', ['  leading', 'a  b', 'trailing  ']),
    ('literal', ['*', '$HOME', "'quotes'", '"double"', '\\n']),
    ('controls', ['a\tb', 'c\nd']), ('utf8', ['Jaguar: ñ á 雪']),
    ('long', ['x' * 32768]), ('many', ['arg%03d' % i for i in range(513)]),
    ('long-many', ['y' * 8192] * 5),
]:
    case('echo-' + name, 'echo', args, (' '.join(args) + '\n').encode())
case('echo-no-newline', 'echo', ['-n', 'a', '', 'b'], b'a  b')
case('cat-stdin-empty', 'cat', [], b'')
case('cat-stdin-binary', 'cat', [], binary, binary)
case('cat-file-empty', 'cat', ['/fixtures/empty'], b'')
case('cat-file-text', 'cat', ['/fixtures/text'], text)
case('cat-file-spaces', 'cat', ['/fixtures/space name'], b'a b\t c\n')
case('cat-files', 'cat', ['/fixtures/text', '/fixtures/empty', '/fixtures/space name'], text + b'a b\t c\n')
case('cat-file-large', 'cat', ['/fixtures/large'], binary)
case('cat-mixed-stdin', 'cat', ['/fixtures/text', '-', '/fixtures/text'], text + b'STDIN\x00\n' + text, b'STDIN\x00\n')
case('cat-missing', 'cat', ['/fixtures/absent'], b'', status=1, diagnostic=b'No such file or directory')
case('cat-missing-continues', 'cat', ['/fixtures/absent', '/fixtures/text'], text,
     status=1, diagnostic=b'No such file or directory')
case('cat-number', 'cat', ['-n', '/fixtures/text'], b'     1\tfirst line\n     2\tsecond line\n')
entries = {}
for name in ['echo', 'cat']:
    parsed = inventory((guest / 'bin' / name).read_bytes())
    entries[name] = next(s['analysis']['entry'] for s in parsed['slices'] if s['cputype'] == 18)
def hx(value):
    if isinstance(value, str): value = value.encode()
    return value.hex() or '-'
dest = root / 'build/utility-cases.tsv'
with dest.open('w', encoding='ascii', newline='\n') as out:
    for name, program, status, stdin, output, diagnostic, args in cases:
        fields = [name, program, str(status), '%08x' % entries[program], hx(stdin), hx(output), hx(diagnostic)]
        fields.extend(hx(arg) for arg in args)
        out.write('\t'.join(fields) + '\n')
print('%d shared cases -> %s' % (len(cases), dest))
