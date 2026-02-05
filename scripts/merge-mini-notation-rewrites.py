#!/usr/bin/env python3
"""Merge rewrites from mini-notation-rewrites.json into existing mini-notation.jsonl.

This script is useful when strudel-docs is not available. It reads the existing
mini-notation.jsonl, merges in the rewrites from mini-notation-rewrites.json,
and writes back the updated file.

Usage:
    python3 scripts/merge-mini-notation-rewrites.py
"""

import json
import os
import sys


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    root = repo_root()
    data_dir = os.path.join(root, 'data')

    mini_path = os.path.join(data_dir, 'mini-notation.jsonl')
    rewrites_path = os.path.join(data_dir, 'mini-notation-rewrites.json')

    if not os.path.isfile(mini_path):
        print(f'ERROR: {mini_path} not found', file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(rewrites_path):
        print(f'ERROR: {rewrites_path} not found', file=sys.stderr)
        sys.exit(1)

    # Load rewrites
    with open(rewrites_path) as f:
        rewrites_data = json.load(f)
    rewrites = rewrites_data.get('rewrites', {})

    if not rewrites:
        print('No rewrites found in overlay file')
        return

    # Read existing mini-notation.jsonl
    records = []
    with open(mini_path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    # Merge rewrites
    merged_count = 0
    for rec in records:
        token = rec.get('token', '')
        if token in rewrites:
            rec['rewrites'] = rewrites[token]
            merged_count += 1

    # Write back
    with open(mini_path, 'w') as out:
        for rec in records:
            out.write(json.dumps(rec, separators=(',', ':'), ensure_ascii=False) + '\n')

    print(f'Merged {merged_count} rewrite entries into {mini_path}')


if __name__ == '__main__':
    main()
