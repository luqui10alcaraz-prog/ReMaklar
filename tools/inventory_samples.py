#!/usr/bin/env python3
"""Record provenance and architecture of samples extracted from the Apple ISO.
SPDX-License-Identifier: MIT
"""
import json
import argparse
from pathlib import Path
from macho_inventory import inventory

root = Path(__file__).resolve().parents[1]
dest = root / 'research/inventory'
dest.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser()
parser.add_argument('items', nargs='*', default=['usr/bin/true', 'usr/bin/false', 'bin/echo', 'bin/cat', 'usr/lib/dyld'])
for item in parser.parse_args().items:
    if item not in ('usr/bin/true', 'usr/bin/false', 'bin/echo', 'bin/cat', 'usr/lib/dyld'):
        raise ValueError('Unknown sample: ' + item)
    project, tag = ('text_cmds', 'text_cmds-18') if item == 'bin/cat' else (
        ('cctools', 'cctools-435') if item == 'usr/lib/dyld' else ('shell_cmds', 'shell_cmds-34'))
    data = (root / 'research/samples-local' / item).read_bytes()
    result = {
        'original_path': '/' + item,
        'distribution': 'Apple Darwin x86 6.0.2 ISO; not yet compared with Jaguar retail',
        'iso_sha256': 'd2c4668dcd4ca4a7498acffaf703a19862f53ab9b58b06c51745bd33e58a584f',
        'analysis': inventory(data),
        'source_correspondence': {
            'status': 'candidate',
            'project': project,
            'tag': tag,
            'evidence': 'ISO contains ' + tag + '-1.ppc.rpm; binary identity with source build not proven'
        }
    }
    (dest / (item.replace('/', '_') + '.json')).write_text(json.dumps(result, indent=2) + '\n')
    print(item, result['analysis']['sha256'])
