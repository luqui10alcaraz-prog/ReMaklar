#!/usr/bin/env python3
"""Local QEMU user-network file exchange; no external listener.
SPDX-License-Identifier: MIT
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

root = Path(__file__).resolve().parents[1]
uploads = root / 'logs/darwin6'
uploads.mkdir(parents=True, exist_ok=True)

class Exchange(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(root / 'build/darwin-payload'), **kwargs)

    def do_PUT(self):
        name = self.path.removeprefix('/')
        count = int(self.headers.get('Content-Length', '-1'))
        if not name or '/' in name or '\\' in name or name in ('.', '..') or not 0 <= count <= 32 * 1024 * 1024:
            self.send_error(400)
            return
        (uploads / name).write_bytes(self.rfile.read(count))
        self.send_response(201)
        self.end_headers()

HTTPServer(('127.0.0.1', 8081), Exchange).serve_forever()
