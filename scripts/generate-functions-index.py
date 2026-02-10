#!/usr/bin/env python3
"""Generate functions-index.jsonl — a lightweight category index of function names.

Reads data/functions.jsonl and produces a compact index with one line per category,
containing only the category name and sorted function names (no descriptions, params,
or examples).

Output format (one JSON object per line):
    {"cat":"Effects","names":["bpf","delay","hpf","lpf","room",...]}

Usage:
    python3 scripts/generate-functions-index.py

Output:
    data/functions-index.jsonl
"""

import json
import os


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_functions_index(data_dir):
    """Read functions.jsonl and produce functions-index.jsonl grouped by category."""

    src_path = os.path.join(data_dir, 'functions.jsonl')
    out_path = os.path.join(data_dir, 'functions-index.jsonl')

    # Group function names by category
    categories = {}
    total_functions = 0

    with open(src_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            name = rec.get('name')
            cat = rec.get('cat')
            if not name or not cat:
                continue
            categories.setdefault(cat, []).append(name)
            total_functions += 1

    # Write one line per category, sorted alphabetically by category name
    cat_count = 0
    with open(out_path, 'w', encoding='utf-8') as out:
        for cat in sorted(categories.keys()):
            names = sorted(categories[cat])
            rec = {'cat': cat, 'names': names}
            out.write(json.dumps(rec, separators=(',', ':'), ensure_ascii=False) + '\n')
            cat_count += 1

    return cat_count, total_functions


def main():
    root = repo_root()
    data_dir = os.path.join(root, 'data')

    print(f'Source: {data_dir}/functions.jsonl')
    print(f'Output: {data_dir}/functions-index.jsonl')
    print()

    cat_count, total_functions = generate_functions_index(data_dir)

    out_path = os.path.join(data_dir, 'functions-index.jsonl')
    size = os.path.getsize(out_path)
    print(f'functions-index.jsonl: {cat_count} categories, {total_functions} functions, {size:,} bytes')


if __name__ == '__main__':
    main()
