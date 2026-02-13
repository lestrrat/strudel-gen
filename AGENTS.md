# Strudel Composer

Workspace for composing [Strudel](https://strudel.cc/) code snippets. Strudel is a JavaScript live coding environment for algorithmic music — a browser-based port of Haskell's TidalCycles. Its core abstraction is **patterns**: values that cycle over time.

**Cardinal rule:** Never guess function names, sound names, or parameter signatures. Always look them up in the reference files below before writing code.

**Data-first rule:** When answering ANY question about Strudel — whether writing code, explaining behavior, or debugging errors — you MUST search the `data/` directory files FIRST. Do NOT jump to the Strudel source code or rely on your own knowledge. The `data/` files are the authoritative reference. Only consult the Strudel source tree as an absolute last resort, after confirming the data files don't contain the answer.

## Composing Strudel Code

When the user asks you to write or compose Strudel code (snippets, songs, beats, etc.), invoke the `/strudel-compose` skill. It contains the full composition workflow including lookup steps, code style guidelines, and verification checklists.

## Reference Data

All reference data lives in `data/` as JSONL files (one JSON object per line), optimized for Grep lookups. Regenerate all with `make data`.

| File | What | How to search |
|------|------|---------------|
| `functions.jsonl` | 838 functions with category, desc, params, examples | `Grep "name":"<fn>"` or `"cat":"Effects"` |
| `functions-index.jsonl` | Function names grouped by category (lightweight) | `Read` whole file |
| `sounds.jsonl` | All sounds by category (synths, drum machines, etc.) | `Grep` for sound name |
| `mini-notation.jsonl` | 14 syntax tokens with rewrites | `Read` whole file |
| `anti-patterns.jsonl` | Common mistakes and corrections | `Read` whole file |
| `idioms.jsonl` | Reusable code patterns by category/tags | `Grep` for tag or category |
| `snippets.jsonl` | Index of working examples in `snippets/` | `Grep` for concept keyword |
| `semantic-map.jsonl` | Musical concepts → functions, idioms, sounds | `Grep` for user keywords |

**Strudel source (last resort):** Check `STRUDEL_SRC` env var for the source tree path. Monorepo: `packages/core/`, `packages/mini/`, `packages/superdough/`, `packages/tonal/`.

## Data Maintenance

Source files and rebuild commands for each data file:

| Data file | Source | Rebuild |
|-----------|--------|---------|
| `anti-patterns.jsonl` | `data/anti-patterns/*.yaml` (fields: `bad`, `why`, `good`) | `make anti-patterns` |
| `idioms.jsonl` | `data/idioms/*.strudel` (header: `@name`, `@cat`, `@desc`, `@tags`, `@functions`, `@notes`) | `make idioms` |
| `snippets.jsonl` | `snippets/*.strudel` or `*.str` (header: `@name`, `@desc`, `@tags`) | `make snippets` |
| `functions-index.jsonl` | Generated from `functions.jsonl` | `make functions-index` |
| `mini-notation.jsonl` rewrites | `data/mini-notation-rewrites.json` | `make rewrites` |
| Everything | — | `make data` |

## Pitfalls

- `note()` sets pitch (MIDI note number or note name). `n()` selects a sample index within a sound bank. Do not confuse them.
- `s()` and `sound()` are aliases — both select the sound/instrument. Use either consistently.
- `$NAME: pattern` is the syntax for named reactive statements (e.g., `$KICK: s("bd*4")\n$HATS: s("hh*8")`). Each named statement is an independent pattern that plays simultaneously and can be individually modified during a live set.
- For optional/toggle layers that the user can comment out to change the feel, use the `_$NAME:` prefix (underscore before the dollar sign), e.g., `_$RIM: s("rim*4")`. The underscore signals that the layer is meant to be toggled on/off. Core layers that define the basic groove use the plain `$NAME:` prefix.
- Place toggle layers near the core layers they relate to or might replace, so the user can see and edit both at the same time. For example, put a half-time kick toggle right after the main kick, or a pad toggle near the lead/bass section.
- `gain()` values should be audible. Use ~1 as the baseline for most sounds. Quiet textures like noise or crackle need much higher values (e.g., 4) because they are inherently faint. Only use low gain values (below 0.5) for deliberate ghost-note dynamics or when distortion/crush effects are already boosting the signal. Values like 0.04–0.2 are almost always inaudible and should be avoided.
- Tempo is in cycles per minute (cpm), not BPM. In 4/4 time, `setcpm(BPM / 4)` or equivalently `setcps(BPM / 4 / 60)`.
- Mini-notation `*` (repeat) and `/` (slow) apply to the element they follow, not the whole pattern.
- Euclidean rhythm mini-notation `(k,n)` goes after the sound name: `"bd(3,8)"`, not `"(3,8) bd"`.

## Authoring Skill Files (.claude/skills/*/SKILL.md)

Skill file contents are expanded and processed through the shell at invocation time. **Avoid shell-sensitive characters in prose text** — they can trigger bash permission check failures and break skill invocation.

Known problematic patterns:
- Backtick-wrapped exclamation marks (e.g., `` `!` ``) — the `!` is interpreted as bash history expansion inside backticks.
- Bare backticks adjacent to shell metacharacters (`$`, `!`, `\`) — these can be misread as command substitution or variable expansion.

**Fix:** Spell out the operator name in words (e.g., "replicate operator" instead of wrapping the `!` symbol in backticks), or restructure the sentence to avoid the problematic combination. Code blocks (triple-backtick fenced blocks) are generally safe.
