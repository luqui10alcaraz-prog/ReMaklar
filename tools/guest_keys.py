#!/usr/bin/env python3
"""Type ASCII into the laboratory guest through QEMU's keyboard device.
SPDX-License-Identifier: MIT
"""
import argparse
from pathlib import Path
import socket
import time

parser = argparse.ArgumentParser()
parser.add_argument('text', nargs='?')
parser.add_argument('--file', type=Path)
parser.add_argument('--delay', type=float, default=.04)
parser.add_argument('--hold-ms', type=int, default=10,
                    help='Key hold duration; use 100 with --delay .3 for slow guests')
args = parser.parse_args()
if not 1 <= args.hold_ms <= 1000 or args.delay < args.hold_ms / 1000:
    parser.error('delay must cover the key hold, and hold-ms must be 1..1000')
text = args.file.read_text() if args.file else args.text
plain = dict(zip(' -=[];\'`,./\\\n', ['spc', 'minus', 'equal', 'bracket_left', 'bracket_right',
    'semicolon', 'apostrophe', 'grave_accent', 'comma', 'dot', 'slash', 'backslash', 'ret']))
shifted = dict(zip('!@#$%^&*()_+{}:"~<>?|', '1234567890-=[];\'`,./\\'))
keys = []
for character in text:
    if character in plain:
        keys.append(plain[character])
    elif character in shifted:
        base = shifted[character]
        keys.append('shift-' + plain.get(base, base))
    elif character.isascii() and character.isupper():
        keys.append('shift-' + character.lower())
    elif character.isascii() and character.isalnum():
        keys.append(character)
    else:
        raise ValueError('Unsupported key: ' + repr(character))

with socket.create_connection(('127.0.0.1', 4444), timeout=5) as connection:
    connection.settimeout(.1)
    for key in keys:
        connection.sendall(('sendkey ' + key + ' ' + str(args.hold_ms) + '\n').encode())
        time.sleep(args.delay)
        try:
            connection.recv(65536)
        except socket.timeout:
            pass
