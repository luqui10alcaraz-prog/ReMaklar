#!/usr/bin/env python3
"""Inventory runtime dependencies from the extracted Apple files.
SPDX-License-Identifier: MIT"""
import json
from pathlib import Path
from macho_inventory import inventory

root = Path(__file__).resolve().parents[1]
for name in ('dyld', 'libSystem.B.dylib'):
    data = (root / 'research/samples-local/usr/lib' / name).read_bytes()
    report = inventory(data)
    dest = root / 'research/inventory' / ('runtime_' + name + '.json')
    dest.write_text(json.dumps(report, indent=2) + '\n')
    ppc = next(s['analysis'] for s in report['slices'] if s['cputype'] == 18)
    print(name, 'flags=' + hex(ppc['flags']), 'dependencies=' + json.dumps(ppc['dependencies']))
