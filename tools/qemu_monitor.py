#!/usr/bin/env python3
"""Operate the localhost-only laboratory QEMU HMP monitor.
SPDX-License-Identifier: MIT
"""
import argparse
import socket
import time

parser = argparse.ArgumentParser()
parser.add_argument('command')
parser.add_argument('--port', type=int, default=4444)
args = parser.parse_args()
with socket.create_connection(('127.0.0.1', args.port), timeout=5) as connection:
    connection.settimeout(5)
    greeting = b''
    while not greeting.endswith(b'(qemu) '):
        greeting += connection.recv(4096)
    connection.sendall((args.command + '\n').encode('ascii'))
    chunks = []
    while True:
        try:
            chunk = connection.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
            if b''.join(chunks).endswith(b'(qemu) '):
                break
        except (socket.timeout, ConnectionResetError):
            break
    # HMP echoes each keystroke using ANSI edits; show only the result lines.
    output = b''.join(chunks).decode(errors='replace').split('\r\n')
    print('\n'.join(line for line in output if '\x1b' not in line).strip())
