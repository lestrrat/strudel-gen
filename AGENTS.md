# Strudel Composer

Workspace for composing [Strudel](https://strudel.cc/) code snippets. Strudel is a JavaScript live coding environment for algorithmic music — a browser-based port of Haskell's TidalCycles. Its core abstraction is **patterns**: values that cycle over time.

**Cardinal rule:** Never guess function names, sound names, or parameter signatures. Always look them up in the reference files below before writing code.

## Reference Data

All reference data lives in the `data/` directory as compact JSONL files (one JSON object per line), optimized for Grep lookups. Regenerate with `make data` (see `scripts/generate-data.py`).

### Function lookup — `data/functions.jsonl`

838 functions, one per line. Each line is a JSON object:

```
{"name":"<fn>","cat":"<Category>","desc":"...","synonyms":[...],"params":[...],"examples":[...]}
```

Fields: `name` (function name), `cat` (category: Pattern Operators, Pattern Transformations, Pattern Combinators, Tonal, Time/Tempo, Controls, Effects, Visualization, Output, Utility), `desc` (description), `synonyms` (aliases), `params` (parameters with name/type/description), `examples` (code examples). Not all fields are present on every function.

To find a function: `Grep for "name":"<functionName>" in data/functions.jsonl`
To browse a category: `Grep for "cat":"Effects" in data/functions.jsonl`

### Sound lookup — `data/sounds.jsonl`

All available sounds, organized by category. Each line is a JSON object. Categories: synths, synthSounds, noises, zzfx, soundfonts, drumMachines, drumMachineAliases, vcsl, piano, mridangam, uzuDrumkit, uzuWavetables, prebakeSamples.

Simple categories have structure:
```
{"cat":"synths","desc":"...","names":["triangle","square",...],"aliases":{"tri":"triangle",...}}
```

Drum machines are split into one line per machine (71 machines). Each machine line:
```
{"cat":"drumMachines","machine":"AkaiLinn","sounds":{"AkaiLinn_bd":1,"AkaiLinn_sd":2,...}}
```
The values in `sounds` are sample counts (e.g., `2` means samples `:0` and `:1` exist).

Categories with `sampleCounts` (vcsl, mridangam, uzuDrumkit, uzuWavetables, prebakeSamples) include them as `{"sampleCounts":{"name":count,...}}`.

To find a sound: `Grep for the sound name in data/sounds.jsonl`

### Mini-notation syntax — `data/mini-notation.jsonl`

14 tokens, one per line:
```
{"token":"[ ]","meaning":"Group / subdivision","desc":"...","example":"\"[bd sd] hh\""}
```

To check mini-notation: `Read data/mini-notation.jsonl` (small enough to read in full).

### Last Resort: Strudel Source Code

`/home/lestrrat/dev/src/codeberg.org/uzu/strudel/`

Only consult when the data files above don't answer the question. The source is a pnpm monorepo; each package lives under `packages/<name>/`. Key entry points: `packages/core/pattern.mjs` (pattern engine), `packages/core/controls.mjs` (control parameters), `packages/mini/` (mini-notation parser), `packages/superdough/` (synth/sampler engine), `packages/tonal/` (scales/chords).

## Workflow: Writing a Strudel Snippet

Follow these steps in order when asked to write Strudel code.

**Step 1 — Identify requirements.** Determine what the user wants: sounds, rhythm, melody, effects, tempo, structure. Note any ambiguous musical terms (see Semantic Mapping below).

**Step 2 — Look up sounds.** If the snippet needs specific sounds, Grep for the sound name in `data/sounds.jsonl`. Confirm every sound name exists before using it.

**Step 3 — Look up functions.** For each function you plan to use, Grep for `"name":"<fn>"` in `data/functions.jsonl`. Check desc, params, and examples. Pay attention to synonyms — many functions have shorthand names.

**Step 4 — Check mini-notation.** If using mini-notation strings, read `data/mini-notation.jsonl` to verify syntax.

**Step 5 — Compose the snippet.** Write the code using only verified function names, sound names, and syntax.

**Step 6 — Verify.** Before presenting the snippet:
- Every function name appears in `data/functions.jsonl`.
- Every sound name appears in `data/sounds.jsonl`.
- Mini-notation syntax follows documented rules.
- Method chaining is consistent with documented return types (pattern methods return patterns).

## Semantic Mapping: Musical Concepts to Documentation

When users describe what they want in musical terms rather than function names, use this mapping to determine where to look.

| User says | Grep `data/functions.jsonl` for | Key functions |
|-----------|-------------------------------|---------------|
| "darker" / "brighter" / "filter" | `"cat":"Effects"` | lpf, hpf, bpf, cutoff, resonance |
| "echo" / "space" / "ambient" | `"cat":"Effects"` | delay, room, size, orbit |
| "distorted" / "heavy" / "gritty" | `"cat":"Effects"` | distort, shape, crush |
| "faster" / "slower" / "double time" | `"cat":"Pattern Transformations"` | fast, slow, hurry |
| "swing" / "shuffle" / "groove" | `"cat":"Pattern Transformations"` | swing, brak |
| "random" / "evolving" / "generative" | `"cat":"Pattern Transformations"` | degrade, sometimes, rand, irand, choose |
| "build up" / "every N bars" | `"cat":"Pattern Transformations"` | every, when, iter |
| "chord" / "harmony" / "scale" | `"cat":"Tonal"` | chord, voicing, scale, note |
| "layer" / "combine" / "together" | `"cat":"Pattern Combinators"` | stack, layer, superimpose |
| "sequence" / "one after another" | `"cat":"Pattern Combinators"` | cat, seq, fastcat |
| "tempo" / "BPM" | `"cat":"Time/Tempo"` | setcps, setcpm (cpm = cycles per minute, not BPM; for 4/4 time, BPM = cpm * 4) |
| "pan left/right" / "stereo" | `"cat":"Controls"` | pan |
| "volume" / "louder" / "quieter" | `"cat":"Controls"` | gain, amp |
| "pitch" / "note" / "melody" | `"cat":"Controls"` or `"cat":"Tonal"` | note, n, freq, scale |
| "MIDI" / "external synth" | `"cat":"Output"` | midi, midichan, ccn, ccv |

## Pitfalls

- `note()` sets pitch (MIDI note number or note name). `n()` selects a sample index within a sound bank. Do not confuse them.
- `s()` and `sound()` are aliases — both select the sound/instrument. Use either consistently.
- `$:` is the syntax for named patterns in multi-pattern setups (e.g., `$: s("bd sd")\n$: s("hh*8")`). Each `$:` line is an independent pattern that plays simultaneously.
- Tempo is in cycles per minute (cpm), not BPM. In 4/4 time, `setcpm(BPM / 4)` or equivalently `setcps(BPM / 4 / 60)`.
- Mini-notation `*` (repeat) and `/` (slow) apply to the element they follow, not the whole pattern.
- Euclidean rhythm mini-notation `(k,n)` goes after the sound name: `"bd(3,8)"`, not `"(3,8) bd"`.
