#!/usr/bin/env python3
"""Record provenance and architecture of samples extracted from the Apple ISO.
SPDX-License-Identifier: MIT
"""
import json
from pathlib import Path
from macho_inventory import inventory

root = Path(__file__).resolve().parents[1]
dest = root / 'research/inventory'
dest.mkdir(parents=True, exist_ok=True)
for item in ('usr/bin/true', 'usr/bin/false', 'bin/echo', 'usr/lib/dyld'):
    data = (root / 'research/samples-local' / item).read_bytes()
    result = {
        'original_path': '/' + item,
        'distribution': 'Apple Darwin x86 6.0.2 ISO; not yet compared with Jaguar retail',
        'iso_sha256': 'd2c4668dcd4ca4a7498acffaf703a19862f53ab9b58b06c51745bd33e58a584f',
        'analysis': inventory(data),
        'source_correspondence': {
            'status': 'candidate',
            'project': 'shell_cmds' if item != 'usr/lib/dyld' else 'cctools',
            'tag': 'shell_cmds-34' if item != 'usr/lib/dyld' else 'cctools-435',
            'evidence': 'ISO contains shell_cmds-34-1.ppc.rpm and cctools-435-1.ppc.rpm; binary identity with source build not proven'
        }
    }
    (dest / (item.replace('/', '_') + '.json')).write_text(json.dumps(result, indent=2) + '\n')
    print(item, result['analysis']['sha256'])
