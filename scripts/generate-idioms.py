#!/usr/bin/env python3
"""Generate idioms.jsonl from .strudel files in data/idioms/.

Each .strudel file should have a header comment block with metadata:

    // @name: beat-switcher
    // @cat: live-performance
    // @desc: Array of beat variations for live switching
    // @notes: Change `beat` index live to switch patterns.

    const beat = 0
    ...

Supported fields:
    @name      - Required. Identifier for grepping (kebab-case recommended)
    @cat       - Required. Category (e.g., live-performance, rhythm, arrangement)
    @desc      - Required. Short description of what the idiom does
    @notes     - Optional. Usage tips, gotchas, or explanation
    @tags      - Optional. Comma-separated keywords for concept-based lookup
    @functions - Optional. Comma-separated key Strudel functions demonstrated

The code (everything after the header block) is captured verbatim.

Usage:
    python3 scripts/generate-idioms.py

Output:
    data/idioms.jsonl - One JSON object per file, optimized for Grep lookups
"""

import json
import os
import re
import sys


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_strudel_file(path):
    """Parse a .strudel file and extract metadata + code.

    Returns a dict with name, cat, desc, notes (optional), and code.
    Returns None if the file is missing required fields.
    """
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract metadata from // @key: value lines at the start
    metadata = {}
    lines = content.split('\n')
    code_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip empty lines at the start
        if not stripped and not metadata:
            code_start = i + 1
            continue

        # Parse // @key: value
        match = re.match(r'^//\s*@(\w+):\s*(.+)$', stripped)
        if match:
            key = match.group(1).lower()
            value = match.group(2).strip()
            metadata[key] = value
            code_start = i + 1
        elif stripped.startswith('//') and not metadata:
            # Regular comment before any metadata — skip
            code_start = i + 1
        elif stripped.startswith('//') and metadata:
            # Comment after metadata started but before code — could be continuation
            # For now, treat as end of metadata
            break
        else:
            # Non-comment line — code starts here
            break

    # Validate required fields
    required = ['name', 'cat', 'desc']
    missing = [f for f in required if f not in metadata]
    if missing:
        filename = os.path.basename(path)
        print(f'  WARN: {filename} missing required fields: {", ".join(missing)}', file=sys.stderr)
        return None

    # Extract code (everything from code_start onwards, trimmed)
    code_lines = lines[code_start:]

    # Trim leading/trailing empty lines from code
    while code_lines and not code_lines[0].strip():
        code_lines.pop(0)
    while code_lines and not code_lines[-1].strip():
        code_lines.pop()

    code = '\n'.join(code_lines)

    if not code:
        filename = os.path.basename(path)
        print(f'  WARN: {filename} has no code', file=sys.stderr)
        return None

    return {
        'name': metadata['name'],
        'cat': metadata['cat'],
        'desc': metadata['desc'],
        'notes': metadata.get('notes'),
        'tags': metadata.get('tags'),
        'functions': metadata.get('functions'),
        'code': code,
    }


def generate_idioms(src_dir, out_dir):
    """Generate idioms.jsonl from .strudel files in src_dir."""

    if not os.path.isdir(src_dir):
        print(f'Creating {src_dir}/')
        os.makedirs(src_dir, exist_ok=True)
        return 0

    # Find all .strudel files
    files = sorted([f for f in os.listdir(src_dir) if f.endswith('.strudel')])

    if not files:
        print(f'No .strudel files found in {src_dir}/')
        return 0

    count = 0
    out_path = os.path.join(out_dir, 'idioms.jsonl')

    with open(out_path, 'w', encoding='utf-8') as out:
        for filename in files:
            path = os.path.join(src_dir, filename)
            record = parse_strudel_file(path)

            if record is None:
                continue

            # Build compact JSON record
            rec = {
                'name': record['name'],
                'cat': record['cat'],
                'desc': record['desc'],
            }
            if record.get('notes'):
                rec['notes'] = record['notes']
            if record.get('tags'):
                rec['tags'] = [t.strip() for t in record['tags'].split(',')]
            if record.get('functions'):
                rec['functions'] = [f.strip() for f in record['functions'].split(',')]
            rec['code'] = record['code']

            out.write(json.dumps(rec, separators=(',', ':'), ensure_ascii=False) + '\n')
            count += 1

    return count


def main():
    root = repo_root()
    src_dir = os.path.join(root, 'data', 'idioms')
    out_dir = os.path.join(root, 'data')

    print(f'Source: {src_dir}/')
    print(f'Output: {out_dir}/idioms.jsonl')
    print()

    count = generate_idioms(src_dir, out_dir)

    if count > 0:
        out_path = os.path.join(out_dir, 'idioms.jsonl')
        size = os.path.getsize(out_path)
        print(f'idioms.jsonl: {count} idioms, {size:,} bytes')
    else:
        print('No idioms generated.')


if __name__ == '__main__':
    main()
