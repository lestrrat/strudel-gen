#!/usr/bin/env python3
"""Generate compressed Strudel reference data for coding-agent consumption.

Reads the full documentation from strudel-docs output/ directories and produces
compact JSONL/text files optimized for Grep lookups and minimal context usage.

Usage:
    python3 scripts/generate-data.py [STRUDEL_DOCS_DIR]

If STRUDEL_DOCS_DIR is not given, defaults to ../strudel-docs relative to the
repository root.

NOTE: STRUDEL_DOCS_DIR refers to lestrrat's custom documentation extraction
project (https://github.com/lestrrat/strudel-docs), NOT the documentation that
ships with the upstream Strudel source code. The strudel-docs project parses
the Strudel source to produce structured JSON/Markdown reference files that
this script then compresses into agent-optimized JSONL.
"""

import json
import os
import sys


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def default_strudel_docs():
    return os.path.join(repo_root(), '..', 'strudel-docs')


# ---------------------------------------------------------------------------
# functions.jsonl
# ---------------------------------------------------------------------------

def generate_functions(src_dir, out_dir):
    """One JSON object per line.  Fields: name, cat, desc, examples, params, synonyms."""
    path = os.path.join(src_dir, 'api', 'output', 'functions.json')
    with open(path) as f:
        data = json.load(f)

    count = 0
    with open(os.path.join(out_dir, 'functions.jsonl'), 'w') as out:
        for cat, fns in data['categories'].items():
            for fn in fns:
                rec = {'name': fn['name'], 'cat': cat}
                if fn.get('description'):
                    rec['desc'] = fn['description']
                if fn.get('synonyms'):
                    rec['synonyms'] = fn['synonyms']
                if fn.get('parameters'):
                    rec['params'] = fn['parameters']
                if fn.get('examples'):
                    rec['examples'] = fn['examples']
                out.write(json.dumps(rec, separators=(',', ':'), ensure_ascii=False) + '\n')
                count += 1

    return count


# ---------------------------------------------------------------------------
# sounds.jsonl
# ---------------------------------------------------------------------------

def generate_sounds(src_dir, out_dir):
    """One JSON object per line, per category (large categories split by group).

    Small categories → one line.
    drumMachines → one line per machine prefix (keeps lines <2 KB each).
    """
    path = os.path.join(src_dir, 'soundbank', 'output', 'sounds.json')
    with open(path) as f:
        data = json.load(f)

    lines = 0
    with open(os.path.join(out_dir, 'sounds.jsonl'), 'w') as out:
        for cat, info in data['categories'].items():
            if cat == 'drumMachines':
                lines += _write_drum_machines(out, info)
            elif cat == 'drumMachineAliases':
                lines += _write_drum_aliases(out, info)
            else:
                lines += _write_sound_category(out, cat, info)

    return lines


def _write_sound_category(out, cat, info):
    rec = {'cat': cat, 'desc': info.get('description', '')}
    if info.get('names'):
        rec['names'] = info['names']
    if info.get('aliases'):
        rec['aliases'] = info['aliases']
    if info.get('sampleCounts'):
        rec['sampleCounts'] = info['sampleCounts']
    if info.get('noteCount'):
        rec['noteCount'] = info['noteCount']
    out.write(json.dumps(rec, separators=(',', ':'), ensure_ascii=False) + '\n')
    return 1


def _write_drum_machines(out, info):
    """Split drum machines: one line per machine prefix."""
    machines = info.get('machines', [])
    sample_counts = info.get('sampleCounts', {})
    names = info.get('names', [])

    # Build mapping: machine -> list of (sound_name, sample_count)
    machine_sounds = {}
    for name in names:
        # Names are Machine_suffix
        parts = name.split('_', 1)
        machine = parts[0]
        if machine not in machine_sounds:
            machine_sounds[machine] = {}
        machine_sounds[machine][name] = sample_counts.get(name, 1)

    # Write header line with metadata
    out.write(json.dumps({
        'cat': 'drumMachines',
        'desc': info.get('description', ''),
        'machines': machines,
        'suffixes': info.get('suffixes', []),
    }, separators=(',', ':'), ensure_ascii=False) + '\n')

    lines = 1
    for machine in machines:
        sounds = machine_sounds.get(machine, {})
        if sounds:
            rec = {
                'cat': 'drumMachines',
                'machine': machine,
                'sounds': sounds,
            }
            out.write(json.dumps(rec, separators=(',', ':'), ensure_ascii=False) + '\n')
            lines += 1

    return lines


def _write_drum_aliases(out, info):
    rec = {
        'cat': 'drumMachineAliases',
        'desc': info.get('description', ''),
    }
    if info.get('aliasMap'):
        rec['aliasMap'] = info['aliasMap']
    if info.get('generatedNames'):
        rec['generatedNames'] = info['generatedNames']
    out.write(json.dumps(rec, separators=(',', ':'), ensure_ascii=False) + '\n')
    return 1


# ---------------------------------------------------------------------------
# mini-notation.jsonl
# ---------------------------------------------------------------------------

def generate_mini_notation(src_dir, out_dir):
    """One JSON object per mini-notation token."""
    path = os.path.join(src_dir, 'patterns', 'output', 'patterns.json')
    with open(path) as f:
        data = json.load(f)

    mini = data.get('miniNotation', {})
    tokens = mini.get('tokens', [])

    count = 0
    with open(os.path.join(out_dir, 'mini-notation.jsonl'), 'w') as out:
        for token in tokens:
            rec = {
                'token': token['token'],
                'meaning': token['meaning'],
                'desc': token.get('description', ''),
            }
            if token.get('example'):
                rec['example'] = token['example']
            out.write(json.dumps(rec, separators=(',', ':'), ensure_ascii=False) + '\n')
            count += 1

    return count


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    src_dir = sys.argv[1] if len(sys.argv) > 1 else default_strudel_docs()
    src_dir = os.path.abspath(src_dir)
    out_dir = os.path.join(repo_root(), 'data')

    os.makedirs(out_dir, exist_ok=True)

    # Validate source exists
    for sub in ['api/output/functions.json',
                'soundbank/output/sounds.json',
                'patterns/output/patterns.json']:
        p = os.path.join(src_dir, sub)
        if not os.path.isfile(p):
            print(f'ERROR: missing {p}', file=sys.stderr)
            sys.exit(1)

    print(f'Source: {src_dir}')
    print(f'Output: {out_dir}')
    print()

    fn_count = generate_functions(src_dir, out_dir)
    print(f'functions.jsonl: {fn_count} functions')

    snd_lines = generate_sounds(src_dir, out_dir)
    print(f'sounds.jsonl:    {snd_lines} lines')

    mini_count = generate_mini_notation(src_dir, out_dir)
    print(f'mini-notation.jsonl: {mini_count} tokens')

    # Report sizes
    print()
    total = 0
    for name in ['functions.jsonl', 'sounds.jsonl', 'mini-notation.jsonl']:
        p = os.path.join(out_dir, name)
        size = os.path.getsize(p)
        total += size
        print(f'  {name}: {size:,} bytes')
    print(f'  total: {total:,} bytes')


if __name__ == '__main__':
    main()
