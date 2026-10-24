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
known = ['usr/bin/true', 'usr/bin/false', 'bin/echo', 'bin/cat', 'usr/lib/dyld', 'bin/ls', 'bin/pwd',
         'usr/lib/libobjc.A.dylib', 'System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation']
parser.add_argument('items', nargs='*', default=known)
for item in parser.parse_args().items:
    if item not in known:
        raise ValueError('Unknown sample: ' + item)
    project, tag = ('text_cmds', 'text_cmds-18') if item == 'bin/cat' else (
        ('cctools', 'cctools-435') if item == 'usr/lib/dyld' else ('shell_cmds', 'shell_cmds-34'))
    if item == 'bin/ls': project, tag = 'file_cmds', 'file_cmds-60'
    if item == 'usr/lib/libobjc.A.dylib': project, tag = 'objc4', 'objc4-222'
    if item.endswith('/CoreFoundation'): project, tag = 'CF', None
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
            'evidence': 'ISO package version candidate ' + str(tag) + '; binary identity with source build not proven'
        }
    }
    if tag is None:
        result['source_correspondence'].update(status='unknown', evidence='ISO RPM CoreFoundation-262; exact CF-262 source tag not found in Apple CF repository')
    (dest / (item.replace('/', '_') + '.json')).write_text(json.dumps(result, indent=2) + '\n')
    print(item, result['analysis']['sha256'])
