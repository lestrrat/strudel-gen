#!/usr/bin/env python3
"""Generate snippets.jsonl from .strudel and .str files in snippets/.

Each file should have a header comment block with metadata:

    // @name: trance-buildup
    // @desc: 140 BPM trance buildup with filtered supersaw
    // @tags: trance, buildup, supersaw

Supported fields:
    @name   - Required. Identifier for grepping (kebab-case recommended)
    @desc   - Required. Short description of what the snippet does
    @tags   - Optional. Comma-separated tags (stored as JSON array)

Unlike idioms.jsonl, snippets.jsonl is just an index — it does NOT include
the code content. Users can read the actual snippet files when needed.

Usage:
    python3 scripts/generate-snippets.py

Output:
    data/snippets.jsonl - One JSON object per file, optimized for Grep lookups
"""

import json
import os
import re
import sys


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_snippet_file(path):
    """Parse a .strudel or .str file and extract metadata.

    Returns a dict with name, file, desc, and tags (optional).
    Returns None if the file is missing required fields.
    """
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract metadata from // @key: value lines at the start
    metadata = {}
    lines = content.split('\n')

    for line in lines:
        stripped = line.strip()

        # Skip empty lines at the start
        if not stripped and not metadata:
            continue

        # Parse // @key: value
        match = re.match(r'^//\s*@(\w+):\s*(.+)$', stripped)
        if match:
            key = match.group(1).lower()
            value = match.group(2).strip()
            metadata[key] = value
        elif stripped.startswith('//') and not metadata:
            # Regular comment before any metadata — skip
            continue
        elif stripped.startswith('//') and metadata:
            # Comment after metadata started but before code — end of metadata
            break
        else:
            # Non-comment line — code starts here
            break

    # Validate required fields
    required = ['name', 'desc']
    missing = [f for f in required if f not in metadata]
    if missing:
        filename = os.path.basename(path)
        print(f'  WARN: {filename} missing required fields: {", ".join(missing)}', file=sys.stderr)
        return None

    # Parse tags into a list if present
    tags = None
    if 'tags' in metadata:
        tags = [t.strip() for t in metadata['tags'].split(',') if t.strip()]

    return {
        'name': metadata['name'],
        'file': os.path.basename(path),
        'desc': metadata['desc'],
        'tags': tags,
    }


def generate_snippets(src_dir, out_dir):
    """Generate snippets.jsonl from .strudel and .str files in src_dir."""

    if not os.path.isdir(src_dir):
        print(f'Creating {src_dir}/')
        os.makedirs(src_dir, exist_ok=True)
        return 0

    # Find all .strudel and .str files
    files = sorted([f for f in os.listdir(src_dir) if f.endswith('.strudel') or f.endswith('.str')])

    if not files:
        print(f'No .strudel or .str files found in {src_dir}/')
        return 0

    count = 0
    out_path = os.path.join(out_dir, 'snippets.jsonl')

    with open(out_path, 'w', encoding='utf-8') as out:
        for filename in files:
            path = os.path.join(src_dir, filename)
            record = parse_snippet_file(path)

            if record is None:
                continue

            # Build compact JSON record
            rec = {
                'name': record['name'],
                'file': record['file'],
                'desc': record['desc'],
            }
            if record.get('tags'):
                rec['tags'] = record['tags']

            out.write(json.dumps(rec, separators=(',', ':'), ensure_ascii=False) + '\n')
            count += 1

    return count


def main():
    root = repo_root()
    src_dir = os.path.join(root, 'snippets')
    out_dir = os.path.join(root, 'data')

    print(f'Source: {src_dir}/')
    print(f'Output: {out_dir}/snippets.jsonl')
    print()

    count = generate_snippets(src_dir, out_dir)

    if count > 0:
        out_path = os.path.join(out_dir, 'snippets.jsonl')
        size = os.path.getsize(out_path)
        print(f'snippets.jsonl: {count} snippets, {size:,} bytes')
    else:
        print('No snippets generated.')


if __name__ == '__main__':
    main()
