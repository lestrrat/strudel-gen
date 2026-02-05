#!/usr/bin/env python3
"""Generate anti-patterns.jsonl from YAML files in data/anti-patterns/.

Each .yaml file should have the following structure:

    bad: |
      [5 ~ ~ ~ ~ ~ ~ ~]
    why: Verbose repetition of rests
    good: |
      [5 ~!7]

The id is derived from the filename (minus .yaml extension).

Supported fields:
    bad   - Required. The anti-pattern code or description
    why   - Required. Explanation of why it's wrong
    good  - Required. The correct approach

Usage:
    python3 scripts/generate-anti-patterns.py

Output:
    data/anti-patterns.jsonl - One JSON object per file, optimized for Grep lookups
"""

import json
import os
import sys

import yaml


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_yaml_file(path):
    """Parse a .yaml file and extract anti-pattern fields.

    Returns a dict with id, bad, why, good.
    Returns None if the file is missing required fields.
    """
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            filename = os.path.basename(path)
            print(f'  WARN: {filename} has invalid YAML: {e}', file=sys.stderr)
            return None

    if not isinstance(data, dict):
        filename = os.path.basename(path)
        print(f'  WARN: {filename} is not a YAML mapping', file=sys.stderr)
        return None

    # Validate required fields
    required = ['bad', 'why', 'good']
    missing = [f for f in required if f not in data or not data[f]]
    if missing:
        filename = os.path.basename(path)
        print(f'  WARN: {filename} missing required fields: {", ".join(missing)}', file=sys.stderr)
        return None

    # Derive id from filename
    filename = os.path.basename(path)
    id_ = filename.rsplit('.', 1)[0]

    # Strip trailing whitespace from block scalars
    bad = data['bad'].rstrip() if isinstance(data['bad'], str) else str(data['bad'])
    why = data['why'].rstrip() if isinstance(data['why'], str) else str(data['why'])
    good = data['good'].rstrip() if isinstance(data['good'], str) else str(data['good'])

    return {
        'id': id_,
        'bad': bad,
        'why': why,
        'good': good,
    }


def generate_anti_patterns(src_dir, out_dir):
    """Generate anti-patterns.jsonl from .yaml files in src_dir."""

    if not os.path.isdir(src_dir):
        print(f'Creating {src_dir}/')
        os.makedirs(src_dir, exist_ok=True)
        return 0

    # Find all .yaml files
    files = sorted([f for f in os.listdir(src_dir) if f.endswith('.yaml')])

    if not files:
        print(f'No .yaml files found in {src_dir}/')
        return 0

    count = 0
    out_path = os.path.join(out_dir, 'anti-patterns.jsonl')

    with open(out_path, 'w', encoding='utf-8') as out:
        for filename in files:
            path = os.path.join(src_dir, filename)
            record = parse_yaml_file(path)

            if record is None:
                continue

            out.write(json.dumps(record, separators=(',', ':'), ensure_ascii=False) + '\n')
            count += 1

    return count


def main():
    root = repo_root()
    src_dir = os.path.join(root, 'data', 'anti-patterns')
    out_dir = os.path.join(root, 'data')

    print(f'Source: {src_dir}/')
    print(f'Output: {out_dir}/anti-patterns.jsonl')
    print()

    count = generate_anti_patterns(src_dir, out_dir)

    if count > 0:
        out_path = os.path.join(out_dir, 'anti-patterns.jsonl')
        size = os.path.getsize(out_path)
        print(f'anti-patterns.jsonl: {count} anti-patterns, {size:,} bytes')
    else:
        print('No anti-patterns generated.')


if __name__ == '__main__':
    main()
